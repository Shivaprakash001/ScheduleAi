from collections import defaultdict

def absolute_slot(day_idx, pos, slots_per_day):
    return day_idx * slots_per_day + pos

def build_weekly_block_indices(days, slots_per_day, positions):
    indices = []
    for d in range(len(days)):
        for p in positions:
            indices.append(absolute_slot(d, p, slots_per_day))
    return indices

def expand_courses(courses):
    sessions = []
    for c in courses:
        groups = c["group"] if isinstance(c["group"], list) else [c["group"]]
        n = c["weekly_slots"]
        k = c["consecutive"]

        for g in groups:
            if k == 1:
                for i in range(n):
                    sessions.append({
                        "sess_id": f"{c['id']}_{g}_s{i}",
                        "course_id": c["id"],
                        "name": c["name"],
                        "faculty": c["faculty"],
                        "group": g,
                        "length": 1
                    })
            else:
                if n % k != 0:
                    raise ValueError("weekly_slots must be divisible by consecutive length.")
                cnt = n // k
                for i in range(cnt):
                    sessions.append({
                        "sess_id": f"{c['id']}_{g}_lab{i}",
                        "course_id": c["id"],
                        "name": c["name"],
                        "faculty": c["faculty"],
                        "group": g,
                        "length": k
                    })
    return sessions
