import os

from qgis.PyQt.QtCore import QSettings
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import (
    QAction,
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QComboBox,
    QListWidget,
    QTextEdit,
    QTableWidget,
    QTableWidgetItem,
    QCheckBox,
    QAbstractItemView,
    QScrollArea,
    QWidget,
    QFrame,
    QSizePolicy,
    QApplication,
    QToolButton,
)

from qgis.core import (
    QgsDataSourceUri,
    QgsProviderRegistry,
    QgsVectorLayer,
    QgsProject,
)


class PostgreSQLConnector:

    def __init__(self, iface):
        self.iface = iface
        self.action = None
        self.settings = QSettings()

    def initGui(self):
        plugin_dir = os.path.dirname(__file__)
        icon_path = os.path.join(plugin_dir, "database.png")

        self.action = QAction(
            QIcon(icon_path),
            "PostgreSQL Connector",
            self.iface.mainWindow(),
        )

        self.action.triggered.connect(self.run)

        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu(
            "&PostgreSQL Connector",
            self.action,
        )

    def unload(self):
        if self.action:
            self.iface.removeToolBarIcon(self.action)
            self.iface.removePluginMenu(
                "&PostgreSQL Connector",
                self.action,
            )

    def run(self):
        dialog = QDialog(self.iface.mainWindow())
        dialog.setWindowTitle("PostgreSQL Connector")
        dialog.resize(820, 760)
        dialog.setMinimumSize(560, 520)

        # Use a clean system font with sensible fallbacks.
        app_font = QApplication.font()
        app_font.setFamily("Segoe UI")
        app_font.setPointSize(10)
        dialog.setFont(app_font)

        dialog.setStyleSheet("""
            QDialog {
                background: #f5f7fa;
            }

            QLabel {
                color: #1f2937;
                font-size: 10pt;
            }

            QLabel#SectionTitle {
                font-size: 12pt;
                font-weight: 600;
                color: #111827;
                padding-top: 4px;
                padding-bottom: 2px;
            }

            QLineEdit,
            QComboBox,
            QListWidget,
            QTextEdit,
            QTableWidget {
                background: white;
                color: #111827;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                padding: 6px;
                selection-background-color: #dbeafe;
                selection-color: #111827;
            }

            QLineEdit:focus,
            QComboBox:focus,
            QListWidget:focus,
            QTextEdit:focus,
            QTableWidget:focus {
                border: 1px solid #2563eb;
            }

            QPushButton {
                background: #2563eb;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 14px;
                font-weight: 600;
            }

            QPushButton:hover {
                background: #1d4ed8;
            }

            QPushButton:pressed {
                background: #1e40af;
            }

            QPushButton:disabled {
                background: #cbd5e1;
                color: #64748b;
            }

            QCheckBox {
                color: #374151;
                spacing: 7px;
            }

            QFrame#SectionCard {
                background: white;
                border: 1px solid #e5e7eb;
                border-radius: 10px;
            }

            QHeaderView::section {
                background: #eef2f7;
                color: #374151;
                border: none;
                border-bottom: 1px solid #d1d5db;
                padding: 6px;
                font-weight: 600;
            }

            QScrollArea {
                border: none;
                background: transparent;
            }

            QScrollBar:vertical {
                background: #eef2f7;
                width: 12px;
                margin: 2px;
                border-radius: 6px;
            }

            QScrollBar::handle:vertical {
                background: #cbd5e1;
                min-height: 32px;
                border-radius: 6px;
            }

            QScrollBar::handle:vertical:hover {
                background: #94a3b8;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        outer_layout = QVBoxLayout(dialog)
        outer_layout.setContentsMargins(10, 10, 10, 10)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)

        content_widget = QWidget()
        main_layout = QVBoxLayout(content_widget)
        main_layout.setContentsMargins(14, 14, 14, 18)
        main_layout.setSpacing(10)

        scroll_area.setWidget(content_widget)
        outer_layout.addWidget(scroll_area)

        # -------------------------------------------------
        # CONNECTION
        # -------------------------------------------------

        section_title = QLabel("PostgreSQL Connection")
        section_title.setObjectName("SectionTitle")
        main_layout.addWidget(section_title)

        host_input = QLineEdit(
            self.settings.value(
                "postgres_connector/host",
                "localhost",
            )
        )
        port_input = QLineEdit(
            self.settings.value(
                "postgres_connector/port",
                "5432",
            )
        )
        database_input = QLineEdit(
            self.settings.value(
                "postgres_connector/database",
                "",
            )
        )
        username_input = QLineEdit(
            self.settings.value(
                "postgres_connector/username",
                "",
            )
        )
        password_input = QLineEdit()
        password_input.setEchoMode(QLineEdit.Password)

        password_container = QWidget()
        password_layout = QHBoxLayout(password_container)
        password_layout.setContentsMargins(0, 0, 0, 0)
        password_layout.setSpacing(6)

        password_layout.addWidget(password_input)

        password_toggle = QToolButton()
        password_toggle.setText("👁")
        password_toggle.setCheckable(True)
        password_toggle.setToolTip("Show password")
        password_toggle.setFixedWidth(38)
        password_toggle.setStyleSheet("""
            QToolButton {
                background: #e5e7eb;
                color: #111827;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                padding: 5px;
            }
            QToolButton:hover {
                background: #d1d5db;
            }
            QToolButton:checked {
                background: #cbd5e1;
            }
        """)

        def toggle_password_visibility(checked):
            if checked:
                password_input.setEchoMode(QLineEdit.Normal)
                password_toggle.setToolTip("Hide password")
            else:
                password_input.setEchoMode(QLineEdit.Password)
                password_toggle.setToolTip("Show password")

        password_toggle.toggled.connect(
            toggle_password_visibility
        )

        password_layout.addWidget(password_toggle)

        remember_checkbox = QCheckBox(
            "Remember host, port, database and username"
        )
        remember_checkbox.setChecked(
            self.settings.value(
                "postgres_connector/remember",
                True,
                type=bool,
            )
        )

        for label_text, widget in [
            ("Host", host_input),
            ("Port", port_input),
            ("Database", database_input),
            ("Username", username_input),
        ]:
            main_layout.addWidget(QLabel(label_text))
            main_layout.addWidget(widget)

        main_layout.addWidget(QLabel("Password"))
        main_layout.addWidget(password_container)

        main_layout.addWidget(remember_checkbox)

        connection_buttons = QHBoxLayout()
        connect_button = QPushButton("Connect")
        refresh_button = QPushButton("Refresh")
        refresh_button.setEnabled(False)
        refresh_button.setStyleSheet("""
            QPushButton {
                background: #e5e7eb;
                color: #111827;
            }
            QPushButton:hover {
                background: #d1d5db;
            }
            QPushButton:pressed {
                background: #cbd5e1;
            }
            QPushButton:disabled {
                background: #f1f5f9;
                color: #94a3b8;
            }
        """)

        connection_buttons.addWidget(connect_button)
        connection_buttons.addWidget(refresh_button)
        main_layout.addLayout(connection_buttons)

        # -------------------------------------------------
        # SCHEMA / SEARCH
        # -------------------------------------------------

        section_title = QLabel("Database Browser")
        section_title.setObjectName("SectionTitle")
        main_layout.addWidget(section_title)

        main_layout.addWidget(QLabel("Schema"))

        schema_combo = QComboBox()
        schema_combo.setEnabled(False)
        main_layout.addWidget(schema_combo)

        main_layout.addWidget(QLabel("Search Tables"))

        search_input = QLineEdit()
        search_input.setPlaceholderText("Search tables or views...")
        search_input.setEnabled(False)
        main_layout.addWidget(search_input)

        # -------------------------------------------------
        # TABLES
        # -------------------------------------------------

        main_layout.addWidget(QLabel("Tables"))

        table_list = QListWidget()
        table_list.setEnabled(False)
        table_list.setMinimumHeight(150)
        main_layout.addWidget(table_list)

        load_button = QPushButton("Load Selected Table")
        load_button.setEnabled(False)
        main_layout.addWidget(load_button)

        # -------------------------------------------------
        # TABLE INFO
        # -------------------------------------------------

        section_title = QLabel("Table Details")
        section_title.setObjectName("SectionTitle")
        main_layout.addWidget(section_title)

        table_info = QTextEdit()
        table_info.setReadOnly(True)
        table_info.setMinimumHeight(170)
        table_info.setPlainText(
            "Select a table to view its information."
        )
        main_layout.addWidget(table_info)

        # -------------------------------------------------
        # ATTRIBUTE PREVIEW
        # -------------------------------------------------

        section_title = QLabel("Attribute Preview")
        section_title.setObjectName("SectionTitle")
        main_layout.addWidget(section_title)

        preview_note = QLabel("Showing up to the first 50 rows")
        preview_note.setStyleSheet("color: #6b7280; font-size: 9pt;")
        main_layout.addWidget(preview_note)

        preview_table = QTableWidget()
        preview_table.setEditTriggers(
            QAbstractItemView.NoEditTriggers
        )
        preview_table.setMinimumHeight(280)
        preview_table.setAlternatingRowColors(True)
        preview_table.setShowGrid(False)
        main_layout.addWidget(preview_table)

        connection_holder = {
            "connection": None,
            "all_tables": [],
        }

        # -------------------------------------------------
        # HELPERS
        # -------------------------------------------------

        def sql_literal(value):
            return value.replace("'", "''")

        def sql_identifier(value):
            return value.replace('"', '""')

        def current_connection_data():
            return {
                "host": host_input.text().strip(),
                "port": port_input.text().strip(),
                "database": database_input.text().strip(),
                "username": username_input.text().strip(),
                "password": password_input.text(),
            }

        def clear_preview():
            preview_table.clear()
            preview_table.setRowCount(0)
            preview_table.setColumnCount(0)

        def save_connection_settings():
            if remember_checkbox.isChecked():
                self.settings.setValue(
                    "postgres_connector/host",
                    host_input.text().strip(),
                )
                self.settings.setValue(
                    "postgres_connector/port",
                    port_input.text().strip(),
                )
                self.settings.setValue(
                    "postgres_connector/database",
                    database_input.text().strip(),
                )
                self.settings.setValue(
                    "postgres_connector/username",
                    username_input.text().strip(),
                )
                self.settings.setValue(
                    "postgres_connector/remember",
                    True,
                )
            else:
                for key in (
                    "host",
                    "port",
                    "database",
                    "username",
                ):
                    self.settings.remove(
                        f"postgres_connector/{key}"
                    )

                self.settings.setValue(
                    "postgres_connector/remember",
                    False,
                )

        # -------------------------------------------------
        # FILTER TABLES
        # -------------------------------------------------

        def apply_filter():
            search_text = search_input.text().strip().lower()

            table_list.clear()

            for table_name, table_type in connection_holder["all_tables"]:
                if not search_text or search_text in table_name.lower():
                    table_list.addItem(table_name)

            table_info.setPlainText(
                "Select a table to view its information."
            )
            clear_preview()

        # -------------------------------------------------
        # LOAD TABLES
        # -------------------------------------------------

        def load_tables():
            connection = connection_holder["connection"]

            if connection is None:
                return

            schema = schema_combo.currentText()

            if not schema:
                connection_holder["all_tables"] = []
                table_list.clear()
                return

            schema_sql = sql_literal(schema)

            rows = connection.executeSql(
                f"""
                SELECT table_name, table_type
                FROM information_schema.tables
                WHERE table_schema = '{schema_sql}'
                  AND table_type IN ('BASE TABLE', 'VIEW')
                ORDER BY table_name;
                """
            )

            connection_holder["all_tables"] = [
                (str(row[0]), str(row[1]))
                for row in rows
            ]

            apply_filter()

        # -------------------------------------------------
        # LOAD SCHEMAS
        # -------------------------------------------------

        def load_schemas():
            connection = connection_holder["connection"]

            if connection is None:
                return

            previous_schema = schema_combo.currentText()

            schema_combo.blockSignals(True)
            schema_combo.clear()

            rows = connection.executeSql(
                """
                SELECT schema_name
                FROM information_schema.schemata
                WHERE schema_name NOT IN (
                    'pg_catalog',
                    'information_schema'
                )
                  AND schema_name NOT LIKE 'pg_toast%'
                  AND schema_name NOT LIKE 'pg_temp_%'
                ORDER BY schema_name;
                """
            )

            for row in rows:
                schema_combo.addItem(str(row[0]))

            if previous_schema:
                index = schema_combo.findText(previous_schema)
                if index >= 0:
                    schema_combo.setCurrentIndex(index)

            schema_combo.blockSignals(False)

            if schema_combo.count() > 0:
                load_tables()
            else:
                connection_holder["all_tables"] = []
                table_list.clear()

        # -------------------------------------------------
        # CONNECT
        # -------------------------------------------------

        def connect_database():
            data = current_connection_data()

            if (
                not data["host"]
                or not data["port"]
                or not data["database"]
                or not data["username"]
            ):
                QMessageBox.warning(
                    dialog,
                    "Missing information",
                    "Please fill in Host, Port, Database and Username.",
                )
                return

            try:
                uri = QgsDataSourceUri()
                uri.setConnection(
                    data["host"],
                    data["port"],
                    data["database"],
                    data["username"],
                    data["password"],
                )

                metadata = (
                    QgsProviderRegistry.instance()
                    .providerMetadata("postgres")
                )

                if metadata is None:
                    raise Exception(
                        "PostgreSQL provider is not available."
                    )

                connection = metadata.createConnection(
                    uri.uri(False),
                    {},
                )

                connection.executeSql("SELECT 1;")

                connection_holder["connection"] = connection

                save_connection_settings()

                schema_combo.setEnabled(True)
                search_input.setEnabled(True)
                table_list.setEnabled(True)
                load_button.setEnabled(True)
                refresh_button.setEnabled(True)

                load_schemas()

                QMessageBox.information(
                    dialog,
                    "Connection successful",
                    "Connected successfully to PostgreSQL.",
                )

            except Exception as error:
                connection_holder["connection"] = None

                schema_combo.setEnabled(False)
                search_input.setEnabled(False)
                table_list.setEnabled(False)
                load_button.setEnabled(False)
                refresh_button.setEnabled(False)

                QMessageBox.critical(
                    dialog,
                    "Connection failed",
                    str(error),
                )

        # -------------------------------------------------
        # REFRESH
        # -------------------------------------------------

        def refresh_database():
            connection = connection_holder["connection"]

            if connection is None:
                return

            try:
                connection.executeSql("SELECT 1;")
                load_schemas()

                QMessageBox.information(
                    dialog,
                    "Refresh complete",
                    "Schemas and tables were refreshed.",
                )

            except Exception as error:
                QMessageBox.critical(
                    dialog,
                    "Refresh failed",
                    str(error),
                )

        # -------------------------------------------------
        # ATTRIBUTE PREVIEW
        # -------------------------------------------------

        def load_preview(schema, table):
            connection = connection_holder["connection"]

            if connection is None:
                return

            try:
                schema_sql = sql_literal(schema)
                table_sql = sql_literal(table)
                schema_ident = sql_identifier(schema)
                table_ident = sql_identifier(table)

                column_rows = connection.executeSql(
                    f"""
                    SELECT column_name, udt_name
                    FROM information_schema.columns
                    WHERE table_schema = '{schema_sql}'
                      AND table_name = '{table_sql}'
                    ORDER BY ordinal_position;
                    """
                )

                preview_columns = [
                    str(row[0])
                    for row in column_rows
                    if str(row[1]) not in ("geometry", "geography")
                ]

                clear_preview()

                if not preview_columns:
                    return

                column_sql = ", ".join(
                    f'"{sql_identifier(column)}"'
                    for column in preview_columns
                )

                rows = connection.executeSql(
                    f'''
                    SELECT {column_sql}
                    FROM "{schema_ident}"."{table_ident}"
                    LIMIT 50;
                    '''
                )

                preview_table.setColumnCount(
                    len(preview_columns)
                )
                preview_table.setHorizontalHeaderLabels(
                    preview_columns
                )
                preview_table.setRowCount(
                    len(rows)
                )

                for row_index, row in enumerate(rows):
                    for column_index, value in enumerate(row):
                        preview_table.setItem(
                            row_index,
                            column_index,
                            QTableWidgetItem(
                                "" if value is None else str(value)
                            ),
                        )

                preview_table.resizeColumnsToContents()

            except Exception as error:
                clear_preview()
                preview_table.setRowCount(1)
                preview_table.setColumnCount(1)
                preview_table.setHorizontalHeaderLabels(
                    ["Preview Error"]
                )
                preview_table.setItem(
                    0,
                    0,
                    QTableWidgetItem(str(error)),
                )

        # -------------------------------------------------
        # TABLE INFO
        # -------------------------------------------------

        def show_table_info(item=None):
            connection = connection_holder["connection"]

            if connection is None:
                return

            if item is None:
                item = table_list.currentItem()

            if item is None:
                table_info.setPlainText(
                    "Select a table to view its information."
                )
                clear_preview()
                return

            schema = schema_combo.currentText()
            table = item.text()

            schema_sql = sql_literal(schema)
            table_sql = sql_literal(table)
            schema_ident = sql_identifier(schema)
            table_ident = sql_identifier(table)

            try:
                type_rows = connection.executeSql(
                    f"""
                    SELECT table_type
                    FROM information_schema.tables
                    WHERE table_schema = '{schema_sql}'
                      AND table_name = '{table_sql}'
                    LIMIT 1;
                    """
                )
                table_type = (
                    str(type_rows[0][0])
                    if type_rows else "Unknown"
                )

                column_rows = connection.executeSql(
                    f"""
                    SELECT COUNT(*)
                    FROM information_schema.columns
                    WHERE table_schema = '{schema_sql}'
                      AND table_name = '{table_sql}';
                    """
                )
                column_count = (
                    str(column_rows[0][0])
                    if column_rows else "Unknown"
                )

                pk_rows = connection.executeSql(
                    f"""
                    SELECT kcu.column_name
                    FROM information_schema.table_constraints tc
                    JOIN information_schema.key_column_usage kcu
                      ON tc.constraint_name = kcu.constraint_name
                     AND tc.table_schema = kcu.table_schema
                     AND tc.table_name = kcu.table_name
                    WHERE tc.constraint_type = 'PRIMARY KEY'
                      AND tc.table_schema = '{schema_sql}'
                      AND tc.table_name = '{table_sql}'
                    ORDER BY kcu.ordinal_position;
                    """
                )
                primary_key = (
                    ", ".join(str(row[0]) for row in pk_rows)
                    if pk_rows else "None"
                )

                owner_rows = connection.executeSql(
                    f"""
                    SELECT tableowner
                    FROM pg_tables
                    WHERE schemaname = '{schema_sql}'
                      AND tablename = '{table_sql}'
                    LIMIT 1;
                    """
                )

                if not owner_rows:
                    owner_rows = connection.executeSql(
                        f"""
                        SELECT viewowner
                        FROM pg_views
                        WHERE schemaname = '{schema_sql}'
                          AND viewname = '{table_sql}'
                        LIMIT 1;
                        """
                    )

                owner = (
                    str(owner_rows[0][0])
                    if owner_rows else "Unknown"
                )

                geometry_rows = connection.executeSql(
                    f"""
                    SELECT column_name, udt_name
                    FROM information_schema.columns
                    WHERE table_schema = '{schema_sql}'
                      AND table_name = '{table_sql}'
                      AND udt_name IN ('geometry', 'geography')
                    ORDER BY ordinal_position
                    LIMIT 1;
                    """
                )

                geometry_column = "None"
                geometry_storage = "Non-spatial"
                geometry_type = "N/A"
                srid = "N/A"

                if geometry_rows:
                    geometry_column = str(
                        geometry_rows[0][0]
                    )
                    geometry_storage = str(
                        geometry_rows[0][1]
                    )
                    geom_ident = sql_identifier(
                        geometry_column
                    )

                    metadata_rows = connection.executeSql(
                        f'''
                        SELECT
                            GeometryType("{geom_ident}"),
                            ST_SRID("{geom_ident}")
                        FROM "{schema_ident}"."{table_ident}"
                        WHERE "{geom_ident}" IS NOT NULL
                        LIMIT 1;
                        '''
                    )

                    if metadata_rows:
                        geometry_type = str(
                            metadata_rows[0][0]
                        )
                        srid = str(
                            metadata_rows[0][1]
                        )

                count_rows = connection.executeSql(
                    f'''
                    SELECT COUNT(*)
                    FROM "{schema_ident}"."{table_ident}";
                    '''
                )
                row_count = (
                    str(count_rows[0][0])
                    if count_rows else "Unknown"
                )

                table_info.setPlainText(
                    f"Schema: {schema}\n"
                    f"Table: {table}\n"
                    f"Type: {table_type}\n"
                    f"Owner: {owner}\n"
                    f"Primary key: {primary_key}\n"
                    f"Columns: {column_count}\n"
                    f"Rows / Features: {row_count}\n"
                    f"Geometry column: {geometry_column}\n"
                    f"Geometry storage: {geometry_storage}\n"
                    f"Geometry type: {geometry_type}\n"
                    f"SRID: {srid}"
                )

                load_preview(
                    schema,
                    table,
                )

            except Exception as error:
                table_info.setPlainText(
                    "Could not read table information.\n\n"
                    + str(error)
                )
                clear_preview()

        # -------------------------------------------------
        # LOAD TABLE INTO QGIS
        # -------------------------------------------------

        def load_selected_table(item=None):
            connection = connection_holder["connection"]

            if connection is None:
                return

            if item is None:
                item = table_list.currentItem()

            if item is None:
                QMessageBox.warning(
                    dialog,
                    "No table selected",
                    "Please select a table first.",
                )
                return

            schema = schema_combo.currentText()
            table = item.text()

            schema_sql = sql_literal(schema)
            table_sql = sql_literal(table)
            data = current_connection_data()

            try:
                geometry_rows = connection.executeSql(
                    f"""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_schema = '{schema_sql}'
                      AND table_name = '{table_sql}'
                      AND udt_name IN ('geometry', 'geography')
                    ORDER BY ordinal_position
                    LIMIT 1;
                    """
                )

                key_rows = connection.executeSql(
                    f"""
                    SELECT kcu.column_name
                    FROM information_schema.table_constraints tc
                    JOIN information_schema.key_column_usage kcu
                      ON tc.constraint_name = kcu.constraint_name
                     AND tc.table_schema = kcu.table_schema
                     AND tc.table_name = kcu.table_name
                    WHERE tc.constraint_type = 'PRIMARY KEY'
                      AND tc.table_schema = '{schema_sql}'
                      AND tc.table_name = '{table_sql}'
                    ORDER BY kcu.ordinal_position
                    LIMIT 1;
                    """
                )

                key_column = (
                    str(key_rows[0][0])
                    if key_rows else ""
                )

                uri = QgsDataSourceUri()
                uri.setConnection(
                    data["host"],
                    data["port"],
                    data["database"],
                    data["username"],
                    data["password"],
                )

                if geometry_rows:
                    geometry_column = str(
                        geometry_rows[0][0]
                    )

                    uri.setDataSource(
                        schema,
                        table,
                        geometry_column,
                        "",
                        key_column,
                    )
                else:
                    uri.setDataSource(
                        schema,
                        table,
                        "",
                        "",
                        key_column,
                    )

                layer = QgsVectorLayer(
                    uri.uri(False),
                    table,
                    "postgres",
                )

                if not layer.isValid():
                    QMessageBox.critical(
                        dialog,
                        "Layer loading failed",
                        f"QGIS could not load {schema}.{table}.",
                    )
                    return

                QgsProject.instance().addMapLayer(layer)

                QMessageBox.information(
                    dialog,
                    "Table loaded",
                    f"{schema}.{table} was added to the QGIS project.",
                )

            except Exception as error:
                QMessageBox.critical(
                    dialog,
                    "Layer loading failed",
                    str(error),
                )

        # -------------------------------------------------
        # SIGNALS
        # -------------------------------------------------

        connect_button.clicked.connect(
            connect_database
        )
        refresh_button.clicked.connect(
            refresh_database
        )
        schema_combo.currentTextChanged.connect(
            load_tables
        )
        search_input.textChanged.connect(
            apply_filter
        )
        table_list.currentItemChanged.connect(
            lambda current, previous: show_table_info(current)
        )
        table_list.itemDoubleClicked.connect(
            load_selected_table
        )
        load_button.clicked.connect(
            lambda: load_selected_table()
        )

        main_layout.addStretch(1)

        dialog.exec()
