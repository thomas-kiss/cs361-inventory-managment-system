import time
import json
import csv
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PIPE_FILE = os.path.join(BASE_DIR, "pipes", "csv_pipe.txt")
CSV_DIR = os.path.join(BASE_DIR, "csv")


def main():
    pipe_msg = read_txt_file(PIPE_FILE)
    if pipe_msg:
        if pipe_msg[0].strip() == "run":
            inventory_path = pipe_msg[1].strip()

            if not os.path.isabs(inventory_path):
                inventory_path = os.path.normpath(
                    os.path.join(BASE_DIR, inventory_path))
            else:
                inventory_path = os.path.normpath(inventory_path)

            inventory_path = os.path.abspath(inventory_path)

            inventory_data = read_json_file(inventory_path)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_filename = f"inventory_export_{timestamp}.csv"
            csv_path = os.path.join(CSV_DIR, csv_filename)

            if inventory_data:
                try:
                    os.makedirs(CSV_DIR, exist_ok=True)
                    with open(
                        csv_path, "w", newline="", encoding="utf-8"
                    ) as csv_file:
                        fieldnames = list(inventory_data[0].keys())
                        writer = csv.DictWriter(
                            csv_file, fieldnames=fieldnames)
                        writer.writeheader()
                        writer.writerows(inventory_data)
                except Exception as e:
                    write_to_txt_file(PIPE_FILE, f"error\n{str(e)}")
                    return

                time.sleep(2)
                write_to_txt_file(PIPE_FILE, f"done\n{csv_path}")
            else:
                write_to_txt_file(PIPE_FILE, "done\n")


def read_json_file(json_path):
    with open(json_path, "r") as f:
        return json.load(f)


def read_txt_file(txt_path):
    with open(txt_path, "r") as f:
        return f.readlines()


def write_to_txt_file(txt_path, string):
    with open(txt_path, "w") as f:
        f.write(string)


if __name__ == "__main__":
    while True:
        main()
        time.sleep(1)
