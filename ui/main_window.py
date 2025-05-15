"""
Main window for the Remote Patient Monitoring application
"""

from datetime import datetime

from PySide6.QtCore import QTimer
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTableWidgetItem, QMessageBox, QStatusBar

from api.patient_data import fetch_patient_data, send_patient_message
from config import SPO2_THRESHOLD
from ui.components import UIComponents
from ui.style import get_application_styles, button_style


class RPMApp(QMainWindow):
    """
    Main application window for Remote Patient Monitoring
    """

    def __init__(self):
        """Initialize the application window and UI components"""
        super().__init__()
        self.setWindowTitle("Remote Patient Monitoring")
        self.resize(800, 600)
        self.current_patient = None
        self.measurements = []
        self.status = "Unknown"

        self.setStyleSheet(get_application_styles())

        # Set up the main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)

        # Create header with patient selection
        UIComponents.setup_header(self)

        # Create the main content area
        self.main_content = QWidget()
        self.main_content_layout = QHBoxLayout(self.main_content)
        self.main_content_layout.setSpacing(20)
        self.main_layout.addWidget(self.main_content, 1)

        # Setup data view area
        UIComponents.setup_data_view(self)

        # Setup status and message area
        UIComponents.setup_status_message_view(self)

        # Setup status bar
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet("QStatusBar { background-color: #f8f9fa; color: #495057; }")
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

        # Initialize
        self.combobox_patient.setCurrentIndex(0)
        self.fetch_patient_data()

        # Setup auto-refresh
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.fetch_patient_data)
        self.timer.start(30000)  # Refresh every 30 seconds

    def on_patient_changed(self):
        """Handle patient selection changes"""
        self.fetch_patient_data()

    def fetch_patient_data(self):
        """Fetch and display patient data"""
        try:
            patient_id = self.combobox_patient.currentData()
            if patient_id is None:
                return

            self.current_patient = patient_id
            self.refresh_button.setEnabled(False)
            self.refresh_button.setText("Loading...")
            self.status_bar.showMessage("Fetching data...")
            self.patient_info.setText(f"Loading data for Patient {patient_id}...")

            data = fetch_patient_data(patient_id)
            self.measurements = data.get("measurements", [])

            # Update patient info display
            if self.measurements:
                self.patient_info.setText(
                    f"Patient {patient_id}"
                )
            else:
                self.patient_info.setText(f"Patient {patient_id} - No data available")

            self.update_table()
            self.update_status()

            self.refresh_button.setText("Refresh")
            self.refresh_button.setEnabled(True)
            self.send_button.setStyleSheet(button_style)
            self.status_bar.showMessage(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        except Exception as e:
            msg = UIComponents.create_message_box(
                self,
                "Error",
                "Could not fetch patient data",
                str(e),
                QMessageBox.Icon.Critical
            )
            msg.exec_()

            self.refresh_button.setText("Refresh")
            self.refresh_button.setEnabled(True)
            self.status_bar.showMessage(f"Error fetching data: {str(e)}")
            patient_id = self.combobox_patient.currentData()
            self.patient_info.setText(f"Error loading data for Patient {patient_id}")
            self.patient_info.setStyleSheet("""
                background-color: #ffebee;
                padding: 10px;
                border-radius: 8px;
                border: 1px solid #ffcdd2;
                font-size: 14px;
                font-weight: bold;
                color: #d32f2f;
            """)

    def update_table(self):
        """Update the SpO2 readings table"""
        self.table.setStyleSheet("""
            QTableWidget::item {
                background-color: transparent !important;
                border: none;
            }
        """)
        self.table.setRowCount(0)

        for measurement in self.measurements:
            timestamp = measurement.get("timestamp", "")
            spo2 = measurement.get("spo2", 0)

            row_position = self.table.rowCount()
            self.table.insertRow(row_position)

            # Format time
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            formatted_time = dt.strftime("%H:%M, %d %b")

            time_item = QTableWidgetItem(formatted_time)
            spo2_item = QTableWidgetItem(str(spo2))

            status_text = "NORMAL" if spo2 >= SPO2_THRESHOLD else "LOW"
            status_item = QTableWidgetItem(status_text)

            # Set color based on status - with better contrast
            if status_text == "NORMAL":
                status_item = QTableWidgetItem(status_text)
                status_item.setFont(QFont("", -1, QFont.Bold))
                self.table.setItem(row_position, 2, status_item)
                self.table.item(row_position, 2).setBackground(QColor("#e8f5e9"))
                self.table.item(row_position, 2).setForeground(QColor("#2e7d32"))

            elif status_text == "LOW":
                status_item = QTableWidgetItem(status_text)
                status_item.setFont(QFont("", -1, QFont.Bold))
                self.table.setItem(row_position, 2, status_item)
                self.table.item(row_position, 2).setBackground(QColor("#ffebee"))
                self.table.item(row_position, 2).setForeground(QColor("#d32f2f"))

            # Add to table
            self.table.setItem(row_position, 0, time_item)
            self.table.setItem(row_position, 1, spo2_item)
            self.table.setItem(row_position, 2, status_item)

        self.table.resizeColumnsToContents()
        self.table.setColumnWidth(0, max(150, self.table.columnWidth(0)))
        self.table.repaint()

    def update_status(self):
        """Update the overall patient status display"""
        if not self.measurements:
            self.status = "Unknown"
            self.status_label.setText("Status: Unknown")
            self.status_label.setStyleSheet("""
                color: #6c757d; 
                background-color: #f8f9fa; 
                padding: 10px; 
                border-radius: 8px;
            """)
            self.message_text.setEnabled(False)
            self.send_button.setEnabled(False)
            self.message_group.setStyleSheet("QGroupBox { background-color: white; }")
            return

        # Check if any reading is below threshold
        low_reading = False
        for measurement in self.measurements:
            spo2 = measurement.get("spo2", 0)
            if spo2 < SPO2_THRESHOLD:
                low_reading = True
                break

        if low_reading:
            self.status = "Warning"
            self.status_label.setText("WARNING")
            self.status_label.setStyleSheet("""
                color: #721c24;
                background-color: #f8d7da;
                padding: 15px;
                border-radius: 8px;
                font-weight: bold;
                border: 1px solid #f5c6cb;
            """)
            self.message_text.setEnabled(True)
            self.send_button.setEnabled(True)
            # Highlight the message group when warning is active
            self.message_group.setStyleSheet("""
                QGroupBox {
                    background-color: #fff8f8;
                    border: 1px solid #f5c6cb;
                }
                QGroupBox::title {
                    color: #721c24;
                }
            """)
        else:
            self.status = "OK"
            self.status_label.setText("OK")
            # Better contrast for OK status
            self.status_label.setStyleSheet("""
                color: #155724;
                background-color: #d4edda;
                padding: 15px;
                border-radius: 8px;
                font-weight: bold;
                border: 1px solid #c3e6cb;
            """)
            self.message_text.setEnabled(False)
            self.send_button.setEnabled(False)
            self.message_group.setStyleSheet("QGroupBox { background-color: white; }")

    def send_message(self):
        """Send a clinical advice message to the patient"""
        if not self.current_patient or self.status != "Warning":
            return

        message = self.message_text.toPlainText().strip()
        if not message:
            # Better warning message dialog
            msg = UIComponents.create_message_box(
                self,
                "Missing Message",
                "Please enter advice for the patient",
                "The message field cannot be empty.",
                QMessageBox.Icon.Warning
            )
            msg.exec_()
            return

        try:
            self.send_button.setEnabled(False)
            self.send_button.setText("Sending...")
            self.status_bar.showMessage("Sending message...")

            result = send_patient_message(self.current_patient, message)

            if result.get("stored", False):
                msg = UIComponents.create_message_box(
                    self,
                    "Success",
                    "Message Sent Successfully",
                    f"Clinical advice has been sent to Patient {self.current_patient}."
                )
                msg.exec_()

                self.message_text.clear()
                self.status_bar.showMessage("Message sent successfully")
            else:

                msg = UIComponents.create_message_box(
                    self,
                    "Warning",
                    "Message Not Stored",
                    "The server received the message but did not confirm storage.",
                    QMessageBox.Icon.Warning
                )
                msg.exec_()
                self.status_bar.showMessage("Message received but not confirmed stored")

            self.send_button.setText("Send Advice")
            self.send_button.setEnabled(True)

        except Exception as e:
            msg = UIComponents.create_message_box(
                self,
                "Error",
                "Could not send message",
                str(e),
                QMessageBox.Icon.Critical
            )
            msg.exec_()

            self.send_button.setText("Send Advice")
            self.send_button.setEnabled(True)
            self.status_bar.showMessage(f"Error sending message: {str(e)}")
