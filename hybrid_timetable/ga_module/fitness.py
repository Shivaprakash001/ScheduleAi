import math
from collections import defaultdict
from ..utils.helpers import build_weekly_block_indices

def ga_fitness(ind, sessions, rooms, days, slots_per_day,
               max_classes_per_day=5, max_consec_slots=3, max_daily_hours_per_faculty=5,
               project_block_positions=None, is_project_func=None,
               group_sizes=None, day_balance_fraction=0.4,
               elective_groups=None, faculty_prefs=None):
    """
    Fitness with NEP-2020 soft constraints:
    - heavy penalties for clashes and room capacity violations
    - penalties for day imbalance, gaps, consecutive over-limit, faculty daily overload, workload variance
    - added elective balancing and faculty load preferences
    """
    def decode(g): return divmod(g, 100)

    assign = {}
    for idx, g in enumerate(ind):
        start, room_idx = decode(g)
        # clamp start to valid range (robustness)
        total_slots = len(days) * slots_per_day
        start = max(0, min(start, total_slots - 1))
        room_idx = max(0, min(room_idx, len(rooms)-1))
        assign[sessions[idx]['sess_id']] = (start, room_idx, sessions[idx]['length'], sessions[idx])

    faculty_occ, group_occ, room_occ = defaultdict(list), defaultdict(list), defaultdict(list)
    hard_penalty, soft_penalty = 0, 0

    # Hard: no overlaps
    for sid, (start, room_idx, length, meta) in assign.items():
        for off in range(length):
            slot = start + off
            faculty_occ[(meta['faculty'], slot)].append(sid)
            group_occ[(meta['group'], slot)].append(sid)
            room_name = rooms[room_idx]["name"] if isinstance(room_idx, int) else room_idx
            room_occ[(room_name, slot)].append(sid)

    for occ in (faculty_occ, group_occ, room_occ):
        for k, v in occ.items():
            if len(v) > 1:
                hard_penalty += 200 * (len(v) - 1)

    # Hard: max classes/day per group
    group_daily_slots = defaultdict(lambda: defaultdict(list))
    for sid, (start, _, length, meta) in assign.items():
        group = meta['group']
        day = start // slots_per_day
        for off in range(length):
            group_daily_slots[group][day].append((start % slots_per_day) + off)

    for group, dayslots in group_daily_slots.items():
        for day, slots in dayslots.items():
            if len(set(slots)) > max_classes_per_day:
                hard_penalty += 300 * (len(set(slots)) - max_classes_per_day)

    # Hard-ish: room capacity violations (if group_sizes present)
    if group_sizes:
        for sid, (start, room_idx, length, meta) in assign.items():
            room = rooms[room_idx]
            size = group_sizes.get(meta['group'], 0)
            if size > room['capacity']:
                # big penalty (hard-ish)
                hard_penalty += 500 + 10 * (size - room['capacity'])

    # Soft: workload balance (faculty variance)
    faculty_hours = defaultdict(int)
    for sid, (start, _, length, meta) in assign.items():
        faculty_hours[meta['faculty']] += length
    vals = list(faculty_hours.values())
    if vals:
        avg = sum(vals) / len(vals)
        variance = sum((x - avg) ** 2 for x in vals) / len(vals)
        soft_penalty += variance

    # Soft: student gaps (minimize idle slots)
    for group, dayslots in group_daily_slots.items():
        for day, slots in dayslots.items():
            slots_sorted = sorted(set(slots))
            for i in range(len(slots_sorted) - 1):
                if slots_sorted[i+1] > slots_sorted[i] + 1:
                    soft_penalty += 1

    # Soft: limit consecutive sessions (heavier penalty for >3)
    for group, dayslots in group_daily_slots.items():
        for day, slots in dayslots.items():
            slots_sorted = sorted(set(slots))
            consec = 1
            for i in range(1, len(slots_sorted)):
                if slots_sorted[i] == slots_sorted[i-1] + 1:
                    consec += 1
                    if consec > max_consec_slots:
                        soft_penalty += 10 * (consec - max_consec_slots)  # increased weight
                else:
                    consec = 1

    # Soft: faculty daily overload
    faculty_daily = defaultdict(lambda: defaultdict(int))
    for sid, (start, _, length, meta) in assign.items():
        day = start // slots_per_day
        faculty_daily[meta['faculty']][day] += length
    for f, days_load in faculty_daily.items():
        for d, load in days_load.items():
            if load > max_daily_hours_per_faculty:
                soft_penalty += 10 * (load - max_daily_hours_per_faculty)

    # Soft: daily load balance for groups
    for group, dayslots in group_daily_slots.items():
        loads = [len(set(slots)) for slots in dayslots.values()]
        if loads:
            avg = sum(loads) / len(loads)
            variance = sum((x - avg)**2 for x in loads) / len(loads)
            soft_penalty += variance * 5

    # Soft: day-balance & clustering penalty
    for group, dayslots in group_daily_slots.items():
        total_sessions = sum(len(set(slots)) for slots in dayslots.values())
        if total_sessions <= 0:
            continue
        for d, slots in dayslots.items():
            cnt = len(set(slots))
            # Existing day fraction penalty
            if cnt > math.ceil(day_balance_fraction * total_sessions):
                soft_penalty += 100 * (cnt - math.ceil(day_balance_fraction * total_sessions))  # stronger
        # Penalize gaps/clustering more heavily
        all_slots = sorted([slot for slots in dayslots.values() for slot in slots])
        for i in range(1, len(all_slots)):
            gap = all_slots[i] - all_slots[i-1] - 1
            soft_penalty += 2 * gap  # heavier penalty for idle slots

    # Soft: elective balancing - spread electives across days and avoid overlaps
    if elective_groups:
        elective_slots = defaultdict(lambda: defaultdict(int))  # group -> slot -> count
        elective_days = defaultdict(lambda: defaultdict(int))  # group -> day -> count
        for sid, (start, _, length, meta) in assign.items():
            if meta['group'] in elective_groups and 'elective' in meta['name'].lower():
                day = start // slots_per_day
                for off in range(length):
                    slot = start + off
                    elective_slots[meta['group']][slot] += 1
                elective_days[meta['group']][day] += length
        # Penalize if electives of different groups overlap too much
        for slot in range(len(days) * slots_per_day):
            counts = [elective_slots[g].get(slot, 0) for g in elective_groups]
            if sum(counts) > 1:
                soft_penalty += 50 * (sum(counts) - 1)
        # Penalize if electives are concentrated on same days
        for day in range(len(days)):
            day_counts = [elective_days[g].get(day, 0) for g in elective_groups]
            if sum(day_counts) > 0 and max(day_counts) > sum(day_counts) / len(elective_groups):
                soft_penalty += 30 * (max(day_counts) - sum(day_counts) / len(elective_groups))

    # Soft: faculty load preferences (morning/afternoon)
    if faculty_prefs:
        morning_slots = set(range(slots_per_day // 2))
        afternoon_slots = set(range(slots_per_day // 2, slots_per_day))
        for sid, (start, _, length, meta) in assign.items():
            pref = faculty_prefs.get(meta['faculty'])
            if pref:
                day_slot = start % slots_per_day
                if pref == 'morning' and day_slot not in morning_slots:
                    soft_penalty += 20
                elif pref == 'afternoon' and day_slot not in afternoon_slots:
                    soft_penalty += 20

    # Soft: project block alignment penalty (existing)
    if project_block_positions and is_project_func:
        project_slots = build_weekly_block_indices(days, slots_per_day, project_block_positions)
        for sid, (start, _, length, meta) in assign.items():
            if not is_project_func(meta):
                for off in range(length):
                    if (start + off) in project_slots:
                        soft_penalty += 5

    # total fitness: heavy weight on hard_penalty
    return (hard_penalty + 0.05 * soft_penalty,)
