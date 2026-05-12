import os
import pandas as pd

input_folder = "./input/2_100 original files"
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

    reports = parse_reports(content)
    if not reports:
        print(f"No reports found in {filename}")
        continue

    rows = []
    for report in reports:
        row = {"Id": report_id, "Notes": report, "PatientMRN": "", "PatientName": ""}
        rows.append(row)
        all_rows.append(row)
        tracker_rows.append({"Id": report_id, "Filename": filename, "Reports in file": len(reports), "Benchmarked?": "", "Status": "", "Comments": ""})
        report_id += 1

    out_name = os.path.splitext(filename)[0] + ".csv"
    out_path = os.path.join(output_folder, out_name)

    df = pd.DataFrame(rows, columns=["Id", "Notes", "PatientMRN", "PatientName"])
    df.to_csv(out_path, index=False, encoding="utf-8")

    print(f"{filename}: {len(reports)} report(s) -> {out_name}")

pd.DataFrame(all_rows, columns=["Id", "Notes", "PatientMRN", "PatientName"]).to_csv(
    os.path.join(output_folder, "all_reports.csv"), index=False, encoding="utf-8"
)
print(f"Collated CSV written: {len(all_rows)} total reports")

tracker_df = pd.DataFrame(tracker_rows, columns=["Id", "Filename", "Reports in file", "Benchmarked?", "Status", "Comments"])
tracker_df.to_excel(os.path.join(output_folder, "Report Tracker.xlsx"), index=False)
print(f"Tracker written: {len(tracker_rows)} total reports")
