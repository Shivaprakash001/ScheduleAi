from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.cell import MergedCell

from .clashes import highlight_clashes

def export_schedule_to_excel(schedule, days, slots_per_day, filename="timetable.xlsx",
                             time_labels=None, semester_name="Semester II",
                             clashes=None, group_matrix=None, faculty_matrix=None,
                             groups=None, faculties=None, room_matrix=None):
    wb = Workbook()

    def write_matrix(ws, matrix, labels, start_row=2, start_col=2):
        # Write labels
        for i, label in enumerate(labels):
            ws.cell(row=start_row + i, column=start_col - 1, value=label)
        # Write matrix
        for i, row in enumerate(matrix):
            for j, val in enumerate(row):
                ws.cell(row=start_row + i, column=start_col + j, value=int(val))

    if time_labels is None:
        time_labels = [f"{9+i}:00 - {10+i}:00" for i in range(slots_per_day)]

    def make_sheet(ws, schedule_subset, title, subtitle=None):
        ws.title = title
        ws.merge_cells(start_row=1, end_row=1, start_column=1, end_column=len(days)+1)
        cell = ws.cell(row=1, column=1, value=subtitle or title)
        cell.font = Font(bold=True, size=14)
        cell.alignment = Alignment(horizontal="center")
        ws.cell(row=2, column=1, value="Slot/Day").font = Font(bold=True)
        for j, day in enumerate(days, start=2):
            ws.cell(row=2, column=j, value=day).font = Font(bold=True)
        for slot in range(slots_per_day):
            ws.cell(row=slot + 3, column=1, value=f"Slot {slot+1}\n{time_labels[slot]}")
        for sess_id, info in sorted(schedule_subset.items(), key=lambda x: x[1]["start"]):
            start = info["start"]
            room = info["room"]
            meta = info["meta"]
            length = info["length"]
            day_idx = start // slots_per_day
            slot_idx = start % slots_per_day
            text = f"{meta['name']} ({meta['faculty']})\n{room}\n{meta['group']}"
            r1 = slot_idx + 3
            r2 = r1 + length - 1
            c = day_idx + 2
            if length > 1:
                try:
                    ws.unmerge_cells(start_row=r1, end_row=r2, start_column=c, end_column=c)
                except Exception:
                    pass
                ws.merge_cells(start_row=r1, end_row=r2, start_column=c, end_column=c)
            cell = ws.cell(row=r1, column=c)
            if isinstance(cell, MergedCell):
                for merge_range in ws.merged_cells.ranges:
                    if r1 >= merge_range.min_row and r1 <= merge_range.max_row and \
                       c >= merge_range.min_col and c <= merge_range.max_col:
                        cell = ws.cell(row=merge_range.min_row, column=merge_range.min_col)
                        break
                else:
                    cell = ws._cells.get((r1, c), ws.cell(row=r1, column=c))
            cell.value = text
            cell.alignment = Alignment(wrap_text=True, horizontal="center", vertical="center")
            cname = meta['name'].lower()
            if "lab" in cname or "project" in cname:
                cell.fill = PatternFill(start_color="FFD9E6", end_color="FFD9E6", fill_type="solid")
            elif "elective" in cname:
                cell.fill = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")
            else:
                cell.fill = PatternFill(start_color="E6F3FF", end_color="E6F3FF", fill_type="solid")
        for col in ws.columns:
            max_len = 0
            col_letter = None
            for cell in col:
                if col_letter is None:
                    if isinstance(cell, MergedCell):
                        continue
                    col_letter = cell.column_letter
                try:
                    if cell.value:
                        max_len = max(max_len, len(str(cell.value)))
                except:
                    pass
            if col_letter:
                ws.column_dimensions[col_letter].width = max_len + 4

    ws_master = wb.active
    make_sheet(ws_master, schedule, "Master", subtitle=f"{semester_name} - Master Timetable")
    if room_matrix is not None:
        highlight_clashes(ws_master, room_matrix)
    groups = {info["meta"]["group"] for info in schedule.values()}
    for g in groups:
        ws = wb.create_sheet(title=f"Group_{g}")
        subset = {sid: info for sid, info in schedule.items() if info["meta"]["group"] == g}
        make_sheet(ws, subset, f"Group_{g}", subtitle=f"{semester_name} - {g}")
    faculties = {info["meta"]["faculty"] for info in schedule.values()}
    for f in faculties:
        ws = wb.create_sheet(title=f"Faculty_{f}")
        subset = {sid: info for sid, info in schedule.items() if info["meta"]["faculty"] == f}
        make_sheet(ws, subset, f"Faculty_{f}", subtitle=f"{semester_name} - {f}")

    # Add clash analysis sheet
    if clashes:
        ws_clash = wb.create_sheet(title="Clash Analysis")
        ws_clash.cell(row=1, column=1, value="Clash Analysis Report").font = Font(bold=True, size=14)
        row = 3
        for clash_type, clash_list in clashes.items():
            if clash_list:
                ws_clash.cell(row=row, column=1, value=f"{clash_type.upper()} clashes:").font = Font(bold=True)
                row += 1
                for item in clash_list:
                    ws_clash.cell(row=row, column=1, value=str(item))
                    row += 1
            else:
                ws_clash.cell(row=row, column=1, value=f"No {clash_type} clashes detected.")
                row += 1
            row += 1

    try:
        wb.save(filename)
        print(f"✅ Timetable exported to {filename}")
    except Exception as e:
        print(f"Error while saving to Excel: {e}")
        input("Press Enter to exit...")
        export_schedule_to_excel(schedule, days, slots_per_day, filename)
