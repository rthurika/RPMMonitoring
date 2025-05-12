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
                               QMessageBox, QHeaderView)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QFont


class RemotePatientMonitoringApp(QMainWindow):
    """Main application window for the Remote Patient Monitoring system."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Remote Patient Monitoring")
        self.setGeometry(100, 100, 800, 600)

        # Main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

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

    def setup_patient_header(self):
        """Create the header showing current patient information."""
        header_group = QGroupBox("Current Patient")
        header_layout = QHBoxLayout()

        self.patient_header = QLabel("No patient data loaded")
        self.patient_header.setFont(QFont("Arial", 16, QFont.Bold))
        self.patient_header.setAlignment(Qt.AlignCenter)
        self.last_updated = QLabel("Last updated: Never")
        self.last_updated.setAlignment(Qt.AlignRight)

        header_layout.addWidget(self.patient_header)
        header_layout.addWidget(self.last_updated)

        header_group.setLayout(header_layout)
        self.main_layout.addWidget(header_group)

    def setup_patient_selection(self):
        """Create the patient selection controls."""
        patient_group = QGroupBox("Patient Selection")
        patient_layout = QHBoxLayout()

        self.patient_label = QLabel("Select Patient ID:")
        self.patient_combo = QComboBox()
        self.patient_combo.addItems(["1", "2", "3", "10", "42"])
        self.fetch_button = QPushButton("Fetch Data")
        self.fetch_button.clicked.connect(self.fetch_patient_data)

        patient_layout.addWidget(self.patient_label)
        patient_layout.addWidget(self.patient_combo)
        patient_layout.addWidget(self.fetch_button)
        patient_layout.addStretch()

        patient_group.setLayout(patient_layout)
        self.main_layout.addWidget(patient_group)

    def setup_data_display(self):
        """Create the data display table."""
        data_group = QGroupBox("SpO2 Readings")
        data_layout = QVBoxLayout()

        # Table for readings
        self.readings_table = QTableWidget(0, 3)
        self.readings_table.setHorizontalHeaderLabels(["Timestamp", "SpO2 (%)", "Status"])
        self.readings_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.readings_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.readings_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)

        data_layout.addWidget(self.readings_table)
        data_group.setLayout(data_layout)
        self.main_layout.addWidget(data_group)

    def setup_status_display(self):
        """Create the overall status display section."""
        status_group = QGroupBox("Overall Status")
        status_layout = QHBoxLayout()

        self.status_label = QLabel("Status: Not analyzed yet")
        self.status_label.setFont(QFont("Arial", 14, QFont.Bold))
        status_layout.addWidget(self.status_label)

        status_group.setLayout(status_layout)
        self.main_layout.addWidget(status_group)

    def setup_message_section(self):
        """Create the message input and sending section."""
        self.message_group = QGroupBox("Send Advice to Patient")
        message_layout = QVBoxLayout()

        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("Enter your advice for the patient here...")
        self.message_input.setMaximumHeight(100)

        self.send_button = QPushButton("Send Advice")
        self.send_button.clicked.connect(self.send_message)

        message_layout.addWidget(self.message_input)
        message_layout.addWidget(self.send_button)

        self.message_group.setLayout(message_layout)
        self.main_layout.addWidget(self.message_group)

    def fetch_patient_data(self):
        """Fetch patient data from the API."""
        patient_id = self.patient_combo.currentText()
        url = f"https://disp.yxl.ch/rpm/patients/{patient_id}"

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
            status_color = QColor(0, 150, 0) if status == "OK" else QColor(200, 0, 0)

            # Add to table
            time_item = QTableWidgetItem(formatted_time)
            spo2_item = QTableWidgetItem(str(spo2))
            status_item = QTableWidgetItem(status)

            time_item.setTextAlignment(Qt.AlignCenter)
            spo2_item.setTextAlignment(Qt.AlignCenter)
            status_item.setTextAlignment(Qt.AlignCenter)

            status_item.setForeground(status_color)

            if spo2 < 95:
                spo2_item.setBackground(QColor(255, 200, 200))

            self.readings_table.setItem(row, 0, time_item)
            self.readings_table.setItem(row, 1, spo2_item)
            self.readings_table.setItem(row, 2, status_item)

    def analyze_data(self, data):
        """Analyze SpO2 readings and update status."""
        measurements = data.get("measurements", [])
        spo2_values = [m["spo2"] for m in measurements]

        if not spo2_values:
            self.status_label.setText("Status: No data available")
            self.message_group.setEnabled(False)
            return

        lowest_spo2 = min(spo2_values)

        if lowest_spo2 >= 95:
            status = "OK"
            status_color = QColor(0, 150, 0)
            self.status_label.setText(f"Status: OK (All SpO2 readings ≥ 95%)")
            self.message_group.setEnabled(False)
        else:
            status = "Warning"
            status_color = QColor(200, 0, 0)
            self.status_label.setText(f"Status: Warning (SpO2 reading < 95% detected)")
            self.message_group.setEnabled(True)

        self.status_label.setStyleSheet(f"color: {status_color.name()}")

    def send_message(self):
        """Send clinician advice to the patient."""
        message_text = self.message_input.toPlainText().strip()
        if not message_text:
            QMessageBox.warning(self, "Warning", "Please enter advice before sending.")
            return

        patient_id = self.patient_combo.currentText()
        url = f"https://disp.yxl.ch/rpm/patients/{patient_id}"

        try:
            payload = {"message": message_text}
            response = requests.post(url, json=payload)
            response.raise_for_status()

            result = response.json()
            if result.get("stored"):
                QMessageBox.information(
                    self,
                    "Success",
                    "Advice sent successfully to the patient."
                )
                self.message_input.clear()
            else:
                QMessageBox.warning(
                    self,
                    "Warning",
                    "Message was received but may not have been stored properly."
                )

        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Error", f"Failed to send advice: {str(e)}")


def main():
    """
    Main entry point for the Remote Patient Monitoring application.
    Initializes the application, creates the main window, and starts the event loop.
    """
    # Create the application instance
    app = QApplication(sys.argv)

    # Apply styling
    app.setStyle("Fusion")

    # Create and show the main window
    window = RemotePatientMonitoringApp()
    window.show()

    # Fetch initial data
    window.fetch_patient_data()

    # Start the event loop
    return app.exec()


# Application entry point
if __name__ == "__main__":
    sys.exit(main())