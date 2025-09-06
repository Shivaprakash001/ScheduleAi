from .utils.helpers import expand_courses
from .ortools_solver.solver import solve_with_ortools
from .room_assignment import greedy_room_assignment
from .ga_module.ga_setup import setup_ga
from .ga_module.fitness import ga_fitness
from deap import tools, algorithms
import numpy as np

def generate_timetable(courses, rooms, days, slots_per_day,
                       ngen=40, pop_size=60, max_time=30,
                       max_classes_per_day=5, max_consec_slots=3,
                       max_weekly_hours_per_faculty=20, max_daily_hours_per_faculty=5,
                       elective_slots_per_day=None, is_elective_func=None,
                       project_block_positions=None, is_project_func=None,
                       faculty_prefs=None, group_sizes=None,
                       use_ga=True, assign_rooms=True, min_group_days=3,
                       day_balance_fraction=0.4, elective_groups=None):
    """
    Hybrid NEP2020 Timetable Generator
    - OR-Tools ensures feasibility (hard)
    - Greedy room assignment respects capacities (if assign_rooms True)
    - GA refinement optimizes NEP soft goals (day-balance, gaps, workload)
    """
    sessions = expand_courses(courses)

    # Step 1: OR-Tools placement (times only)
    feasible = solve_with_ortools(sessions, rooms, days, slots_per_day,
                                  max_time=max_time,
                                  max_classes_per_day=max_classes_per_day,
                                  max_consec_slots=max_consec_slots,
                                  max_weekly_hours_per_faculty=max_weekly_hours_per_faculty,
                                  max_daily_hours_per_faculty=max_daily_hours_per_faculty,
                                  project_block_positions=project_block_positions,
                                  is_project_func=is_project_func,
                                  min_group_days=min_group_days)
    if not feasible:
        raise RuntimeError("No feasible solution from OR-Tools.")

    # Step 2: Greedy room assignment using start times from OR-Tools
    if assign_rooms and group_sizes:
        start_times = {sid: st for sid, (st, rm) in feasible.items()}
        assignment = greedy_room_assignment(start_times, sessions, rooms, group_sizes)
        if not assignment:
            print("⚠️ Greedy room assignment failed; continuing without assigned rooms.")
        else:
            for sid, rm in assignment.items():
                st, _ = feasible[sid]
                feasible[sid] = (st, rm)

    # Step 3: GA refinement (if enabled) - seeded with feasible solution
    if use_ga:
        toolbox, decode = setup_ga(sessions, rooms, days, slots_per_day,
                                   elective_slots_per_day=elective_slots_per_day,
                                   is_elective_func=is_elective_func,
                                   project_block_positions=project_block_positions,
                                   is_project_func=is_project_func,
                                   faculty_prefs=faculty_prefs
                                   )

        # inject day_balance_fraction into fitness function
        from functools import partial
        toolbox.unregister("evaluate")
        toolbox.register("evaluate", partial(
            ga_fitness,
            sessions=sessions,
            rooms=rooms,
            days=days,
            slots_per_day=slots_per_day,
            max_classes_per_day=max_classes_per_day,
            max_consec_slots=max_consec_slots,
            max_daily_hours_per_faculty=max_daily_hours_per_faculty,
            project_block_positions=project_block_positions,
            is_project_func=is_project_func,
            group_sizes=group_sizes,
            day_balance_fraction=day_balance_fraction
        ))

        def encode(start, room):
            if isinstance(room, str):
                room_idx = next((i for i, r in enumerate(rooms) if r["name"] == room), 0)
            else:
                room_idx = room if room is not None else 0
            return int(start) * 100 + int(room_idx)

        feasible_vals = []
        for s in sessions:
            sid = s['sess_id']
            st, rm = feasible[sid]
            feasible_vals.append(encode(st, rm))

        seed_ind = toolbox.individual()
        seed_ind[:] = feasible_vals

        # Step 3 continued: GA refinement
        pop = toolbox.population(n=pop_size)
        pop[0] = seed_ind  # seed first individual with feasible solution

        hof = tools.HallOfFame(1)
        stats = tools.Statistics(lambda ind: ind.fitness.values)
        stats.register("avg", np.mean)
        stats.register("min", np.min)
        stats.register("max", np.max)

        algorithms.eaSimple(pop, toolbox, cxpb=0.7, mutpb=0.2, ngen=ngen,
                            stats=stats, halloffame=hof, verbose=True)

        # decode best individual
        best_schedule = decode(hof[0])
        return best_schedule

    # If GA disabled, just return feasible OR-Tools schedule
    schedule_dict = {}
    for sid, (st, rm) in feasible.items():
        s = next(s for s in sessions if s['sess_id'] == sid)
        schedule_dict[sid] = {"start": st, "room": rm, "length": s['length'], "meta": s}
    return schedule_dict
