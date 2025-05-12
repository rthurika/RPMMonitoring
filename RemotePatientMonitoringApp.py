#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Remote Patient Monitoring Application

This application monitors patient SpO2 levels from a remote API and allows
clinicians to send advice when readings are below normal levels.
"""

import sys
import json
from datetime import datetime
import requests
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QLabel, QComboBox, QPushButton,
                               QTableWidget, QTableWidgetItem, QTextEdit, QGroupBox,
                               QMessageBox, QHeaderView, QFrame)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QFont, QPalette


class RemotePatientMonitoringApp(QMainWindow):
    """Main application window for the Remote Patient Monitoring system."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Remote Patient Monitoring")
        self.setGeometry(100, 100, 900, 700)

        # Apply Apple-like styling globally
        self.apply_global_styles()

        # Main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)

        # Patient info header
        self.setup_patient_header()

        # Patient selection section
        self.setup_patient_selection()

        # Data display section
        self.setup_data_display()

        # Status section
        self.setup_status_display()

        # Message section
        self.setup_message_section()

        # Initial state
        self.message_group.setEnabled(False)

        # Auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.fetch_patient_data)
        self.refresh_timer.start(30000)  # Refresh every 30 seconds

    def apply_global_styles(self):
        """Apply modern Apple-like styles to the entire application."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;  /* Dark background */
            }
            QGroupBox {
                border-radius: 10px;
                border: 1px solid #3d3d3d;
                margin-top: 12px;
                font-weight: bold;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 10px;
                padding: 0 5px;
                color: #666666;
            }
            QPushButton {
                background-color: #0071e3;
                color: white;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background-color: #0077ED;
            }
            QPushButton:pressed {
                background-color: #0062C3;
            }
            QPushButton:disabled {
                background-color: #B3D7FF;
                color: #EEEEEE;
            }
            QLabel {
                color: #333333;
            }
            QComboBox {
                border-radius: 6px;
                padding: 6px;
                border: 1px solid #e0e0e0;
                background-color: white;
            }
            QComboBox:hover {
                border-color: #0071e3;
                background-color: #f0f9ff;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #e0e0e0;
                background-color: white;
                selection-background-color: #0071e3;
                selection-color: white;
            }
            QTableWidget {
                border-radius: 6px;
                border: 1px solid #e0e0e0;
                gridline-color: #f0f0f0;
                selection-background-color: #e8f0fe;
                selection-color: #333333;
            }
            QTableWidget::item {
                padding: 5px;
                border-bottom: 1px solid #f0f0f0;
            }
            QTableWidget QHeaderView::section {
                background-color: #f5f5f7;
                color: #666666;
                font-weight: bold;
                padding: 8px;
                border: none;
                border-bottom: 1px solid #e0e0e0;
            }
            QTextEdit {
                border-radius: 6px;
                border: 1px solid #e0e0e0;
                padding: 5px;
                background-color: white;
                color: #333333;  /* Make text clearly visible */
            }
            QTextEdit[placeholderText] {
                color: #86868b;  /* Ensuring placeholder text is visible */
            }
        """)

    def setup_patient_header(self):
        """Create the header showing current patient information."""
        header_group = QGroupBox("Current Patient")
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(15, 20, 15, 15)

        self.patient_header = QLabel("No patient data loaded")
        self.patient_header.setFont(
            QFont("SF Pro Display, -apple-system, BlinkMacSystemFont, Helvetica, Arial", 18, QFont.Bold))
        self.patient_header.setAlignment(Qt.AlignLeft)
        self.patient_header.setStyleSheet("color: #1d1d1f;")

        self.last_updated = QLabel("Last updated: Never")
        self.last_updated.setFont(QFont("SF Pro Text, -apple-system, BlinkMacSystemFont, Helvetica, Arial", 12))
        self.last_updated.setAlignment(Qt.AlignRight)
        self.last_updated.setStyleSheet("color: #86868b;")

        header_layout.addWidget(self.patient_header)
        header_layout.addWidget(self.last_updated)

        header_group.setLayout(header_layout)
        header_group.setFixedHeight(90)
        self.main_layout.addWidget(header_group)

    def setup_patient_selection(self):
        """Create the patient selection controls."""
        patient_group = QGroupBox("Patient Selection")
        patient_layout = QHBoxLayout()
        patient_layout.setContentsMargins(15, 20, 15, 15)
        patient_layout.setSpacing(12)

        self.patient_label = QLabel("Select Patient ID:")
        self.patient_label.setFont(QFont("SF Pro Text, -apple-system, BlinkMacSystemFont, Helvetica, Arial", 13))

        self.patient_combo = QComboBox()
        self.patient_combo.addItems(["1", "2", "3", "10", "42"])
        self.patient_combo.setFixedHeight(38)
        self.patient_combo.setFixedWidth(100)
        self.patient_combo.setFont(QFont("SF Pro Text, -apple-system, BlinkMacSystemFont, Helvetica, Arial", 13))

        self.fetch_button = QPushButton("Fetch Data")
        self.fetch_button.setFont(QFont("SF Pro Text, -apple-system, BlinkMacSystemFont, Helvetica, Arial", 13))
        self.fetch_button.setFixedHeight(38)
        self.fetch_button.setFixedWidth(120)
        self.fetch_button.clicked.connect(self.fetch_patient_data)

        patient_layout.addWidget(self.patient_label)
        patient_layout.addWidget(self.patient_combo)
        patient_layout.addWidget(self.fetch_button)
        patient_layout.addStretch()

        patient_group.setLayout(patient_layout)
        patient_group.setFixedHeight(100)
        self.main_layout.addWidget(patient_group)

    def setup_data_display(self):
        """Create the data display table."""
        data_group = QGroupBox("SpO2 Readings")
        data_layout = QVBoxLayout()
        data_layout.setContentsMargins(15, 20, 15, 15)

        # Table for readings - fixed height to show all 3 rows without scrolling
        self.readings_table = QTableWidget(0, 3)
        self.readings_table.setHorizontalHeaderLabels(["Timestamp", "SpO2 (%)", "Status"])
        self.readings_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.readings_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.readings_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.readings_table.setShowGrid(False)  # Apple UIs typically don't show grids
        self.readings_table.setAlternatingRowColors(True)
        self.readings_table.verticalHeader().setVisible(False)  # Hide row numbers
        self.readings_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.readings_table.setEditTriggers(QTableWidget.NoEditTriggers)  # Read-only

        # Set fixed height to fit 3 rows plus header
        # We're using a fixed height calculation: header (30px) + 3 rows (40px each) + margins
        self.readings_table.setFixedHeight(170)  # This should be enough for 3 rows + header
        self.readings_table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # Disable scrollbar

        # Set row height
        self.readings_table.verticalHeader().setDefaultSectionSize(40)

        data_layout.addWidget(self.readings_table)
        data_group.setLayout(data_layout)
        self.main_layout.addWidget(data_group)

    def setup_status_display(self):
        """Create the overall status display section."""
        status_group = QGroupBox("Overall Status")
        status_layout = QHBoxLayout()
        status_layout.setContentsMargins(15, 20, 15, 15)

        self.status_label = QLabel("Status: Not analyzed yet")
        self.status_label.setFont(
            QFont("SF Pro Display, -apple-system, BlinkMacSystemFont, Helvetica, Arial", 14, QFont.Bold))
        self.status_label.setAlignment(Qt.AlignCenter)

        # Create a frame for the status indicator - smaller height
        status_container = QFrame()
        status_container.setFrameShape(QFrame.StyledPanel)
        status_container.setStyleSheet("""
            QFrame {
                border-radius: 8px;
                background-color: #f5f5f7;
                padding: 8px;  /* Reduced padding */
            }
        """)

        container_layout = QVBoxLayout(status_container)
        container_layout.addWidget(self.status_label)
        container_layout.setContentsMargins(10, 5, 10, 5)  # Smaller margins

        status_layout.addWidget(status_container)

        status_group.setLayout(status_layout)
        status_group.setFixedHeight(90)  # Reduced height
        self.main_layout.addWidget(status_group)

    def setup_message_section(self):
        """Create the message input and sending section."""
        self.message_group = QGroupBox("Send Advice to Patient")
        message_layout = QVBoxLayout()
        message_layout.setContentsMargins(15, 20, 15, 15)
        message_layout.setSpacing(12)

        # Instruction label
        instruction_label = QLabel("When SpO2 readings are below 95%, you can send advice to the patient:")
        instruction_label.setFont(QFont("SF Pro Text, -apple-system, BlinkMacSystemFont, Helvetica, Arial", 13))
        instruction_label.setStyleSheet("color: #666666;")

        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("Enter your advice for the patient here...")
        self.message_input.setFixedHeight(100)
        self.message_input.setFont(QFont("SF Pro Text, -apple-system, BlinkMacSystemFont, Helvetica, Arial", 13))
        # Ensure placeholder text is visible with appropriate contrast
        self.message_input.setStyleSheet("""
            QTextEdit {
                color: #333333;
            }
            QTextEdit[placeholderText] {
                color: #8a8a8f;
            }
        """)

        self.send_button = QPushButton("Send Advice")
        self.send_button.setFont(QFont("SF Pro Text, -apple-system, BlinkMacSystemFont, Helvetica, Arial", 13))
        self.send_button.setFixedHeight(38)
        self.send_button.setFixedWidth(120)
        self.send_button.clicked.connect(self.send_message)

        # Button container for right alignment
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.addStretch()
        button_layout.addWidget(self.send_button)

        message_layout.addWidget(instruction_label)
        message_layout.addWidget(self.message_input)
        message_layout.addWidget(button_container)

        self.message_group.setLayout(message_layout)
        self.main_layout.addWidget(self.message_group)

    def fetch_patient_data(self):
        """Fetch patient data from the API."""
        patient_id = self.patient_combo.currentText()
        url = f"https://disp.yxl.ch/rpm/patients/{patient_id}"

        # Show loading state
        self.fetch_button.setEnabled(False)
        self.fetch_button.setText("Loading...")
        self.patient_header.setText(f"Loading patient {patient_id}...")

        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for 4xx/5xx errors

            data = response.json()

            # Update patient header
            self.patient_header.setText(f"Patient ID: {patient_id}")
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.last_updated.setText(f"Last updated: {current_time}")

            self.display_data(data)
            self.analyze_data(data)

        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Error", f"Failed to fetch data: {str(e)}")
            self.patient_header.setText(f"Patient ID: {patient_id} (Error loading data)")
            self.status_label.setText("Status: Error")
            self.status_label.setStyleSheet("color: #ff3b30;")  # Apple red

        finally:
            # Restore button state
            self.fetch_button.setEnabled(True)
            self.fetch_button.setText("Fetch Data")

    def display_data(self, data):
        """Display patient data in the UI."""
        # Clear previous data
        self.readings_table.setRowCount(0)

        # Add new data
        measurements = data.get("measurements", [])
        self.readings_table.setRowCount(len(measurements))

        for row, measurement in enumerate(measurements):
            # Format timestamp for display
            timestamp = datetime.fromisoformat(measurement["timestamp"].replace("Z", "+00:00"))
            formatted_time = timestamp.strftime("%Y-%m-%d %H:%M:%S")

            # SpO2 value
            spo2 = measurement["spo2"]

            # Status for individual reading
            status = "OK" if spo2 >= 95 else "Warning"

            # Create QTableWidgetItems with proper styling
            time_item = QTableWidgetItem(formatted_time)
            time_item.setTextAlignment(Qt.AlignCenter)
            time_item.setFont(QFont("SF Pro Text, -apple-system, BlinkMacSystemFont, Helvetica, Arial", 13))

            spo2_item = QTableWidgetItem(str(spo2))
            spo2_item.setTextAlignment(Qt.AlignCenter)
            spo2_item.setFont(QFont("SF Pro Text, -apple-system, BlinkMacSystemFont, Helvetica, Arial", 13, QFont.Bold))

            status_item = QTableWidgetItem(status)
            status_item.setTextAlignment(Qt.AlignCenter)
            status_item.setFont(QFont("SF Pro Text, -apple-system, BlinkMacSystemFont, Helvetica, Arial", 13))

            # Apply color-coding
            if spo2 < 95:
                # Apple-style warning: subtle background with icon-like indicator
                status_item.setForeground(QColor("#ff3b30"))  # Apple red
                # We don't set background colors for a cleaner look - Apple UIs rarely use background colors for status
            else:
                status_item.setForeground(QColor("#34c759"))  # Apple green

            self.readings_table.setItem(row, 0, time_item)
            self.readings_table.setItem(row, 1, spo2_item)
            self.readings_table.setItem(row, 2, status_item)

    def analyze_data(self, data):
        """Analyze SpO2 readings and update status."""
        measurements = data.get("measurements", [])
        spo2_values = [m["spo2"] for m in measurements]

        if not spo2_values:
            self.status_label.setText("Status: No data available")
            self.status_label.setStyleSheet("color: #8e8e93;")  # Apple gray
            self.message_group.setEnabled(False)
            return

        lowest_spo2 = min(spo2_values)

        if lowest_spo2 >= 95:
            self.status_label.setText("Status: OK")
            self.status_label.setStyleSheet("""
                color: #34c759;  /* Apple green */
                font-size: 18px;
            """)
            self.message_group.setEnabled(False)
        else:
            self.status_label.setText("Status: Warning")
            self.status_label.setStyleSheet("""
                color: #ff3b30;  /* Apple red */
                font-size: 18px;
            """)
            self.message_group.setEnabled(True)

    def send_message(self):
        """Send clinician advice to the patient."""
        message_text = self.message_input.toPlainText().strip()
        if not message_text:
            QMessageBox.warning(self, "Warning", "Please enter advice before sending.")
            return

        patient_id = self.patient_combo.currentText()
        url = f"https://disp.yxl.ch/rpm/patients/{patient_id}"

        # Create a custom "sending" indicator
        self.send_button.setEnabled(False)
        self.send_button.setText("Sending...")

        try:
            payload = {"message": message_text}
            response = requests.post(url, json=payload)
            response.raise_for_status()

            result = response.json()
            if result.get("stored"):
                # Modern, Apple-style success dialog
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Information)
                msg.setWindowTitle("Success")
                msg.setText("Advice Sent")
                msg.setInformativeText("Your advice has been successfully delivered to the patient.")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.setStyleSheet("""
                    QMessageBox {
                        background-color: white;
                    }
                    QMessageBox QPushButton {
                        background-color: #0071e3;
                        color: white;
                        border-radius: 6px;
                        min-width: 80px;
                        min-height: 30px;
                    }
                """)
                msg.exec()

                self.message_input.clear()
            else:
                QMessageBox.warning(
                    self,
                    "Warning",
                    "Message was received but may not have been stored properly."
                )

        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Error", f"Failed to send advice: {str(e)}")

        finally:
            # Restore button state
            self.send_button.setEnabled(True)
            self.send_button.setText("Send Advice")


