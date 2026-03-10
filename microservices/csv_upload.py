import csv
import json
import time
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PIPE_FILE = os.path.join(BASE_DIR, "pipes", "csv_upload_pipe.txt")
INVENTORY_FILE = os.path.join(BASE_DIR, "data", "inventory.json")
OUTPUT_FILE = os.path.join(BASE_DIR, "data", "updated_inventory.json")


def read_txt_file(path):
    with open(path, "r") as f:
        return f.readlines()


def write_txt_file(path, content):
    with open(path, "w") as f:
        f.write(content)


def read_inventory(path):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def write_inventory(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def process_csv_upload():
    pipe_lines = read_txt_file(PIPE_FILE)
    if not pipe_lines or pipe_lines[0].strip() != "run":
        return

    csv_path = pipe_lines[1].strip()

    if not os.path.isabs(csv_path):
        if not csv_path.startswith("csv" + os.sep):
            csv_path = os.path.join(BASE_DIR, "csv", csv_path)
        else:
            csv_path = os.path.join(BASE_DIR, csv_path)

    inventory = read_inventory(INVENTORY_FILE)
    inventory_by_sku = {item.get("sku", ""): item for item in inventory}

    try:
        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            expected_columns = [
                "name",
                "sku",
                "quantity",
                "restock threshold",
                "size",
                "material",
                "location",
                "cost"]
            if any(col not in reader.fieldnames for col in expected_columns):
                raise ValueError(
                    "CSV missing required columns. "
                    f"Required: {expected_columns}"
                )

            for row in reader:
                sku = row.get("sku", "").strip()
                if not sku:
                    continue  # skip rows without SKU

                # Update existing or add new
                if sku in inventory_by_sku:
                    inventory_by_sku[sku].update(row)
                else:
                    inventory_by_sku[sku] = row

        updated_inventory = list(inventory_by_sku.values())
        write_inventory(OUTPUT_FILE, updated_inventory)

        # Write success response to pipe
        write_txt_file(PIPE_FILE, f"done\n{OUTPUT_FILE}\n")

    except Exception as e:
        write_txt_file(PIPE_FILE, f"error\n{str(e)}\n")


if __name__ == "__main__":
    while True:
        process_csv_upload()
        time.sleep(2)
