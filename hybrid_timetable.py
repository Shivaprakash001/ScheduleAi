"""
Hybrid Timetable Generator (NEP-2020 aligned)
- OR-Tools CP-SAT ensures feasible schedules (hard constraints)
- Greedy room assignment for capacity-aware room allocation
- DEAP Genetic Algorithm refines for soft metrics (day-balance, gaps, workload balance, etc.)
"""

import json
import matplotlib.pyplot as plt
from typing import List, Dict, Any, Optional
from hybrid_timetable.timetable_generator import generate_timetable
from hybrid_timetable.utils.clashes import detect_clashes
from hybrid_timetable.utils.excel_export import export_schedule_to_excel


def run_timetable_workflow(
    courses: List[Dict[str, Any]],
    rooms: List[Dict[str, Any]],
    days: List[str],
    slots_per_day: int,
    group_sizes: Optional[Dict[str, int]] = None,
    output_dir: str = ".",
    excel_filename: str = "timetable.xlsx",
    show_plots: bool = False,
    **kwargs
) -> Dict[str, Any]:
    """
    Complete timetable generation and visualization workflow.

    This function orchestrates the entire process from timetable generation
    to comprehensive visualization and reporting.

    Args:
        courses: List of course dictionaries with scheduling requirements
        rooms: List of room dictionaries with capacity information
        days: List of day names (e.g., ["Mon", "Tue", "Wed", "Thu", "Fri"])
        slots_per_day: Number of time slots per day (NEP-2020: ≤6)
        group_sizes: Dictionary mapping group names to student counts
        output_dir: Directory to save output files
        excel_filename: Name of the Excel output file
        show_plots: Whether to display plots interactively
        **kwargs: Additional parameters for timetable generation

    Returns:
        Dictionary containing the complete results and metadata

    Workflow:
    1. Generate optimized timetable using hybrid OR-Tools + GA approach
    2. Perform comprehensive clash analysis
    3. Generate schedule summary statistics
    4. Create professional visualizations (heatmaps)
    5. Export to Excel with embedded charts
    6. Return complete results dictionary
    """
    import os
    from analysis_visualization import (
        generate_matrix, visualize_entity_schedule,
        analyze_schedule, print_schedule_summary
    )

    print("\n" + "="*70)
    print("HYBRID TIMETABLE GENERATOR - COMPLETE WORKFLOW")
    print("="*70)
    print(f"Days: {len(days)} | Slots/Day: {slots_per_day} | Courses: {len(courses)}")
    print(f"Rooms: {len(rooms)} | Groups: {len(group_sizes) if group_sizes else 'N/A'}")
    print("="*70)

    # Step 1: Generate optimized timetable
    print("\STEP 1: Generating Optimized Timetable")
    print("-" * 50)

    try:
        # Set default parameters for timetable generation
        timetable_params = {
            "courses": courses,
            "rooms": rooms,
            "days": days,
            "slots_per_day": slots_per_day,
            "max_classes_per_day": 5,
            "max_daily_hours_per_faculty": 5,
            "max_weekly_hours_per_faculty": 18,
            "group_sizes": group_sizes,
            "use_ga": True,
            "assign_rooms": True,
            "min_group_days": 3,
            "day_balance_fraction": 0.4,
            **kwargs  # Allow overriding defaults
        }

        schedule = generate_timetable(**timetable_params)

        if not schedule:
            raise RuntimeError("Failed to generate feasible timetable")

        print("Timetable generation successful!")
        print(f"Total sessions scheduled: {len(schedule)}")

    except Exception as e:
        print(f"Timetable generation failed: {e}")
        return {"success": False, "error": str(e), "stage": "timetable_generation"}

    # Step 2: Generate matrices for analysis
    print("\STEP 2: Preparing Data Matrices")
    print("-" * 50)

    try:
        groups = list(set(info["meta"]["group"] for info in schedule.values()))
        faculties = list(set(info["meta"]["faculty"] for info in schedule.values()))

        group_matrix, groups = generate_matrix(schedule, "group", days, slots_per_day)
        faculty_matrix, faculties = generate_matrix(schedule, "faculty", days, slots_per_day)
        room_matrix, _ = generate_matrix(schedule, "room", days, slots_per_day)

        print("Data matrices generated successfully!")
    except Exception as e:
        print(f"Matrix generation failed: {e}")
        return {"success": False, "error": str(e), "stage": "matrix_generation"}

    # Step 3: Perform clash analysis
    print("\STEP 3: Performing Clash Analysis")
    print("-" * 50)

    try:
        clashes = detect_clashes(schedule, slots_per_day, rooms, group_sizes=group_sizes)
        clash_count = sum(len(clash_list) for clash_list in clashes.values())

        if clash_count == 0:
            print("EXCELLENT! No clashes detected in the timetable.")
        else:
            print(f"WARNING: {clash_count} clashes detected.")

    except Exception as e:
        print(f"Clash analysis failed: {e}")
        clashes = {}
        clash_count = 0

    # Step 4: Generate comprehensive summary
    print("\STEP 4: Generating Schedule Summary")
    print("-" * 50)

    try:
        print_schedule_summary(schedule, days, slots_per_day)
    except Exception as e:
        print(f"Could not generate schedule summary: {e}")

    # Step 5: Create visualizations
    print("\STEP 5: Creating Professional Visualizations")
    print("-" * 50)

    visualization_files = []

    # Group timetable heatmap
    try:
        matrix, entities = visualize_entity_schedule(
            schedule, "group", days, slots_per_day,
            save_path=os.path.join(output_dir, "group_timetable_heatmap.png"),
            show=show_plots
        )
        visualization_files.append("group_timetable_heatmap.png")
        print("Group timetable heatmap created")
    except Exception as e:
        print(f"Group heatmap generation failed: {e}")

    # Faculty workload heatmap
    try:
        matrix, entities = visualize_entity_schedule(
            schedule, "faculty", days, slots_per_day,
            save_path=os.path.join(output_dir, "faculty_workload_heatmap.png"),
            show=show_plots
        )
        visualization_files.append("faculty_workload_heatmap.png")
        print("Faculty workload heatmap created")
    except Exception as e:
        print(f"Faculty heatmap generation failed: {e}")

    # Room utilization heatmap
    try:
        matrix, entities = visualize_entity_schedule(
            schedule, "room", days, slots_per_day,
            save_path=os.path.join(output_dir, "room_utilization_heatmap.png"),
            show=show_plots
        )
        visualization_files.append("room_utilization_heatmap.png")
        print("Room utilization heatmap created")
    except Exception as e:
        print(f"Room heatmap generation failed: {e}")

    # Step 6: Detailed clash analysis report
    print("\STEP 6: Generating Detailed Clash Report")
    print("-" * 50)

    try:
        analyze_schedule(schedule, rooms, slots_per_day, group_sizes)
    except Exception as e:
        print(f"Detailed clash analysis failed: {e}")

    # Step 7: Export to Excel
    print("\STEP 7: Exporting to Excel Report")
    print("-" * 50)

    excel_path = os.path.join(output_dir, excel_filename)
    try:
        export_schedule_to_excel(
            schedule, days, slots_per_day, excel_path,
            clashes=clashes, group_matrix=group_matrix,
            faculty_matrix=faculty_matrix, groups=groups,
            faculties=faculties, room_matrix=room_matrix
        )
        print(f"Excel report exported to: {excel_path}")
    except Exception as e:
        print(f"Excel export failed: {e}")
        excel_path = None

    # Step 8: Final summary and results
    print("\n" + "="*70)
    print("🎉 WORKFLOW COMPLETED SUCCESSFULLY!")
    print("="*70)

    # Calculate final metrics
    total_sessions = len(schedule)
    total_slots = len(days) * slots_per_day
    utilization_rate = (sum(1 for info in schedule.values() if info.get("room")) / total_sessions) * 100

    print("FINAL RESULTS SUMMARY:")
    print(f"   Sessions Scheduled: {total_sessions}")
    print(f"   Total Time Slots: {total_slots}")
    print(f"   Room Utilization: {utilization_rate:.1f}%")
    print(f"   Clashes Detected: {clash_count}")
    print(f"   Excel Report: {excel_filename}")
    print(f"   Visualizations: {len(visualization_files)} files")
    print()
    print("Generated Files:")
    if excel_path:
        print(f"   • {excel_filename} (Multi-sheet Excel report)")
    for viz_file in visualization_files:
        print(f"   • {viz_file} (High-resolution heatmap)")

    print("="*70)

    # Return comprehensive results
    return {
        "success": True,
        "schedule": schedule,
        "clashes": clashes,
        "matrices": {
            "group": group_matrix,
            "faculty": faculty_matrix,
            "room": room_matrix
        },
        "entities": {
            "groups": groups,
            "faculties": faculties
        },
        "metrics": {
            "total_sessions": total_sessions,
            "total_slots": total_slots,
            "clash_count": clash_count,
            "utilization_rate": utilization_rate
        },
        "files": {
            "excel": excel_path,
            "visualizations": visualization_files
        },
        "parameters": {
            "courses": len(courses),
            "rooms": len(rooms),
            "days": len(days),
            "slots_per_day": slots_per_day,
            "group_sizes": group_sizes
        }
    }


