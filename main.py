import os
import json
import time

INVENTORY_FILE = "data/inventory.json"


class InventoryApp:
    def __init__(self):
        self.inventory = self.load_inventory()

    def clear(self):
        os.system("cls" if os.name == "nt" else "clear")

    def pause(self):
        input("\nPress Enter to return to Main Menu...")

    def load_inventory(self):
        try:
            with open(INVENTORY_FILE, "r") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save_inventory(self):
        with open(INVENTORY_FILE, "w") as file:
            json.dump(self.inventory, file, indent=2)
        print(f"\nInventory saved to {INVENTORY_FILE}.")

    def normalize_path(self, input_path, base_folder):
        input_path = input_path.strip()
        base_folder_with_sep = base_folder + os.sep
        # Remove duplicate base folder prefix if present
        if input_path.startswith(base_folder_with_sep):
            input_path = input_path[len(base_folder_with_sep):]
        # If relative, prepend base folder
        if not os.path.isabs(input_path):
            input_path = os.path.join(base_folder, input_path)
        # Normalize path to clean redundant separators etc.
        return os.path.normpath(input_path)

    # UI
    def title_screen(self):
        self.clear()
        print("############################################")
        print("#                                          #")
        print("#      Inventory Management Application    #")
        print("#          Created by Alex Kiss            #")
        print("#                                          #")
        print("############################################\n")
        input("Press Enter to continue...")

    def display_table(self, data):
        if not data:
            print("No items in inventory.")
            return

        headers = [
            "#",
            "Name",
            "SKU",
            "Qty",
            "Threshold",
            "Size",
            "Material",
            "Location",
            "Cost"]
        col_widths = [5, 40, 8, 10, 10, 30, 12, 12, 8]

        header_row = "".join(
            f"{headers[i]:<{col_widths[i]}}" for i in range(
                len(headers)))
        print(header_row)
        print("-" * len(header_row))

        for idx, item in enumerate(data):
            row = [
                str(idx + 1),
                item.get("name", "")[:39],
                item.get("sku", ""),
                str(item.get("quantity", "")),
                str(item.get("restock threshold", "")),
                item.get("size", ""),
                item.get("material", ""),
                item.get("location", ""),
                str(item.get("cost", ""))
            ]
            print(
                "".join(
                    f"{row[i]:<{col_widths[i]}}" for i in range(
                        len(row))))

    def exit_program(self):
        self.clear()
        print("====== EXIT PROGRAM ======")
        print("[1] Confirm and Exit Program")
        print("[2] Return to Main Menu")
        return input("Select an option: ") == "1"

    # CRUD
    def add_inventory(self):
        self.clear()
        print("====== ADD A NEW INVENTORY ITEM ======")
        print("(Type 'cancel' anytime to return to Main Menu)\n")
        fields = [
            'name',
            'sku',
            'quantity',
            'restock threshold',
            'size',
            'material',
            'location',
            'cost']
        item = {}
        for field in fields:
            value = input(f"Enter {field.replace('_', ' ').title()}: ").strip()
            if value.lower() == 'cancel':
                return
            item[field] = value

        self.clear()
        print("You entered:")
        for key, val in item.items():
            print(f"{key.title()}: {val}")
        if input("\nSave this item? (y/n): ").lower() == 'y':
            self.inventory.append(item)
            print("Item saved.")
        else:
            print("Item discarded.")
        self.pause()

    def view_inventory(self):
        self.clear()
        print("====== VIEW ALL INVENTORY ======\n")
        self.display_table(self.inventory)
        self.pause()

    def search_inventory(self):
        self.clear()
        print("====== SEARCH INVENTORY ======")
        term = input("Search: ").lower()
        results = [
            item for item in self.inventory if term in item.get(
                'name', '').lower()]
        self.clear()
        print("====== SEARCH RESULTS ======\n")
        self.display_table(results)
        if results:
            print("\n[1] Edit or Delete an Item (by result number)")
            print("[2] Return to Main Menu")
            option = input("Select an option: ")
            if option == "1":
                idx = int(input("Enter item number to manage: ")) - 1
                if 0 <= idx < len(results):
                    self.manage_item(results[idx])
        self.pause()

    def manage_inventory(self):
        self.clear()
        print("====== MANAGE INVENTORY ======\n")
        if not self.inventory:
            print("Inventory is empty.")
            self.pause()
            return
        self.display_table(self.inventory)
        print("\n[1] Edit or Delete an Item (by list number)")
        print("[2] Search for an Item")
        print("[3] Return to Main Menu")
        choice = input("Select an option: ")
        if choice == "1":
            idx = int(input("Enter the Inventory List Item Number: ")) - 1
            if 0 <= idx < len(self.inventory):
                self.manage_item(self.inventory[idx])
        elif choice == "2":
            self.search_inventory()

    def manage_item(self, item):
        print("\nSelected:")
        for k, v in item.items():
            print(f"{k.title()}: {v}")
        print("\n[1] Edit this item")
        print("[2] Delete this item")
        print("[3] Cancel")
        choice = input("Select an option: ")
        if choice == "1":
            self.edit_item(item)
        elif choice == "2":
            self.delete_item(item)

    def edit_item(self, item):
        print("====== EDIT ITEM ======")
        print("Press Enter to keep the current value.")
        for key in item:
            old = item[key]
            new = input(f"{key.title()} ({old}): ").strip()
            if new:
                item[key] = new
        print("\nUpdated values:")
        for key, val in item.items():
            print(f"{key.title()}: {val}")
        if input("Save changes? (y/n): ").lower() != 'y':
            print("Changes discarded.")

    def delete_item(self, item):
        self.clear()
        print("====== DELETE ITEM ======\n")
        for k, v in item.items():
            print(f"{k.title()}: {v}")
        print("\n[1] I want to permanently delete the item.")
        print("[2] Return to Main Menu")
        choice = input("Select an option: ")
        if choice == "1":
            self.inventory.remove(item)
            print("Item deleted.")

    def check_low_inventory(self):
        pipe_path = os.path.join("pipes", "inventory_pipe.txt")
        inventory_file = INVENTORY_FILE
        try:
            with open(pipe_path, "w") as pipe_file:
                pipe_file.write(f"run\n{inventory_file}\n")
        except Exception as e:
            print(f"Error writing to pipe file: {e}")
            self.pause()
            return
        print("Low inventory request sent. Waiting for response...")
        time.sleep(5)
        try:
            with open(pipe_path, "r") as pipe_file:
                lines = pipe_file.readlines()
        except Exception as e:
            print(f"Error reading from pipe file: {e}")
            self.pause()
            return
        if len(lines) >= 2 and lines[0].strip() == "done":
            low_inventory_path = lines[1].strip()
            # Normalize to data/ folder if missing
            if not low_inventory_path.startswith("data" + os.sep):
                low_inventory_path = self.normalize_path(
                    low_inventory_path, "data")
            try:
                with open(low_inventory_path, "r") as low_file:
                    low_inventory_data = json.load(low_file)
            except Exception as e:
                print(f"Error loading low inventory JSON: {e}")
                self.pause()
                return

            print("\n====== LOW INVENTORY REPORT ======\n")
            self.display_table(low_inventory_data)
        else:
            print(
                "Low inventory report is not ready or "
                "pipe file format incorrect."
            )
        self.pause()

    def save_inventory_to_csv(self):
        pipe_path = os.path.join("pipes", "csv_pipe.txt")
        inventory_file = INVENTORY_FILE
        try:
            with open(pipe_path, "w") as pipe_file:
                pipe_file.write(f"run\n{inventory_file}\n")
        except Exception as e:
            print(f"Error writing to CSV pipe: {e}")
            self.pause()
            return
        print("CSV save request sent. Waiting for response...")
        time.sleep(5)
        try:
            with open(pipe_path, "r") as pipe_file:
                lines = pipe_file.readlines()
        except Exception as e:
            print(f"Error reading from CSV pipe: {e}")
            self.pause()
            return
        if len(lines) >= 2:
            status = lines[0].strip()
            message = lines[1].strip()
            if status == "done":
                # Normalize path if it's a file path returned
                if not message.startswith(
                        "csvs" + os.sep) and os.path.isfile(message):
                    message = os.path.join("csvs", message)
                print(f"\nInventory successfully saved to CSV file: {message}")
            elif status == "error":
                print(f"\nCSV save error: {message}")
            else:
                print("\nUnexpected response from CSV microservice.")
        else:
            print("\nCSV save response not ready or invalid format.")
        self.pause()

    def check_inventory_value_report(self):
        pipe_path = os.path.join("pipes", "value_pipe.txt")
        inventory_file = INVENTORY_FILE
        try:
            with open(pipe_path, "w") as pipe_file:
                pipe_file.write(f"run\n{inventory_file}\n")
        except Exception as e:
            print(f"Error writing to pipe file: {e}")
            self.pause()
            return
        print("Inventory value report request sent. Waiting for response...")
        time.sleep(5)
        try:
            with open(pipe_path, "r") as pipe_file:
                lines = pipe_file.readlines()
        except Exception as e:
            print(f"Error reading from pipe file: {e}")
            self.pause()
            return

        if len(lines) >= 2 and lines[0].strip() == "done":
            report_path = lines[1].strip()
            if not report_path.startswith("data" + os.sep):
                report_path = self.normalize_path(report_path, "data")
            try:
                with open(report_path, "r") as report_file:
                    report_data = json.load(report_file)
            except Exception as e:
                print(f"Error loading value report JSON: {e}")
                self.pause()
                return
            print("\n====== INVENTORY VALUE REPORT ======\n")
            items = report_data.get('total_items', 'N/A')
            value = report_data.get('total_value', 'N/A')
            generated = report_data.get('report_generated', 'N/A')
            print(f"Total Items in Inventory: {items}")
            print(f"Total Inventory Value: ${value}")
            print(f"Report Generated At: {generated}")
        else:
            print(
                "Inventory value report is not ready or "
                "pipe file format incorrect."
            )
        self.pause()

    def upload_inventory_csv(self):
        pipe_path = os.path.join("pipes", "csv_upload_pipe.txt")
        self.clear()
        print("====== UPLOAD INVENTORY FROM CSV ======")
        csv_path = input(
            "Enter CSV file path to upload/update inventory: ").strip()

        # Normalize CSV path to csv folder if not absolute or already in csv/
        csv_path = self.normalize_path(csv_path, "csv")

        # Check if file exists before proceeding
        if not os.path.isfile(csv_path):
            print(f"CSV file not found: {csv_path}")
            self.pause()
            return

        try:
            with open(pipe_path, "w") as pipe_file:
                pipe_file.write(f"run\n{csv_path}\n")
        except Exception as e:
            print(f"Error writing to pipe file: {e}")
            self.pause()
            return

        print(
            "\nCSV upload request sent. "
            "Waiting for response from microservice..."
        )
        time.sleep(5)
        try:
            with open(pipe_path, "r") as pipe_file:
                lines = pipe_file.readlines()
        except Exception as e:
            print(f"Error reading from pipe file: {e}")
            self.pause()
            return
        if not lines:
            print("No response from microservice.")
            self.pause()
            return
        status = lines[0].strip()
        if status == "done":
            updated_inventory_path = lines[1].strip()
            if not updated_inventory_path.startswith("data" + os.sep):
                updated_inventory_path = self.normalize_path(
                    updated_inventory_path, "data")
            try:
                with open(updated_inventory_path, "r") as f:
                    updated_inventory = json.load(f)
                self.inventory = updated_inventory
                print(
                    "\nInventory successfully updated from CSV and "
                    f"loaded from {updated_inventory_path}"
                )
            except Exception as e:
                print(f"Error loading updated inventory JSON: {e}")
        elif status == "error":
            error_msg = lines[1].strip() if len(lines) > 1 else "Unknown error"
            print(f"\nMicroservice error: {error_msg}")
        else:
            print("\nUnexpected response from microservice.")
        self.pause()

    # Menu
    def main_menu(self):
        self.title_screen()
        while True:
            self.clear()
            print("====== MAIN MENU ======")
            print("[1] Add Inventory")
            print("[2] View All Inventory")
            print("[3] Search Inventory")
            print("[4] Manage Inventory (Edit/Delete)")
            print("[5] Save Inventory")
            print("[6] Save Inventory to CSV")
            print("[7] Low Inventory Report")
            print("[8] Inventory Value Report")
            print("[9] Upload Inventory from CSV")
            print("[10] Exit")
            choice = input("\nSelect an option: ").strip()

            if choice == "1":
                self.add_inventory()
            elif choice == "2":
                self.view_inventory()
            elif choice == "3":
                self.search_inventory()
            elif choice == "4":
                self.manage_inventory()
            elif choice == "5":
                self.save_inventory()
                self.pause()
            elif choice == "6":
                self.save_inventory_to_csv()
            elif choice == "7":
                self.check_low_inventory()
            elif choice == "8":
                self.check_inventory_value_report()
            elif choice == "9":
                self.upload_inventory_csv()
            elif choice == "10":
                if self.exit_program():
                    break
            else:
                input("Invalid option. Press Enter to try again.")


if __name__ == "__main__":
    app = InventoryApp()
    app.main_menu()
