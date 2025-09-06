import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from collections import defaultdict
from typing import Dict, List, Tuple, Optional, Any
from hybrid_timetable.utils.clashes import detect_clashes

def analyze_schedule(schedule: Dict[str, Any], rooms: List[Dict], slots_per_day: int, group_sizes: Optional[Dict[str, int]] = None) -> Dict[str, List]:
    """
    Analyze timetable clashes with enhanced reporting.

    Args:
        schedule: Dictionary of session assignments
        rooms: List of room dictionaries with capacity info
        slots_per_day: Number of time slots per day
        group_sizes: Dictionary mapping group names to sizes

    Returns:
        Dictionary containing clash information by type
    """
    clashes = detect_clashes(schedule, slots_per_day, rooms, group_sizes)

    print("\n" + "="*50)
    print("🎯 TIMETABLE CLASH ANALYSIS REPORT")
    print("="*50)

    total_clashes = sum(len(clash_list) for clash_list in clashes.values())

    if total_clashes == 0:
        print("✅ EXCELLENT! No clashes detected in the timetable.")
        print("🎉 Schedule is conflict-free and ready for deployment.")
    else:
        print(f"⚠️  WARNING: {total_clashes} total clashes detected")
        print("-" * 50)

    for clash_type, clash_list in clashes.items():
        if clash_list:
            print(f"\n🔴 {clash_type.upper()} CLASHES: ({len(clash_list)} instances)")
            print("-" * 40)
            for i, item in enumerate(clash_list, 1):
                print(f"  {i:2d}. {item}")
        else:
            print(f"\n✅ {clash_type.upper()}: No clashes detected")

    # Summary statistics
    if total_clashes > 0:
        print(f"\n📊 SUMMARY STATISTICS:")
        print(f"   • Total clashes: {total_clashes}")
        print(f"   • Clash types affected: {sum(1 for lst in clashes.values() if lst)}")
        print(f"   • Most critical: {max(clashes.keys(), key=lambda k: len(clashes[k]))}")

    print("="*50)
    return clashes

def generate_matrix(schedule: Dict[str, Any], entity_type: str, days: List[str], slots_per_day: int) -> Tuple[np.ndarray, List[str]]:
    """
    Generic matrix generator for groups, faculties, or rooms.

    Args:
        schedule: Dictionary of session assignments
        entity_type: Type of entity ('group', 'faculty', or 'room')
        days: List of day names
        slots_per_day: Number of slots per day

    Returns:
        Tuple of (matrix, entity_list)
    """
    if entity_type == "room":
        entities = sorted({info.get("room") for info in schedule.values() if info.get("room")})
    else:
        entities = sorted({info["meta"][entity_type] for info in schedule.values()})

    entity_idx = {e: i for i, e in enumerate(entities)}
    total_slots = len(days) * slots_per_day
    matrix = np.zeros((len(entities), total_slots), dtype=int)

    for sid, info in schedule.items():
        start = info["start"]
        length = info["length"]

        if entity_type == "room":
            e = info.get("room")
        else:
            e = info["meta"].get(entity_type)

        if not e:
            continue

        idx = entity_idx[e]
        for offset in range(length):
            slot = start + offset
            if slot >= total_slots:
                slot = total_slots - 1
            matrix[idx, slot] += 1

    return matrix, entities


