# PostgreSQL Connector for QGIS

A lightweight QGIS plugin for connecting to PostgreSQL/PostGIS databases, browsing schemas and tables, previewing attributes, inspecting table metadata, and loading spatial or non-spatial tables directly into QGIS.

## Features

- Connect to PostgreSQL using host, port, database, username, and password
- Show/hide password with an eye button
- Optional remembering of host, port, database, and username
- Password is not saved by the plugin
- Browse database schemas
- Search and filter tables and views
- Refresh schemas and tables without restarting QGIS
- Inspect table metadata:
  - table type
  - owner
  - primary key
  - number of columns
  - row / feature count
  - geometry column
  - geometry storage type
  - geometry type
  - SRID
- Preview up to the first 50 non-spatial attribute rows
- Load PostGIS spatial tables as QGIS layers
- Load non-spatial PostgreSQL tables into QGIS
- Double-click a table to load it
- Scrollable interface for smaller screens
- Custom plugin icon support via `database.png`

## Requirements

- QGIS 3.28 or newer
- PostgreSQL
- PostGIS for spatial tables

No additional Python packages are required. The plugin uses the PostgreSQL provider included with QGIS.

## Installation

### Manual installation

1. Download or clone this repository.
2. Make sure the plugin folder contains:

```text
postgres_connector/
├── __init__.py
├── postgres_connector.py
├── metadata.txt
└── database.png
```

3. Copy the `postgres_connector` folder to your QGIS plugins directory.

On Windows this is usually:

```text
C:\Users\<USERNAME>\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\
```

4. Restart QGIS.
5. Open **Plugins → Manage and Install Plugins**.
6. Enable **PostgreSQL Connector**.

## Usage

1. Open the plugin from the toolbar or plugin menu.
2. Enter your PostgreSQL connection details.
3. Click **Connect**.
4. Choose a schema.
5. Search or select a table.
6. Review the table information and attribute preview.
7. Click **Load Selected Table** or double-click the table to add it to QGIS.

## Security

The plugin does **not** save the database password.

If the **Remember host, port, database and username** option is enabled, only those non-password connection details are stored using QGIS/Qt settings.

## Project Status

Current release: **0.1.0**

This is an early public release. Feedback, bug reports, and contributions are welcome.

## License

This project is licensed under the GNU General Public License v2.0 or later.

See the [LICENSE](LICENSE) file for details.
