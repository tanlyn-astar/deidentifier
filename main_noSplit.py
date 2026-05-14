import html
import os
import pandas as pd

input_folder = "./input/3_100 gold standard files"
output_folder = "./output"

os.makedirs(output_folder, exist_ok=True)

# wipe the output folder (not subfolders) before beginning
for f in os.listdir(output_folder):
    fpath = os.path.join(output_folder, f)
    if os.path.isfile(fpath):
        os.remove(fpath)

START_MARKER = "********** Start of Report **********"
END_MARKER = "********** End of Report **********"


def parse_reports(text):
    reports = []
    segments = text.split(START_MARKER)
    for segment in segments[1:]:
        content = segment.split(END_MARKER)[0].strip()
        if content:
            reports.append(content)
    return reports


report_id = 1
tracker_rows = []
all_rows = []

for filename in sorted(os.listdir(input_folder)):
    if not filename.lower().endswith(".txt"):
        continue

    filepath = os.path.join(input_folder, filename)
    with open(filepath, encoding="utf-8", errors="replace") as f:
        content = f.read()

    content = html.unescape(content)
    content = content.replace('"', "'")

    EXCEL_CELL_LIMIT = 32000
    chunks = [content[i:i + EXCEL_CELL_LIMIT] for i in range(0, len(content), EXCEL_CELL_LIMIT)]
    num_records = len(chunks)

    rows = []
    for chunk in chunks:
        row = {"Id": report_id, "Notes": chunk, "PatientMRN": "", "PatientName": "", "PatientPhone": "", "PatientDateOfBirth": ""}
        rows.append(row)
        all_rows.append(row)
        tracker_rows.append({"Id": report_id, "Filename": filename, "Records per file": num_records, "Reviewed by": "", "Status": "", "Comments": ""})
        report_id += 1

    out_name = os.path.splitext(filename)[0] + ".csv"
    out_path = os.path.join(output_folder, out_name)

    with open(out_path, "w", encoding="utf-8-sig", newline="") as f:
        f.write('"Id","Notes","PatientMRN","PatientName","PatientPhone","PatientDateOfBirth"\r\n')
        for row in rows:
            f.write(f'"{row["Id"]}","{row["Notes"]}","",""\r\n')

    print(f"{filename}: {num_records} record(s) -> {out_name}")

with open(os.path.join(output_folder, "all_reports.csv"), "w", encoding="utf-8-sig", newline="") as f:
    f.write('"Id","Notes","PatientMRN","PatientName"\r\n')
    for row in all_rows:
        f.write(f'"{row["Id"]}","{row["Notes"]}","",""\r\n')
print(f"Collated CSV written: {len(all_rows)} total reports")

tracker_df = pd.DataFrame(tracker_rows, columns=["Id", "Filename", "Records per file", "Reviewed by", "Status", "Comments"])
tracker_df.to_excel(os.path.join(output_folder, "Report Tracker.xlsx"), index=False)
print(f"Tracker written: {len(tracker_rows)} total reports")
