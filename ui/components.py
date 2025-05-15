"""
UI components for the Remote Patient Monitoring application
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QComboBox,
    QPushButton, QLabel, QTextEdit, QGroupBox, QFrame,
    QMessageBox, QTableWidget, QAbstractItemView
)

from config import VALID_PATIENTS, SPO2_THRESHOLD


class UIComponents:
    """
    Helper class to set up UI components for the main window
    """

    @staticmethod
    def setup_header(parent):
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 15)

        title_area = QWidget()
        title_layout = QVBoxLayout(title_area)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(5)

        title_label = QLabel("Remote Patient Monitoring")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #051d40;")

        subtitle_label = QLabel("Real-time SpO2 monitoring system")
        subtitle_font = QFont()
        subtitle_font.setPointSize(10)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setStyleSheet("color: #6c757d;")

        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)

        selection_area = QWidget()
        selection_area.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border-radius: 8px;
                border: 1px solid #e9ecef;
            }
        """)
        selection_layout = QHBoxLayout(selection_area)
        selection_layout.setContentsMargins(15, 10, 15, 10)
        selection_layout.setSpacing(10)

        patient_label = QLabel("Patient:")
        patient_label.setFixedWidth(60)
        font = QFont()
        font.setBold(True)
        patient_label.setFont(font)

        parent.combobox_patient = QComboBox()
        parent.combobox_patient.setCursor(Qt.PointingHandCursor)
        parent.combobox_patient.setStyleSheet("""
            QComboBox {
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 5px 30px 5px 10px;
                background-color: white;
                color: #1a1a1a;
                min-width: 150px;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 24px;
                border-left: 1px solid #ced4da;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #ced4da;
                selection-background-color: #e9ecef;
                selection-color: #212121;
                background-color: white;
                font-size: 13px;
            }
        """)

        for patient_id in sorted(VALID_PATIENTS):
            parent.combobox_patient.addItem(f"Patient {patient_id}", userData=patient_id)

        if parent.combobox_patient.count() > 0:
            parent.combobox_patient.setCurrentIndex(0)
            parent.current_patient = parent.combobox_patient.currentData()

        parent.combobox_patient.currentIndexChanged.connect(parent.on_patient_changed)

        parent.refresh_button = QPushButton("Refresh")
        parent.refresh_button.setFixedWidth(100)
        parent.refresh_button.setCursor(Qt.PointingHandCursor)
        parent.refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #0d6efd;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0b5ed7;
            }
            QPushButton:disabled {
                background-color: #8cadf3;
                color: #ffffff;
            }
        """)
        parent.refresh_button.clicked.connect(parent.fetch_patient_data)

        selection_layout.addWidget(patient_label)
        selection_layout.addWidget(parent.combobox_patient)
        selection_layout.addWidget(parent.refresh_button)

        header_layout.addWidget(title_area, 1)
        header_layout.addWidget(selection_area)

        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("""
            background-color: #dee2e6;
            margin-top: 5px;
            margin-bottom: 5px;
        """)

        parent.main_layout.addWidget(header_widget)
        parent.main_layout.addWidget(separator)

        return header_widget

    @staticmethod
    def setup_data_view(parent):
        data_widget = QWidget()
        data_layout = QVBoxLayout(data_widget)
        data_layout.setContentsMargins(0, 0, 0, 0)
        data_layout.setSpacing(10)

        parent.patient_info = QLabel("Loading patient data...")
        parent.patient_info.setStyleSheet("""
            background-color: #e8f4ff;
            padding: 10px;
            border-radius: 8px;
            border: 1px solid #c8e1ff;
            font-size: 14px;
            font-weight: bold;
        """)
        parent.patient_info.setAlignment(Qt.AlignCenter)
        data_layout.addWidget(parent.patient_info)

        parent.table_group = QGroupBox("SpO2 Readings")
        table_layout = QVBoxLayout(parent.table_group)
        table_layout.setContentsMargins(15, 20, 15, 15)

        parent.table = QTableWidget(0, 3)
        parent.table.setHorizontalHeaderLabels(["Time", "SpO2 (%)", "Status"])
        parent.table.horizontalHeader().setStretchLastSection(True)
        parent.table.verticalHeader().setVisible(False)

        parent.table.setSelectionMode(QAbstractItemView.NoSelection)  # ✅ fixed
        parent.table.setEditTriggers(QTableWidget.NoEditTriggers)
        parent.table.setAlternatingRowColors(False)  # ✅ fixes macOS coloring issue
        parent.table.setShowGrid(False)

        table_layout.addWidget(parent.table)
        data_layout.addWidget(parent.table_group)

        parent.main_content_layout.addWidget(data_widget, 3)

        return data_widget

    @staticmethod
    def setup_status_message_view(parent):
        status_widget = QWidget()
        status_layout = QVBoxLayout(status_widget)
        status_layout.setContentsMargins(0, 0, 0, 0)
        status_layout.setSpacing(15)

        parent.status_group = QGroupBox("Patient Status")
        status_group_layout = QVBoxLayout(parent.status_group)
        status_group_layout.setContentsMargins(15, 20, 15, 15)

        parent.status_label = QLabel("Status: Unknown")
        parent.status_label.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setBold(True)
        font.setPointSize(16)
        parent.status_label.setFont(font)

        status_group_layout.addWidget(parent.status_label)
        status_layout.addWidget(parent.status_group)

        parent.message_group = QGroupBox("Clinical Advice")
        message_layout = QVBoxLayout(parent.message_group)
        message_layout.setContentsMargins(15, 20, 15, 15)
        message_layout.setSpacing(10)

        message_info = QLabel(
            f"When SpO2 levels are below {SPO2_THRESHOLD}%, you can send clinical advice to the patient:")
        message_info.setWordWrap(True)
        message_info.setStyleSheet("color: #6c757d;")

        parent.message_text = QTextEdit()
        parent.message_text.setPlaceholderText("Enter clinical advice for the patient...")
        parent.message_text.setEnabled(False)

        parent.send_button = QPushButton("Send Advice")
        parent.send_button.setCursor(Qt.PointingHandCursor)
        parent.send_button.clicked.connect(parent.send_message)
        parent.send_button.setEnabled(False)

        message_layout.addWidget(message_info)
        message_layout.addWidget(parent.message_text)
        message_layout.addWidget(parent.send_button)

        status_layout.addWidget(parent.message_group)
        status_layout.addStretch(1)

        parent.main_content_layout.addWidget(status_widget, 2)

        return status_widget

    @staticmethod
    def create_message_box(parent, title, text, info_text, icon_type=QMessageBox.Icon.Information):
        msg = QMessageBox(parent)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setInformativeText(info_text)
        msg.setIcon(icon_type)

        if icon_type in [QMessageBox.Icon.Critical, QMessageBox.Icon.Warning]:
            button_style = """
                background-color: #1a1a1a;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 12px;
            """
        else:
            button_style = """
                background-color: #7bb9ff;
                color: black;
                border: none;
                padding: 6px 12px;
                border-radius: 12px;
            """

        msg.setStyleSheet(f"""
            QMessageBox {{
                background-color: white;
            }}
            QMessageBox QLabel {{
                color: #1a1a1a;
            }}
            QPushButton {{
                {button_style}
            }}
        """)

        return msg