def main():
    """
    Main entry point for the Remote Patient Monitoring application.
    Initializes the application, creates the main window, and starts the event loop.
    """
    # Create the application instance
    app = QApplication(sys.argv)

    # Dark mode with white containers
    app.setStyle("Fusion")

    # Set dark color palette with white elements
    palette = app.palette()
    palette.setColor(QPalette.ColorRole.Window, QColor(30, 30, 30))  # Dark background
    palette.setColor(QPalette.ColorRole.WindowText, QColor(240, 240, 240))  # Light text for dark bg
    palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))  # White for input controls
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(245, 245, 245))  # Light alt bg
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(30, 30, 30))
    palette.setColor(QPalette.ColorRole.Text, QColor(30, 30, 30))  # Dark text for white bg controls
    palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))  # Darker buttons
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(240, 240, 240))  # Light text for buttons
    palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(0, 122, 255))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
    app.setPalette(palette)

    # Create and show the main window
    window = RemotePatientMonitoringApp()

    # Set window to center of screen
    screen_geometry = app.primaryScreen().geometry()
    x = (screen_geometry.width() - window.width()) // 2
    y = (screen_geometry.height() - window.height()) // 2
    window.move(x, y)

    window.show()

    # Fetch initial data
    window.fetch_patient_data()

    # Start the event loop
    return app.exec()


# Application entry point
if __name__ == "__main__":
    sys.exit(main())