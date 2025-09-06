#!/usr/bin/env python3
"""
ScheduleAI - Quick Example Script

This script demonstrates how to use the ScheduleAI timetable generator
with a small example dataset.
"""

import sys
import os

# Add current directory to path for imports
current_dir = os.path.dirname(__file__)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Import the main workflow function
import hybrid_timetable as ht

def main():
    """Run a quick timetable generation example."""

    print("🎯 ScheduleAI - Hybrid Timetable Generator")
    print("=" * 50)

    # Sample courses (NEP-2020 compliant)
    courses = [
        {
            "id": "CS101",
            "name": "Data Structures",
            "faculty": "Dr. Smith",
            "group": ["CSE", "AIML"],
            "weekly_slots": 3,
            "consecutive": 1
        },
        {
            "id": "CS102",
            "name": "Algorithms",
            "faculty": "Dr. Johnson",
            "group": "CSE",
            "weekly_slots": 3,
            "consecutive": 1
        },
        {
            "id": "AI101",
            "name": "Machine Learning",
            "faculty": "Dr. Davis",
            "group": "AIML",
            "weekly_slots": 3,
            "consecutive": 1
        },
        {
            "id": "CS201",
            "name": "Database Systems",
            "faculty": "Dr. Wilson",
            "group": ["CSE", "AIML"],
            "weekly_slots": 2,
            "consecutive": 1
        },
        {
            "id": "LAB101",
            "name": "Programming Lab",
            "faculty": "Dr. Smith",
            "group": "CSE",
            "weekly_slots": 2,
            "consecutive": 2
        }
    ]

    # Sample rooms
    rooms = [
        {"name": "R101", "capacity": 60},
        {"name": "R102", "capacity": 60},
        {"name": "Lab1", "capacity": 30},
        {"name": "Lab2", "capacity": 30}
    ]

    # Configuration
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    slots_per_day = 6  # NEP-2020: ≤6 slots per day
    group_sizes = {"CSE": 50, "AIML": 40}

    print(f"📚 Courses: {len(courses)}")
    print(f"🏫 Rooms: {len(rooms)}")
    print(f"👥 Groups: {len(group_sizes)}")
    print(f"📅 Days: {len(days)}")
    print(f"⏰ Slots/Day: {slots_per_day}")
    print()

    # Generate timetable
    print("🔧 Generating timetable...")
    result = ht.run_timetable_workflow(
        courses=courses,
        rooms=rooms,
        days=days,
        slots_per_day=slots_per_day,
        group_sizes=group_sizes,
        show_plots=False  # Set to True to display plots
    )

    # Print results
    if result["success"]:
        print("\n✅ Timetable generated successfully!")
        print(f"📊 Total sessions: {result['metrics']['total_sessions']}")
        print(f"🏫 Room utilization: {result['metrics']['utilization_rate']:.1f}%")
        print(f"⚠️ Clashes detected: {result['metrics']['clash_count']}")

        if result["files"]["excel"]:
            print(f"📄 Excel report: {result['files']['excel']}")

        if result["files"]["visualizations"]:
            print(f"🖼️ Visualizations: {len(result['files']['visualizations'])} files")
            for viz in result["files"]["visualizations"]:
                print(f"   • {viz}")

        print("\n🎉 Example completed! Check the generated files.")
    else:
        print(f"❌ Generation failed: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main()