def plot_heatmap(matrix: np.ndarray, labels: List[str], days: List[str], slots_per_day: int,
                 title: str = "Heatmap", save_path: Optional[str] = None, show: bool = True,
                 cmap: str = "YlGnBu", figsize: Optional[Tuple[float, float]] = None) -> Optional[plt.Figure]:
    """
    Enhanced heatmap plotting function with professional visuals.

    Args:
        matrix: 2D numpy array of occupancy data
        labels: List of entity names (groups/faculties/rooms)
        days: List of day names
        slots_per_day: Number of slots per day
        title: Plot title
        save_path: Path to save PNG file (optional)
        show: Whether to display the plot
        cmap: Color map for the heatmap
        figsize: Figure size (auto-calculated if None)

    Returns:
        Matplotlib figure object if return_fig is True, else None
    """
    total_slots = len(days) * slots_per_day

    if figsize is None:
        figsize = (max(total_slots * 0.4, 8), max(len(labels) * 0.4, 6))

    fig, ax = plt.subplots(figsize=figsize)

    # Create custom colormap for better overlap visualization
    if "overlap" in title.lower() or "clash" in title.lower():
        cmap = "Reds"
    elif "faculty" in title.lower():
        cmap = "Blues"
    elif "group" in title.lower():
        cmap = "Greens"

    # Plot heatmap with enhanced styling
    sns.heatmap(matrix, annot=True, fmt="d", cmap=cmap,
                cbar_kws={'label': 'Sessions/Overlaps'},
                linewidths=0.5, linecolor='lightgray',
                square=False, ax=ax)

    # Enhanced labels and title
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    ax.set_xlabel("Time Slots", fontsize=12, labelpad=10)
    ax.set_ylabel("Entities", fontsize=12, labelpad=10)

    # Custom x-axis labels with day/slot format
    x_labels = []
    for s in range(total_slots):
        day_name = days[s // slots_per_day]
        slot_num = s % slots_per_day + 1
        x_labels.append(f"{day_name[:3]}\n{slot_num}")

    ax.set_xticks(np.arange(total_slots) + 0.5)
    ax.set_xticklabels(x_labels, rotation=0, ha='center', fontsize=9)
    ax.set_yticklabels(labels, rotation=0, fontsize=10)

    # Add summary statistics as text
    max_overlaps = np.max(matrix)
    total_sessions = np.sum(matrix)
    avg_occupancy = total_sessions / (len(labels) * total_slots) * 100

    stats_text = f"Max: {max_overlaps} | Total: {total_sessions} | Avg: {avg_occupancy:.1f}%"
    fig.text(0.02, 0.98, stats_text, fontsize=10,
             verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"💾 Heatmap saved to: {save_path}")

    if show:
        plt.show()
    else:
        plt.close()

    return fig if not show else None


def visualize_entity_schedule(schedule: Dict[str, Any], entity_type: str, days: List[str],
                            slots_per_day: int, save_path: Optional[str] = None,
                            show: bool = True) -> Tuple[np.ndarray, List[str]]:
    """
    Complete pipeline for entity heatmap visualization.

    Args:
        schedule: Dictionary of session assignments
        entity_type: Type of entity to visualize ('group', 'faculty', 'room')
        days: List of day names
        slots_per_day: Number of slots per day
        save_path: Path to save PNG file
        show: Whether to display the plot

    Returns:
        Tuple of (matrix, entities)
    """
    matrix, entities = generate_matrix(schedule, entity_type, days, slots_per_day)

    title = f"{entity_type.capitalize()} Timetable Heatmap"
    if np.max(matrix) > 1:
        title += " (Red = Overlaps)"

    plot_heatmap(matrix, entities, days, slots_per_day, title=title,
                save_path=save_path, show=show)

    return matrix, entities


def generate_schedule_summary(schedule: Dict[str, Any], days: List[str], slots_per_day: int) -> Dict[str, Any]:
    """
    Generate comprehensive summary statistics for the schedule.

    Args:
        schedule: Dictionary of session assignments

    Returns:
        Dictionary containing summary statistics
    """
    total_slots = len(days) * slots_per_day
    total_sessions = len(schedule)

    # Calculate utilization metrics
    groups = set(info["meta"]["group"] for info in schedule.values())
    faculties = set(info["meta"]["faculty"] for info in schedule.values())
    rooms = set(info.get("room") for info in schedule.values() if info.get("room"))

    # Session length distribution
    session_lengths = [info["length"] for info in schedule.values()]
    avg_session_length = np.mean(session_lengths)
    max_session_length = np.max(session_lengths)

    # Time slot utilization
    slot_utilization = np.zeros(total_slots)
    for info in schedule.values():
        start = info["start"]
        length = info["length"]
        for offset in range(length):
            slot = start + offset
            if slot < total_slots:
                slot_utilization[slot] += 1

    avg_slot_utilization = np.mean(slot_utilization)
    max_slot_utilization = np.max(slot_utilization)

    return {
        "total_sessions": total_sessions,
        "total_slots": total_slots,
        "groups_count": len(groups),
        "faculties_count": len(faculties),
        "rooms_count": len(rooms),
        "avg_session_length": avg_session_length,
        "max_session_length": max_session_length,
        "avg_slot_utilization": avg_slot_utilization,
        "max_slot_utilization": max_slot_utilization,
        "utilization_percentage": (np.sum(slot_utilization > 0) / total_slots) * 100
    }


def print_schedule_summary(schedule: Dict[str, Any], days: List[str], slots_per_day: int) -> None:
    """
    Print formatted schedule summary statistics.
    """
    summary = generate_schedule_summary(schedule, days, slots_per_day)

    print("\n" + "="*60)
    print("📊 TIMETABLE SUMMARY STATISTICS")
    print("="*60)
    print(f"🎯 Total Sessions:     {summary['total_sessions']}")
    print(f"📅 Total Time Slots:   {summary['total_slots']} ({len(days)} days × {slots_per_day} slots)")
    print(f"👥 Groups:            {summary['groups_count']}")
    print(f"👨‍🏫 Faculty Members:  {summary['faculties_count']}")
    print(f"🏫 Rooms Used:        {summary['rooms_count']}")
    print()
    print("⏱️  Session Metrics:")
    print(f"   • Avg Session Length: {summary['avg_session_length']:.2f} slots")
    print(f"   • Max Session Length: {summary['max_session_length']} slots")
    print()
    print("📈 Utilization Metrics:")
    print(f"   • Avg Slot Usage:     {summary['avg_slot_utilization']:.2f} sessions")
    print(f"   • Peak Slot Usage:    {summary['max_slot_utilization']} sessions")
    print(f"   • Overall Utilization: {summary['utilization_percentage']:.1f}%")
    print("="*60)


# Legacy functions for backward compatibility
def visualize_schedule(schedule, days, slots_per_day, rooms, group_sizes=None, return_fig=False):
    """Legacy group visualization function."""
    return visualize_entity_schedule(schedule, "group", days, slots_per_day, show=return_fig is False)

def visualize_faculty_schedule(schedule, days, slots_per_day, return_fig=False):
    """Legacy faculty visualization function."""
    return visualize_entity_schedule(schedule, "faculty", days, slots_per_day, show=return_fig is False)

def generate_group_matrix(schedule, days, slots_per_day):
    """Legacy group matrix generator."""
    return generate_matrix(schedule, "group", days, slots_per_day)

def generate_faculty_matrix(schedule, days, slots_per_day):
    """Legacy faculty matrix generator."""
    return generate_matrix(schedule, "faculty", days, slots_per_day)

def generate_room_matrix(schedule, days, slots_per_day):
    """Legacy room matrix generator."""
    matrix, _ = generate_matrix(schedule, "room", days, slots_per_day)
    return matrix

def plot_heatmap_legacy(matrix, labels, title="Heatmap"):
    """Legacy heatmap plotting function."""
    plt.figure(figsize=(12,6))
    sns.heatmap(matrix, annot=True, fmt="d", xticklabels=False, yticklabels=labels, cmap="coolwarm")
    plt.title(title)
    plt.xlabel("Time Slots")
    plt.ylabel("Groups / Faculties")
    plt.show()
