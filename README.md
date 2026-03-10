# Inventory Management Application

A Python terminal application for managing product inventory, built with a microservices architecture. Developed for CS361 at Oregon State University.

## Features

- **Add / View / Search** inventory items
- **Edit and Delete** items individually or via search
- **Save to JSON** for persistent storage
- **Export to CSV** — generates a timestamped CSV export
- **Upload from CSV** — bulk add or update inventory via CSV file
- **Low Inventory Report** — flags items at or below their restock threshold
- **Inventory Value Report** — calculates total quantity and dollar value on hand

## Architecture

The application uses a file-based pipe system to communicate between the main app and independent microservices.

```
main.py                        # Main application (UI + CRUD)
microservices/
  low_inventory_checker.py     # Generates low stock report
  inventory_value_report.py    # Calculates total inventory value
  save_to_csv.py               # Exports inventory to CSV
  csv_upload.py                # Imports/updates inventory from CSV
data/
  inventory.json               # Main inventory data store
pipes/                         # IPC pipe files (text-based)
csv/                           # CSV exports and sample upload files
```

## Getting Started

### Requirements

- Python 3.10+
- No external dependencies

### Running the Application

1. Start the microservices (each in its own terminal):

```bash
python3 microservices/low_inventory_checker.py
python3 microservices/inventory_value_report.py
python3 microservices/save_to_csv.py
python3 microservices/csv_upload.py
```

2. Run the main application:

```bash
python3 main.py
```

### CSV Upload Format

CSV files must include the following columns:

```
name, sku, quantity, restock threshold, size, material, location, cost
```

Sample files are provided in the `csv/` directory.

## Data

A sample inventory dataset is included in `data/inventory.json` with 11 framing supply items to demonstrate all application features.