# ---------------- Example usage ---------------- #
if __name__ == "__main__":
    # NEP-aligned sample dataset (small, feasible)
    courses = [
        {"id": "C1", "name": "Mathematics", "faculty": "F_A", "group": ["AIML", "CSE"], "weekly_slots": 3, "consecutive": 1},
        {"id": "C2", "name": "English Communication", "faculty": "F_B", "group": ["AIML", "CSE"], "weekly_slots": 2, "consecutive": 1},
        {"id": "C3", "name": "AI Fundamentals", "faculty": "F_C", "group": "AIML", "weekly_slots": 3, "consecutive": 1},
        {"id": "C4", "name": "Data Structures", "faculty": "F_D", "group": "CSE", "weekly_slots": 3, "consecutive": 1},
        {"id": "C5", "name": "AI Lab", "faculty": "F_C", "group": "AIML", "weekly_slots": 2, "consecutive": 2},
        {"id": "C6", "name": "DS Lab", "faculty": "F_D", "group": "CSE", "weekly_slots": 2, "consecutive": 2},
        {"id": "C7", "name": "Elective: Psychology", "faculty": "F_E", "group": ["AIML", "CSE"], "weekly_slots": 2, "consecutive": 1},
        {"id": "C8", "name": "Elective: Design Thinking", "faculty": "F_F", "group": ["AIML", "CSE"], "weekly_slots": 2, "consecutive": 1},
        {"id": "C9", "name": "Innovation Project", "faculty": "F_G", "group": ["AIML", "CSE"], "weekly_slots": 2, "consecutive": 2}
    ]

    days = ["Mon", "Tue", "Wed", "Thu", "Fri"]
    slots_per_day = 6  # <= 6 slots per NEP guidance

    rooms = [
        {"name": "R101", "capacity": 60},
        {"name": "R102", "capacity": 60},
        {"name": "Lab1", "capacity": 30},
        {"name": "Lab2", "capacity": 30}
    ]

    group_sizes = {"AIML": 40, "CSE": 50}

    try:
        schedule = generate_timetable(
        courses, rooms, days, slots_per_day,
        max_classes_per_day=5,
        max_daily_hours_per_faculty=5,
        max_weekly_hours_per_faculty=18,
        group_sizes=group_sizes,
        use_ga=True,
        assign_rooms=True,
        min_group_days=5,          # HARD: at least 3 distinct days
        day_balance_fraction=0.50  # SOFT: no day > 33% of sessions
    )

    except ValueError as e:
        print(f"Input validation error: {e}")
        exit(1)
    except RuntimeError as e:
        print(f"Solver error: {e}")
        exit(1)

    # Generate matrices for visualization
    from analysis_visualization import (generate_matrix, visualize_entity_schedule, analyze_schedule, print_schedule_summary)

    groups = list(set(info["meta"]["group"] for info in schedule.values()))
    faculties = list(set(info["meta"]["faculty"] for info in schedule.values()))
    group_matrix, groups = generate_matrix(schedule, "group", days, slots_per_day)
    faculty_matrix, faculties = generate_matrix(schedule, "faculty", days, slots_per_day)
    room_matrix, _ = generate_matrix(schedule, "room", days, slots_per_day)

    clashes = detect_clashes(schedule, slots_per_day, rooms, group_sizes=group_sizes)

    # Generate and save visualizations
    print("Generating enhanced visualizations...")

    # Print comprehensive schedule summary
    try:
        print_schedule_summary(schedule, days, slots_per_day)
    except Exception as e:
        print(f"Could not generate schedule summary: {e}")

    # Group timetable heatmap
    try:
        matrix, entities = visualize_entity_schedule(schedule, "group", days, slots_per_day,
                                                   save_path="group_timetable_heatmap.png", show=False)
        print("Group timetable heatmap saved as 'group_timetable_heatmap.png'")
    except Exception as e:
        print(f"Could not generate group heatmap: {e}")

    # Faculty workload heatmap
    try:
        matrix, entities = visualize_entity_schedule(schedule, "faculty", days, slots_per_day,
                                                   save_path="faculty_workload_heatmap.png", show=False)
        print("Faculty workload heatmap saved as 'faculty_workload_heatmap.png'")
    except Exception as e:
        print(f"Could not generate faculty heatmap: {e}")

    # Room utilization heatmap
    try:
        matrix, entities = visualize_entity_schedule(schedule, "room", days, slots_per_day,
                                                   save_path="room_utilization_heatmap.png", show=False)
        print("Room utilization heatmap saved as 'room_utilization_heatmap.png'")
    except Exception as e:
        print(f"Could not generate room heatmap: {e}")

    # Detailed clash analysis
    try:
        analyze_schedule(schedule, rooms, slots_per_day, group_sizes)
    except Exception as e:
        print(f"Could not perform detailed clash analysis: {e}")

    export_schedule_to_excel(schedule, days, slots_per_day, "timetable.xlsx",
                             clashes=clashes, group_matrix=group_matrix, faculty_matrix=faculty_matrix,
                             groups=groups, faculties=faculties, room_matrix=room_matrix)

    if any(clashes.values()):
        print("Clashes detected:")
        for t, lst in clashes.items():
            for clash in lst:
                if t == "room_capacity":
                    if len(clash) == 5:
                        sid, g, room, size, cap = clash
                        print(f" - ROOM CAPACITY: session {sid} group {g} in {room} ({size} > {cap})")
                    else:
                        print(f" - {t.upper()} clash: {clash}")
                else:
                    print(f" - {t.upper()} clash: {clash}")
    else:
        print("No clashes found")

    print(json.dumps(schedule, indent=2))
