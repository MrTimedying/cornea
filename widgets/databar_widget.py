# widgets/sidebar_widget.py

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton,
                               QFrame, QComboBox, QSpacerItem, QSizePolicy)
from PySide6.QtCore import Qt, Slot # Import Slot for clarity

class DatabarContentWidget(QWidget):
    """
    A custom widget to hold the contents of the sidebar, with dynamic content
    based on the QComboBox selection.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SidebarContent")

        # --- Main Layout ---
        self.main_layout = QVBoxLayout(self) # Store main layout reference
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(15)
        self.main_layout.setAlignment(Qt.AlignTop)

        # --- Static Top Elements ---
        title_label = QLabel("Analysis Output")
        title_label.setStyleSheet("font-weight: bold; font-size: 14pt;")
        self.main_layout.addWidget(title_label)


        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        self.main_layout.addWidget(line)

   


