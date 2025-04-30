# widgets/sidebar_widget.py

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton,
                               QFrame, QComboBox, QSpacerItem, QSizePolicy)
from PySide6.QtCore import Qt, Slot # Import Slot for clarity

class SidebarContentWidget(QWidget):
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
        title_label = QLabel("Analysis Tools")
        title_label.setStyleSheet("font-weight: bold; font-size: 14pt;")
        self.main_layout.addWidget(title_label)

        # --- ComboBox (Needs to be instance variable to connect signal) ---
        self.combo_box = QComboBox()
        self.combo_box.addItem("Gait Analysis", userData="gait") # Add user data for easier mapping
        self.combo_box.addItem("Individual form", userData="form")
        self.combo_box.addItem("Posture Analysis", userData="posture")
        self.combo_box.addItem("FMS Suite", userData="fms")
        self.main_layout.addWidget(self.combo_box) # Add combo box to layout

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        self.main_layout.addWidget(line)

        # --- Container for Dynamic Content ---
        # We'll add buttons related to the combo box selection here
        self.content_layout = QVBoxLayout() # Create a layout for dynamic content
        self.content_layout.setSpacing(10) # Spacing for the dynamic buttons
        # Add this dynamic layout to the main layout
        self.main_layout.addLayout(self.content_layout)

        # --- Static Bottom Elements ---
        self.main_layout.addStretch(1) # Pushes settings button to the bottom

        settings_button = QPushButton("Settings")
        # You might want to make settings_button 'self.settings_button' if you
        # need to access it from other methods later.
        self.main_layout.addWidget(settings_button)

        # --- Connect Signal to Slot ---
        self.combo_box.currentIndexChanged.connect(self.update_sidebar_content)

        # --- Initial Content Population ---
        self.update_sidebar_content(self.combo_box.currentIndex()) # Populate with initial selection

        print("SidebarContentWidget initialized.")

    @Slot(int) # Decorator clarifies this is a slot connected to a signal sending an int
    def update_sidebar_content(self, index):
        """
        Clears the current dynamic content and adds new widgets based
        on the combo box selection.
        """
        print(f"Combo box index changed to: {index}")

        # 1. Clear existing dynamic widgets from the content_layout
        # Iterate backwards while removing items from the layout
        while (item := self.content_layout.takeAt(0)) is not None:
            if item.widget():
                item.widget().deleteLater() # Important: properly delete the widget
            # If you had nested layouts, you'd need to handle item.layout() too

        # 2. Determine selected analysis type (using userData is convenient)
        selected_type = self.combo_box.itemData(index) # Get the userData we stored
        print(f"Selected type (userData): {selected_type}")

        # 3. Define content for each type
        new_buttons = []
        if selected_type == "gait":
            new_buttons = ["Gait Parameters", "Joint Angles", "Temporal-Spatial", "Export Gait Data"]
        elif selected_type == "form":
            new_buttons = ["Key Poses", "Range of Motion", "Compare Trials", "Export Form Data"]
        elif selected_type == "posture":
            new_buttons = ["Alignment Analysis", "Symmetry Check", "Posture Report"]
        elif selected_type == "fms":
            new_buttons = ["Deep Squat", "Hurdle Step", "Inline Lunge", "Shoulder Mobility", "ASLR", "Trunk Stability", "Rotary Stability", "FMS Score"]
        else:
            # Handle unexpected case or default
            label = QLabel("Select an analysis type.")
            self.content_layout.addWidget(label)
            return # Nothing more to add

        # 4. Create and add new buttons to the content_layout
        for button_text in new_buttons:
            button = QPushButton(button_text)
            # TODO: Connect these new buttons' clicked signals to actual actions!
            button.clicked.connect(self.on_dynamic_button_clicked) # Example connection
            self.content_layout.addWidget(button) # Add to the dynamic layout

        # Add a stretch at the end of dynamic content if needed,
        # although the main layout's stretch might be sufficient.
        # self.content_layout.addStretch(1)

    @Slot() # Slot for the dynamically created buttons
    def on_dynamic_button_clicked(self):
        """Handles clicks for any of the dynamically generated buttons."""
        # self.sender() returns the object that emitted the signal (the button)
        button = self.sender()
        if button:
            print(f"Dynamic button clicked: {button.text()}")
            # Add specific logic here based on button.text() or other properties


