# ScheduleAI - Hybrid Timetable Generator

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![OR-Tools](https://img.shields.io/badge/OR--Tools-9.14+-orange.svg)](https://developers.google.com/optimization)
[![Smart India Hackathon](https://img.shields.io/badge/Smart%20India-Hackathon-blue.svg)](https://sih.gov.in/)

A sophisticated timetable generation system that combines **OR-Tools CP-SAT solver** with **Genetic Algorithms** to create optimal academic schedules compliant with NEP-2020 guidelines.

**🏆 Smart India Hackathon 2025 Project** - Team of 6 developers

## 👥 Team

This project is developed by a team of 6 talented developers participating in Smart India Hackathon 2025:

- **Shiva Prakash** (spchidiri2006@gmail.com) - Project Lead & AI/ML Engineer
- Team Member 2 - [Role]
- Team Member 3 - [Role]
- Team Member 4 - [Role]
- Team Member 5 - [Role]
- Team Member 6 - [Role]

## 🎯 Features

### Core Capabilities
- **Hybrid Optimization**: OR-Tools for hard constraints + Genetic Algorithm for soft metrics
- **NEP-2020 Compliance**: ≤6 slots per day, balanced workload distribution
- **Multi-entity Scheduling**: Groups, faculties, and rooms with capacity management
- **Conflict Detection**: Comprehensive clash analysis for faculty, group, and room conflicts
- **Room Assignment**: Intelligent capacity-aware room allocation

### Advanced Features
- **Professional Visualizations**: Heatmaps for schedule analysis
- **Excel Export**: Multi-sheet reports with clash highlighting
- **Flexible Configuration**: Customizable constraints and optimization parameters
- **Real-time Analysis**: Detailed clash reports and utilization metrics

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/Shivaprakash001/ScheduleAi.git
cd ScheduleAi

# Install dependencies
pip install -r requirements.txt
# or using uv (if available)
uv sync
```

### Basic Usage

```python
from hybrid_timetable import run_timetable_workflow

# Define your courses
courses = [
    {
        "id": "CS101",
        "name": "Data Structures",
        "faculty": "Dr. Smith",
        "group": ["CSE", "AIML"],
        "weekly_slots": 3,
        "consecutive": 1
    }
]

# Define rooms and groups
rooms = [
    {"name": "R101", "capacity": 60},
    {"name": "Lab1", "capacity": 30}
]

days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
group_sizes = {"CSE": 50, "AIML": 40}

# Generate timetable
result = run_timetable_workflow(
    courses=courses,
    rooms=rooms,
    days=days,
    slots_per_day=6,
    group_sizes=group_sizes
)

print(f"✅ Generated schedule with {result['metrics']['total_sessions']} sessions")
```

## 📁 Project Structure

```
scheduleai/
├── hybrid_timetable/
│   ├── __init__.py
│   ├── timetable_generator.py    # Main generation logic
│   ├── room_assignment.py        # Room allocation algorithms
│   ├── ortools_solver/
│   │   └── solver.py            # CP-SAT constraint modeling
│   ├── ga_module/
│   │   ├── ga_setup.py          # Genetic algorithm configuration
│   │   └── fitness.py           # Fitness function definitions
│   └── utils/
│       ├── helpers.py           # Utility functions
│       ├── clashes.py           # Conflict detection
│       └── excel_export.py      # Excel report generation
├── analysis_visualization.py     # Visualization and analysis tools
├── hybrid_timetable.py          # Main workflow orchestrator
├── requirements.txt             # Python dependencies
├── pyproject.toml               # Project configuration
└── README.md
```

## 🔧 Configuration Options

### Timetable Parameters

```python
timetable_params = {
    # Basic settings
    "courses": courses,
    "rooms": rooms,
    "days": ["Mon", "Tue", "Wed", "Thu", "Fri"],
    "slots_per_day": 6,

    # Constraints
    "max_classes_per_day": 5,
    "max_daily_hours_per_faculty": 5,
    "max_weekly_hours_per_faculty": 18,
    "group_sizes": {"CSE": 50, "AIML": 40},

    # Optimization
    "use_ga": True,
    "assign_rooms": True,
    "min_group_days": 3,
    "day_balance_fraction": 0.4
}
```

### Course Definition Format

```python
course = {
    "id": "CS101",                    # Unique course identifier
    "name": "Data Structures",        # Full course name
    "faculty": "Dr. Smith",           # Faculty member
    "group": ["CSE", "AIML"],         # Target groups (can be list or string)
    "weekly_slots": 3,                # Number of sessions per week
    "consecutive": 1                  # Max consecutive slots (1 for theory, 2 for labs)
}
```

## 📊 Analysis & Visualization

The system provides comprehensive analysis tools:

```python
from analysis_visualization import (
    visualize_entity_schedule,
    analyze_schedule,
    print_schedule_summary
)

# Generate heatmaps
visualize_entity_schedule(schedule, "group", days, slots_per_day,
                         save_path="group_heatmap.png")

visualize_entity_schedule(schedule, "faculty", days, slots_per_day,
                         save_path="faculty_heatmap.png")

# Analyze clashes
clashes = analyze_schedule(schedule, rooms, slots_per_day, group_sizes)

# Print summary
print_schedule_summary(schedule, days, slots_per_day)
```

## 🎯 Optimization Objectives

### Hard Constraints (Must be satisfied)
- No faculty double-booking
- No group double-booking
- Room capacity limits
- Course weekly slot requirements
- Consecutive slot limits
- NEP-2020 compliance (≤6 slots/day)

### Soft Constraints (Optimized)
- Day balance across groups
- Faculty workload distribution
- Gap minimization
- Room utilization efficiency

## 📈 Performance Metrics

The system tracks key performance indicators:

- **Total Sessions**: Number of scheduled sessions
- **Utilization Rate**: Percentage of time slots used
- **Clash Count**: Number of constraint violations
- **Balance Score**: Distribution quality across days/groups

## 🔍 API Reference

### Main Functions

#### `run_timetable_workflow()`
Complete end-to-end timetable generation pipeline.

**Parameters:**
- `courses`: List of course dictionaries
- `rooms`: List of room dictionaries
- `days`: List of day names
- `slots_per_day`: Number of time slots per day
- `group_sizes`: Dictionary of group sizes
- `**kwargs`: Additional configuration options

**Returns:** Dictionary with schedule, metrics, and file paths

#### `generate_timetable()`
Core timetable generation function.

#### `detect_clashes()`
Comprehensive conflict analysis.

#### `export_schedule_to_excel()`
Multi-sheet Excel report generation.

## 🧪 Example Datasets

The repository includes NEP-2020 compliant example datasets:

```python
# Small dataset for testing
from hybrid_timetable import run_timetable_workflow

# Sample data is included in hybrid_timetable.py
result = run_timetable_workflow(
    courses=sample_courses,
    rooms=sample_rooms,
    days=["Mon", "Tue", "Wed", "Thu", "Fri"],
    slots_per_day=6,
    group_sizes={"CSE": 50, "AIML": 40}
)
```

## 📊 Generated Outputs

When you run the system, it generates comprehensive visualizations and reports:

### Visualizations
- **Faculty Workload Heatmap** - Shows teacher scheduling distribution across days
- **Group Timetable Heatmap** - Visualizes student group schedules with time slots
- **Room Utilization Heatmap** - Displays room usage patterns and capacity analysis

### Reports
- **Excel Report** (`timetable.xlsx`) - Multi-sheet report with:
  - Master timetable with room assignments
  - Group-wise schedules
  - Faculty-wise schedules
  - Clash analysis summary
  - Embedded charts and formatting

### Sample Output Structure
```
📁 Generated Files:
├── faculty_workload_heatmap.png     # Teacher workload visualization
├── group_timetable_heatmap.png      # Student group schedules
├── room_utilization_heatmap.png     # Room usage analysis
└── timetable.xlsx                   # Complete Excel report
```

### Running the System
```bash
# Generate visualizations and reports
python hybrid_timetable.py

# Or run the example script
python example.py
```

**Note:** The system generates these files in the current directory for immediate viewing and analysis.

## 🛠️ Development

### Local Development Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run the example
python example.py

# Run the main script
python hybrid_timetable.py
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google OR-Tools**: For the powerful constraint programming solver
- **DEAP**: For genetic algorithm framework
- **NEP-2020**: For modern educational guidelines
- **Open-source community**: For amazing libraries and tools

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/Shivaprakash001/ScheduleAi/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Shivaprakash001/ScheduleAi/discussions)
- **Email**: spchidiri2006@gmail.com

---

**Made with ❤️ for educational institutions**

*Optimize your academic scheduling with AI-powered precision!*
