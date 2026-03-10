import time
import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PIPE_FILE = os.path.join(BASE_DIR, "pipes", "inventory_pipe.txt")
OUTPUT_FILE = os.path.join(BASE_DIR, "data", "low_inventory.json")


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

            # Gather low inventory items
            low_inventory_list = [
                item for item in inventory_data if int(
                    item.get(
                        "quantity",
                        0)) <= int(
                    item.get(
                        "restock threshold",
                        0))]

            time.sleep(2)
            write_to_json_file(OUTPUT_FILE, low_inventory_list)

            time.sleep(2)
            write_to_txt_file(PIPE_FILE, f"done\n{OUTPUT_FILE}")


def read_json_file(json_path):
    with open(json_path, "r") as f:
        return json.load(f)


def read_txt_file(txt_path):
    with open(txt_path, "r") as f:
        return f.readlines()


def write_to_txt_file(txt_path, string):
    with open(txt_path, "w") as f:
        f.write(string)


def write_to_json_file(json_path, data):
    with open(json_path, "w") as f:
        json.dump(data, f, indent=2)


if __name__ == "__main__":
    while True:
        main()
        time.sleep(1)
