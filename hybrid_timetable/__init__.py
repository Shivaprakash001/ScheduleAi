"""
ScheduleAI - Hybrid Timetable Generator

A sophisticated timetable generation system that combines OR-Tools CP-SAT solver
with Genetic Algorithms to create optimal academic schedules.
"""

from .timetable_generator import generate_timetable
from .utils.clashes import detect_clashes
from .utils.excel_export import export_schedule_to_excel
from .room_assignment import greedy_room_assignment

__all__ = [
    "generate_timetable",
    "detect_clashes",
    "export_schedule_to_excel",
    "greedy_room_assignment"
]
