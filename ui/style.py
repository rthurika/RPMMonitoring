"""
UI styles for the Remote Patient Monitoring application
"""


def get_application_styles():
    """
    Returns the stylesheet for the application

    Returns:
        str: CSS-like stylesheet for Qt
    """
    return """
        QMainWindow {
            background-color: #f0f2f5;
        }
        QLabel {
            color: #1a1a1a;
        }
        QPushButton {
            background-color: #1a1a1a;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 12px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #9b9d9f;
        }
        QPushButton:disabled {
            background-color: #9b9d9f;
            color: #555555;
        }
        QComboBox {
            border: 1px solid #ced4da;
            border-radius: 8px;
            padding: 5px;
            background-color: white;
            color: #1a1a1a;
            min-width: 150px;
        }
        QComboBox QAbstractItemView {
            background-color: white;
            color: #1a1a1a;
            selection-background-color: #7bb9ff;
            selection-color: black;
        }
        QGroupBox {
            font-weight: bold;
            border: 1px solid #d1d9e6;
            border-radius: 10px;
            margin-top: 12px;
            background-color: white;
            color: #1a1a1a;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
            color: #1a1a1a;
        }
        QTableWidget {
            border: none;
            gridline-color: #e9ecef;
            background-color: white;
            color: #1a1a1a;
            alternate-background-color: #f8f9fa;  /* Alternating row colors */
        }
        QTableWidget::item {
            padding: 5px;
            border: none;
            background-color: inherit !important;
        }
        QHeaderView::section {
            background-color: #f8f9fa;
            color: #1a1a1a;
            padding: 8px;
            font-weight: bold;
            border: none;
            border-bottom: 1px solid #dee2e6;
        }
        QTextEdit {
            border: 1px solid #ced4da;
            border-radius: 8px;
            padding: 5px;
            background-color: white;
            color: #1a1a1a;
        }
        QScrollBar:vertical {
            border: none;
            background: #f8f9fa;
            width: 8px;
            margin: 0px;
        }
        QScrollBar::handle:vertical {
            background: #adb5bd;
            min-height: 20px;
            border-radius: 4px;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            border: none;
            background: none;
        }
        QStatusBar {
            background-color: #f8f9fa;
            color: #495057;
        }
    """


modern_light_theme = {
    "background": "#FAFAFA",
    "text": "#212121",
    "primary": "#4CAF50",
    "warning": "#FF9800",
    "border": "#E0E0E0"
}

button_style = """
    QPushButton {
        background-color: #4CAF50;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 8px 16px;
        font-size: 14px;
    }
    QPushButton:hover {
        background-color: #45A049;
    }
    QPushButton:disabled {
        background-color: #CCCCCC;
        color: #666666;
    }
"""
