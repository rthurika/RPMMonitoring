"""
UI components for the Remote Patient Monitoring application
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QComboBox,
                               QPushButton, QLabel, QTableWidget, QTextEdit, QGroupBox, QFrame, QMessageBox)
from PySide6.QtWidgets import QTableWidget, QAbstractItemView

from config import VALID_PATIENTS, SPO2_THRESHOLD


class UIComponents:
    """
    Helper class to set up UI components for the main window
    """

    @staticmethod
    def setup_header(parent):
        """
        Set up the header section with title and patient selection
        """
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 15)

        # Title and subtitle
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

        # Patient selection area with visual distinction
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
        parent.combobox_patient.setStyleSheet("""
            QComboBox {
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 5px;
                background-color: white;
                color: #1a1a1a;
                min-width: 150px;
            }
            QComboBox::drop-down {
                border: none;
                width: 24px;
            }
        """)
        for patient_id in VALID_PATIENTS:
            parent.combobox_patient.addItem(f"Patient {patient_id}", patient_id)
        parent.combobox_patient.currentIndexChanged.connect(parent.on_patient_changed)

        # Refresh button with icon-like appearance
        parent.refresh_button = QPushButton("Refresh")
        parent.refresh_button.setFixedWidth(100)
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

        # Add separator with shadow effect for visual depth
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
        """
        Set up the data view area with patient info and data table
        """
        data_widget = QWidget()
        data_layout = QVBoxLayout(data_widget)
        data_layout.setContentsMargins(0, 0, 0, 0)
        data_layout.setSpacing(10)

        # Patient info display
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

        # Table view
        parent.table_group = QGroupBox("SpO2 Readings")
        table_layout = QVBoxLayout(parent.table_group)
        table_layout.setContentsMargins(15, 20, 15, 15)

        parent.table = QTableWidget(0, 3)
        parent.table.setHorizontalHeaderLabels(["Time", "SpO2 (%)", "Status"])
        parent.table.horizontalHeader().setStretchLastSection(True)
        parent.table.verticalHeader().setVisible(False)

        # Disable selection to make it clear the table isn't interactive
        parent.table.setSelectionMode(QTableWidget.NoSelection)
        parent.table.setEditTriggers(QTableWidget.NoEditTriggers)

        parent.table.setAlternatingRowColors(True)
        parent.table.setShowGrid(False)

        table_layout.addWidget(parent.table)
        data_layout.addWidget(parent.table_group)

        parent.main_content_layout.addWidget(data_widget, 3)

        return data_widget

    @staticmethod
    def setup_status_message_view(parent):
        """
        Set up the status and message area

        Args:
            parent: The main window instance

        Returns:
            QWidget: The status widget
        """
        status_widget = QWidget()
        status_layout = QVBoxLayout(status_widget)
        status_layout.setContentsMargins(0, 0, 0, 0)
        status_layout.setSpacing(15)

        # Overall status
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

        # Message area
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
        """
        Create a styled message box

        Args:
            parent: The parent widget
            title: Message box title
            text: Main message text
            info_text: Informational text
            icon_type: Message box icon type

        Returns:
            QMessageBox: The configured message box
        """
        msg = QMessageBox(parent)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setInformativeText(info_text)
        msg.setIcon(icon_type)

        # Apply styling based on message type
        if icon_type == QMessageBox.Icon.Critical or icon_type == QMessageBox.Icon.Warning:
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