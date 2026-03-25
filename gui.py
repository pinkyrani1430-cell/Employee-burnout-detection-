from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QFrame, QLabel, QPushButton, QTextEdit, QProgressBar)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QKeyEvent
from keyboard_tracker import KeyboardTracker
from stress_model import StressModel

class ModernCard(QFrame):
    """Custom widget for dashboard-style cards"""
    def __init__(self, title, value, unit="", parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.layout = QVBoxLayout(self)
        
        self.title_label = QLabel(title)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setObjectName("cardTitle")
        
        self.value_label = QLabel(f"{value} {unit}")
        self.value_label.setAlignment(Qt.AlignCenter)
        self.value_label.setObjectName("cardValue")
        
        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.value_label)

    def update_value(self, value, unit=""):
        self.value_label.setText(f"{value} {unit}")

class BurnoutApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Employee Burnout Detection System")
        self.resize(900, 700)
        
        self.tracker = KeyboardTracker()
        self.is_dark_theme = True
        
        # Setup UI
        self.init_ui()
        self.apply_theme()
        
        # Timer for real-time updates (every 1 second)
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.refresh_stats)
        self.update_timer.start(1000)

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setSpacing(20)
        self.main_layout.setContentsMargins(30, 30, 30, 30)

        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Burnout Detection Dashboard")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        
        self.theme_btn = QPushButton("Toggle Theme")
        self.theme_btn.setFixedWidth(120)
        self.theme_btn.clicked.connect(self.toggle_theme)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.theme_btn)
        self.main_layout.addLayout(header_layout)

        # Stats Row - Typing Speed
        stats_layout = QHBoxLayout()
        self.speed_card = ModernCard("Typing Speed", "0.0", "KPS")
        
        stats_layout.addStretch()
        stats_layout.addWidget(self.speed_card)
        stats_layout.addStretch()
        self.main_layout.addLayout(stats_layout)

        # Stress Level Section
        stress_section = QFrame()
        stress_section.setObjectName("stressSection")
        stress_layout = QVBoxLayout(stress_section)
        
        stress_header = QHBoxLayout()
        stress_label = QLabel("Current Stress Level:")
        stress_label.setFont(QFont("Segoe UI", 12))
        self.level_display = QLabel("Idle / Waiting for typing")
        self.level_display.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.level_display.setStyleSheet("color: #888888;")
        
        stress_header.addWidget(stress_label)
        stress_header.addWidget(self.level_display)
        stress_header.addStretch()
        stress_layout.addLayout(stress_header)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(15)
        stress_layout.addWidget(self.progress_bar)
        
        self.main_layout.addWidget(stress_section)

        # Typing Area
        typing_label = QLabel("Typing Analysis Area")
        typing_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.main_layout.addWidget(typing_label)
        
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Start typing here to analyze behavior...")
        self.text_edit.setFont(QFont("Consolas", 12))
        self.text_edit.installEventFilter(self) # Capture key presses from the widget
        self.main_layout.addWidget(self.text_edit)

        # Control Buttons
        btn_layout = QHBoxLayout()
        self.start_btn = QPushButton("Start Monitoring")
        self.stop_btn = QPushButton("Stop Monitoring")
        self.start_btn.setObjectName("startBtn")
        self.stop_btn.setObjectName("stopBtn")
        
        self.start_btn.clicked.connect(self.start_monitoring)
        self.stop_btn.clicked.connect(self.stop_monitoring)
        
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.stop_btn)
        self.main_layout.addLayout(btn_layout)

    def eventFilter(self, obj, event):
        """Captures key presses only when they happen inside the QTextEdit"""
        if obj is self.text_edit and event.type() == QKeyEvent.KeyPress:
            if self.tracker.is_monitoring:
                # Record the character typed
                self.tracker.record_character()
        return super().eventFilter(obj, event)

    def start_monitoring(self):
        """Resets and starts the monitoring process"""
        self.tracker.start()
        self.text_edit.clear()
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        # Reset UI to Idle state immediately
        self.speed_card.update_value("0.0", "KPS")
        self.level_display.setText("Idle")
        self.level_display.setStyleSheet("color: #888888;")
        self.progress_bar.setValue(0)

    def stop_monitoring(self):
        self.tracker.stop()
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

    def refresh_stats(self):
        """Updates the UI every 1 second while monitoring is active"""
        if not self.tracker.is_monitoring:
            return
            
        # Get KPS from tracker using sliding window
        kps = self.tracker.get_kps()
        
        # Update Typing Speed Card
        self.speed_card.update_value(f"{kps:.2f}", "KPS")
        
        # Calculate Stress using the sliding window model
        score, level, color = StressModel.calculate_stress(kps)
        
        # Update Progress Bar and Level Label
        self.progress_bar.setValue(score)
        self.level_display.setText(level)
        self.level_display.setStyleSheet(f"color: {color};")
        self.progress_bar.setStyleSheet(f"""
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 5px;
            }}
        """)

    def toggle_theme(self):
        self.is_dark_theme = not self.is_dark_theme
        self.apply_theme()

    def apply_theme(self):
        if self.is_dark_theme:
            bg = "#2b2b2b"
            card_bg = "#3c3f41"
            text = "#ffffff"
            secondary_text = "#bbbbbb"
            border = "#555555"
        else:
            bg = "#ffffff"
            card_bg = "#f5f5f5"
            text = "#333333"
            secondary_text = "#666666"
            border = "#dddddd"

        self.setStyleSheet(f"""
            QMainWindow {{ background-color: {bg}; }}
            QLabel {{ color: {text}; }}
            #cardTitle {{ color: {secondary_text}; font-size: 14px; font-weight: bold; }}
            #cardValue {{ color: {text}; font-size: 24px; font-weight: bold; }}
            QFrame {{ 
                background-color: {card_bg}; 
                border: 1px solid {border}; 
                border-radius: 10px; 
            }}
            #stressSection {{ padding: 10px; }}
            QTextEdit {{ 
                background-color: {card_bg}; 
                color: {text}; 
                border: 1px solid {border}; 
                border-radius: 5px;
                padding: 10px;
            }}
            QPushButton {{
                background-color: #0078D7;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: #005a9e; }}
            QPushButton:disabled {{ background-color: #cccccc; }}
            #stopBtn {{ background-color: #d83b01; }}
            #stopBtn:hover {{ background-color: #a82a01; }}
            QProgressBar {{
                background-color: {border};
                border-radius: 7px;
                text-align: center;
            }}
        """)
