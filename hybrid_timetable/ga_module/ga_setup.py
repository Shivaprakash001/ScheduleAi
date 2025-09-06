import random
from deap import base, creator, tools
import numpy as np
from functools import partial
from .fitness import ga_fitness

def setup_ga(sessions, rooms, days, slots_per_day,
             elective_slots_per_day=None, is_elective_func=None,
             project_block_positions=None, is_project_func=None,
             faculty_prefs=None, use_parallel=True):
    total_slots = len(days) * slots_per_day
    creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
    creator.create("Individual", list, fitness=creator.FitnessMin)
    toolbox = base.Toolbox()

    def encode(start, room): return start * 100 + room
    def decode(g): return divmod(g, 100)

    def possible_starts(length):
        return [d * slots_per_day + p
                for d in range(len(days))
                for p in range(slots_per_day - length + 1)]

    start_opts = {l: possible_starts(l) for l in set(s['length'] for s in sessions)}
    room_indices = list(range(len(rooms)))

    def init_ind():
        genome = []
        for s in sessions:
            start = random.choice(start_opts[s['length']])
            # choose room indices matching lab/lecture preference if possible
            poss_rooms = [i for i, r in enumerate(rooms)
                          if (('lab' in s['name'].lower()) == ('lab' in r['name'].lower()))]
            if not poss_rooms:
                poss_rooms = room_indices
            room = random.choice(poss_rooms)
            genome.append(encode(start, room))
        return creator.Individual(genome)

    toolbox.register("individual", init_ind)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    from functools import partial
    fitness_func = partial(ga_fitness, sessions=sessions, rooms=rooms, days=days,
                          slots_per_day=slots_per_day, max_classes_per_day=5,
                          max_consec_slots=3, max_daily_hours_per_faculty=5,
                          project_block_positions=project_block_positions, is_project_func=is_project_func)

    toolbox.register("evaluate", fitness_func)
    toolbox.register("mate", tools.cxTwoPoint)
    toolbox.register("mutate", tools.mutShuffleIndexes, indpb=0.05)
    toolbox.register("select", tools.selTournament, tournsize=3)

    def decode_ind(ind):
        out = {}
        for idx, g in enumerate(ind):
            start, room = decode(g)
            s = sessions[idx]
            out[s['sess_id']] = {
                "start": start,
                "room": rooms[room]["name"] if isinstance(room, int) else room,
                "length": s['length'],
                "meta": s
            }
        return out

    return toolbox, decode_ind
