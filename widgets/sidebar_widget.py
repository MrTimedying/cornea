# widgets/sidebar_widget.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QFrame
from PySide6.QtCore import Qt

class SidebarContentWidget(QWidget):
    """
    A custom widget to hold the contents of the sidebar.
    This is placed *inside* the QDockWidget.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SidebarContent") # Helps with styling/debugging

        # --- Layout for the sidebar content ---
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10) # Add some padding
        layout.setSpacing(15)                    # Space between widgets
        layout.setAlignment(Qt.AlignTop)         # Widgets align to the top

        # --- Example Sidebar Widgets ---
        title_label = QLabel("Analysis Tools")
        title_label.setStyleSheet("font-weight: bold; font-size: 14pt;")
        layout.addWidget(title_label)

        # Add a separator line
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)

        # Example buttons or controls
        button1 = QPushButton("Gait Parameters")
        button2 = QPushButton("Joint Angles")
        button3 = QPushButton("Export Data")
        settings_button = QPushButton("Settings")

        layout.addWidget(button1)
        layout.addWidget(button2)
        layout.addWidget(button3)

        # Add a stretch at the bottom to push everything up
        layout.addStretch(1)

        layout.addWidget(settings_button)

        # --- Connect Signals (Example) ---
        # You would connect these buttons to actual functions later
        # button1.clicked.connect(self.on_gait_params_clicked)
        # button2.clicked.connect(self.on_joint_angles_clicked)

        print("SidebarContentWidget initialized.")

    # --- Example Slot Methods (to be implemented later) ---
    # def on_gait_params_clicked(self):
    #     print("Gait Parameters button clicked")
    #
    # def on_joint_angles_clicked(self):
    #     print("Joint Angles button clicked")

