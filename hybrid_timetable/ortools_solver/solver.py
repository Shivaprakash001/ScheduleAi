from ortools.sat.python import cp_model
from collections import defaultdict

from ..utils.helpers import absolute_slot, build_weekly_block_indices

def solve_with_ortools_intervals(sessions, rooms, days, slots_per_day,
                                 max_time=30, max_consec_slots=3,
                                 max_classes_per_day=6, max_weekly_hours_per_faculty=20,
                                 max_daily_hours_per_faculty=5,
                                 room_preference=None,
                                 enforce_rooms=False,
                                 project_block_positions=None,
                                 is_project_func=None,
                                 min_group_days=3):
    """
    CP-SAT model using interval variables and NoOverlap for resources.
    Added: min_group_days (hard) — each group must occupy at least that many distinct days.
    """
    total_slots = len(days) * slots_per_day
    model = cp_model.CpModel()

    # Precompute possible starts per session to limit domains
    possible_starts = {}
    for s in sessions:
        L = s['length']
        starts = []
        for d in range(len(days)):
            for p in range(slots_per_day - L + 1):
                starts.append(d * slots_per_day + p)
        possible_starts[s['sess_id']] = starts

    # Create vars and intervals
    sess_vars = {}
    intervals_for_room = defaultdict(list)
    intervals_for_faculty = defaultdict(list)
    intervals_for_group = defaultdict(list)

    for s in sessions:
        sid = s['sess_id']
        starts = possible_starts[sid]
        start_var = model.NewIntVarFromDomain(cp_model.Domain.FromValues(starts), f"start_{sid}")
        end_var = model.NewIntVar(min(starts) + s['length'], max(starts) + s['length'], f"end_{sid}")
        interval = model.NewIntervalVar(start_var, s['length'], end_var, f"int_{sid}")
        sess_vars[sid] = {"start": start_var, "end": end_var, "interval": interval, "meta": s}

        intervals_for_faculty[s['faculty']].append(interval)
        intervals_for_group[s['group']].append(interval)

        if enforce_rooms:
            room_dom = list(range(len(rooms)))
            if room_preference and sid in room_preference:
                room_dom = room_preference[sid]
            room_var = model.NewIntVar(min(room_dom), max(room_dom), f"room_{sid}")
            if room_dom != list(range(min(room_dom), max(room_dom)+1)):
                model.AddAllowedAssignments([room_var], [[r] for r in room_dom])
            sess_vars[sid]["room"] = room_var
            for r in room_dom:
                opt_var = model.NewBoolVar(f"assign_{sid}_room{r}")
                opt_interval = model.NewOptionalIntervalVar(start_var, s['length'], end_var, opt_var, f"optint_{sid}_r{r}")
                intervals_for_room[r].append(opt_interval)
                model.Add(room_var == r).OnlyEnforceIf(opt_var)
                model.Add(room_var != r).OnlyEnforceIf(opt_var.Not())

    # No-overlap per faculty/group
    for faculty, ints in intervals_for_faculty.items():
        if len(ints) > 1:
            model.AddNoOverlap(ints)
    for group, ints in intervals_for_group.items():
        if len(ints) > 1:
            model.AddNoOverlap(ints)

    # Rooms non-overlap (if enforced)
    if enforce_rooms:
        for r, ints in intervals_for_room.items():
            if len(ints) > 1:
                model.AddNoOverlap(ints)

    # ---------- HARD NEP CONSTRAINTS ----------

    # Faculty weekly load (sum of lengths)
    for f in intervals_for_faculty:
        weekly_load = []
        for sid, var in sess_vars.items():
            if var["meta"]["faculty"] == f:
                weekly_load.append(var["meta"]["length"])
        if weekly_load:
            model.Add(sum(weekly_load) <= max_weekly_hours_per_faculty)

    # Faculty daily cap (we model "session starts on day d" booleans and multiply by lengths)
    for f in intervals_for_faculty:
        for d in range(len(days)):
            daily_terms = []
            for sid, var in sess_vars.items():
                if var["meta"]["faculty"] == f:
                    is_on_day = model.NewBoolVar(f"{sid}_fac_day{d}")
                    # day_var = floor(start / slots_per_day)
                    day_var = model.NewIntVar(0, len(days)-1, f"{sid}_fac_dayvar")
                    model.AddDivisionEquality(day_var, var["start"], slots_per_day)
                    model.Add(day_var == d).OnlyEnforceIf(is_on_day)
                    model.Add(day_var != d).OnlyEnforceIf(is_on_day.Not())
                    # We'll count length * is_on_day as linear by expanding (length * bool) as int with bounds
                    if var["meta"]["length"] == 1:
                        daily_terms.append(is_on_day)
                    else:
                        # create int term length_if = length * is_on_day (use linearization)
                        length_if = model.NewIntVar(0, var["meta"]["length"], f"{sid}_fac_len_day{d}")
                        model.Add(length_if == var["meta"]["length"]).OnlyEnforceIf(is_on_day)
                        model.Add(length_if == 0).OnlyEnforceIf(is_on_day.Not())
                        daily_terms.append(length_if)
            if daily_terms:
                model.Add(sum(daily_terms) <= max_daily_hours_per_faculty)

    # Group daily cap (max classes per day) - already similar to above
    groups = set(s['group'] for s in sessions)
    for g in groups:
        for d in range(len(days)):
            daily_terms = []
            for sid, var in sess_vars.items():
                if var["meta"]["group"] == g:
                    is_on_day = model.NewBoolVar(f"{sid}_grp_day{d}")
                    day_var = model.NewIntVar(0, len(days)-1, f"{sid}_grp_dayvar")
                    model.AddDivisionEquality(day_var, var["start"], slots_per_day)
                    model.Add(day_var == d).OnlyEnforceIf(is_on_day)
                    model.Add(day_var != d).OnlyEnforceIf(is_on_day.Not())
                    if var["meta"]["length"] == 1:
                        daily_terms.append(is_on_day)
                    else:
                        length_if = model.NewIntVar(0, var["meta"]["length"], f"{sid}_grp_len_day{d}")
                        model.Add(length_if == var["meta"]["length"]).OnlyEnforceIf(is_on_day)
                        model.Add(length_if == 0).OnlyEnforceIf(is_on_day.Not())
                        daily_terms.append(length_if)
            if daily_terms:
                model.Add(sum(daily_terms) <= max_classes_per_day)

    # MIN DISTINCT DAYS per group (NEP: spread across week)
    # Create used_g_d booleans: True iff group g has at least one session starting on day d.
    for g in groups:
        used_day_bools = []
        for d in range(len(days)):
            used = model.NewBoolVar(f"used_{g}_day{d}")
            # used implies exists a session of group g on day d
            # build list of booleans is_on_day for sessions in group
            is_on_day_vars = []
            for sid, var in sess_vars.items():
                if var["meta"]["group"] == g:
                    is_on = model.NewBoolVar(f"{sid}_is_{g}_day{d}")
                    day_var = model.NewIntVar(0, len(days)-1, f"{sid}_{g}_dayvar{d}")
                    model.AddDivisionEquality(day_var, var["start"], slots_per_day)
                    # Link is_on with equality as before
                    model.Add(day_var == d).OnlyEnforceIf(is_on)
                    model.Add(day_var != d).OnlyEnforceIf(is_on.Not())
                    is_on_day_vars.append(is_on)
            if is_on_day_vars:
                # If any is_on_day_vars true then used == True
                model.AddBoolOr(is_on_day_vars).OnlyEnforceIf(used)
                # If used false then all is_on_day_vars false
                for v in is_on_day_vars:
                    model.Add(v == False).OnlyEnforceIf(used.Not())
            else:
                # no sessions for group -> used is false
                model.Add(used == False)
            used_day_bools.append(used)
        # enforce minimum distinct days
        # min_group_days can't exceed number of days available
        effective_min = min(min_group_days, len(days))
        model.Add(sum(used_day_bools) >= effective_min)

    # Objective: place sessions as early as possible (simple prototype objective)
    model.Minimize(sum(sess_vars[sid]['start'] for sid in sess_vars))

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = max_time
    solver.parameters.num_search_workers = 8
    solver.parameters.random_seed = 42
    solver.parameters.log_search_progress = True
    solver.parameters.cp_model_probing_level = 0
    solver.parameters.cp_model_presolve = False

    status = solver.Solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        result = {}
        for sid, info in sess_vars.items():
            st = solver.Value(info['start'])
            room = None
            if enforce_rooms and 'room' in info:
                room = solver.Value(info['room'])
            result[sid] = (st, room)
        return result
    return None

# wrapper
def solve_with_ortools(sessions, rooms, days, slots_per_day, max_time=30, max_classes_per_day=5,
                       max_consec_slots=3, max_weekly_hours_per_faculty=20, max_daily_hours_per_faculty=5,
                       project_block_positions=None, is_project_func=None, min_group_days=3):
    return solve_with_ortools_intervals(sessions, rooms, days, slots_per_day, max_time=max_time,
                                        max_consec_slots=max_consec_slots, max_classes_per_day=max_classes_per_day,
                                        max_weekly_hours_per_faculty=max_weekly_hours_per_faculty,
                                        max_daily_hours_per_faculty=max_daily_hours_per_faculty,
                                        enforce_rooms=False, project_block_positions=project_block_positions,
                                        is_project_func=is_project_func, min_group_days=min_group_days)
