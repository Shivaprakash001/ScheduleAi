from collections import defaultdict

def greedy_room_assignment(schedule_times, sessions, rooms, group_sizes):
    """Greedy room assignment considering capacity and session lengths."""
    room_schedule = {r: set() for r in range(len(rooms))}
    assignment = {}

    # sort: labs (longer) first, then larger groups first
    sess_list = sorted(sessions, key=lambda s: (-s['length'], -group_sizes.get(s['group'], 0)))
    for s in sess_list:
        sid = s['sess_id']
        start = schedule_times[sid]
        group = s["group"]
        size = group_sizes.get(group, 0)

        placed = False
        # prefer lecture rooms for lectures, labs for labs (simple heuristic)
        name_low = s['name'].lower()
        prefer_lab = ('lab' in name_low) or ('project' in name_low)
        room_order = list(range(len(rooms)))
        # prefer matching rooms first
        room_order.sort(key=lambda r_idx: (('lab' in rooms[r_idx]['name'].lower()) != prefer_lab))
        for r in room_order:
            room = rooms[r]
            if size > room["capacity"]:
                continue
            conflict = False
            for off in range(s['length']):
                if (start + off) in room_schedule[r]:
                    conflict = True
                    break
            if not conflict:
                for off in range(s['length']):
                    room_schedule[r].add(start + off)
                assignment[sid] = room["name"]
                placed = True
                break
        if not placed:
            return None
    return assignment
