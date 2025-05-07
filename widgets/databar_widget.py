# widgets/sidebar_widget.py or widgets/databar_widget.py (depending on intended use)

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton,
                               QFrame, QComboBox, QSpacerItem, QSizePolicy,
                               QPlainTextEdit, QScrollArea) # Added QPlainTextEdit, QScrollArea for display
from PySide6.QtCore import Qt, Slot # Import Slot for clarity

class DatabarContentWidget(QWidget): # Or SidebarContentWidget if this is truly the sidebar
    """
    A custom widget to hold the contents of a data display area, potentially
    including MediaPipe pose landmark information.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ContentWidget") # Use a more general object name

        # --- Main Layout ---
        self.main_layout = QVBoxLayout(self) # Store main layout reference
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(15)
        self.main_layout.setAlignment(Qt.AlignTop)

        # --- Static Top Elements ---
        # Renamed to be more general if used for different outputs
        title_label = QLabel("Analysis/Data Output")
        title_label.setStyleSheet("font-weight: bold; font-size: 14pt;")
        self.main_layout.addWidget(title_label)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        self.main_layout.addWidget(line)

        # --- Section for Landmark Display ---
        # Added the creation and layout for the landmark display elements
        self.landmarks_title_label = QLabel("Pose Landmarks (first few):")
        self.main_layout.addWidget(self.landmarks_title_label)

        # Use a QPlainTextEdit to display landmark coordinates
        self.landmarks_text_edit = QPlainTextEdit()
        self.landmarks_text_edit.setReadOnly(True) # Make it read-only
        # Set size policy so it expands to take available space
        self.landmarks_text_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.main_layout.addWidget(self.landmarks_text_edit)

        # --- You can add other display elements here ---
        # e.g., Labels for specific angle values, graphs, etc.
        # self.angle_label = QLabel("Calculated Angle:")
        # self.main_layout.addWidget(self.angle_label)

        # Add stretch at the end to push content to the top
        self.main_layout.addStretch(1)


        print("Widget content initialized.")

    @Slot(object) # Decorator specifying this method is a slot receiving an object
    def update_landmarks_display(self, pose_landmarks_object):
        """
        Receives pose landmarks from the worker and updates the display.
        This slot is called automatically when the landmarks_ready signal is emitted.
        """
        # print("Widget: update_landmarks_display slot called.") # Debug print

        # Check if the landmarks_text_edit was successfully created
        if not hasattr(self, 'landmarks_text_edit') or self.landmarks_text_edit is None:
             print("Widget: landmarks_text_edit not initialized. Cannot update display.")
             return # Cannot update if the widget doesn't exist

        if pose_landmarks_object is None:
            self.landmarks_text_edit.setPlainText("No pose landmarks detected.")
            return

        # Check if the object has the expected 'landmark' attribute (it should be a list-like structure)
        if not hasattr(pose_landmarks_object, 'landmark'):
             self.landmarks_text_edit.setPlainText("Received invalid landmark data structure.")
             print("Widget: Received object without 'landmark' attribute.") # Debug print
             return

        # Prepare text to display
        display_text = "Pose Landmarks:\n"
        # Iterate through the first few landmarks to display (e.g., first 10)
        # Ensure we don't try to access more landmarks than exist
        num_landmarks_to_display = min(len(pose_landmarks_object.landmark), 10) # Display up to 10
        # Add more names if displaying more landmarks
        landmark_names = [
            "Nose", "Left Eye Inner", "Left Eye", "Left Eye Outer", "Right Eye Inner",
            "Right Eye", "Right Eye Outer", "Left Ear", "Right Ear", "Mouth Left",
            "Mouth Right", "Left Shoulder", "Right Shoulder", "Left Elbow", "Right Elbow",
            "Left Wrist", "Right Wrist", "Left Pinky", "Right Pinky", "Left Index",
            "Right Index", "Left Thumb", "Right Thumb", "Left Hip", "Right Hip",
            "Left Knee", "Right Knee", "Left Ankle", "Right Ankle", "Left Heel",
            "Right Heel", "Left Foot Index", "Right Foot Index"
        ]


        for i in range(num_landmarks_to_display):
            landmark = pose_landmarks_object.landmark[i]
            # Use landmark name if available, otherwise use index
            name = landmark_names[i] if i < len(landmark_names) else f"Landmark {i}"
            display_text += f"{name}: x={landmark.x:.4f}, y={landmark.y:.4f}, z={landmark.z:.4f}, visibility={landmark.visibility:.2f}\n"

        # Indicate if there are more landmarks than displayed
        if len(pose_landmarks_object.landmark) > num_landmarks_to_display:
             display_text += f"... + {len(pose_landmarks_object.landmark) - num_landmarks_to_display} more landmarks (total {len(pose_landmarks_object.landmark)})\n"


        # Update the text edit widget with the new data
        self.landmarks_text_edit.setPlainText(display_text)

        # --- You would add logic here to calculate and display specific angles ---
        # This involves accessing the coordinates of relevant landmarks (e.g., elbow = landmark[13])
        # and performing geometric calculations.
        # Remember to handle potential IndexError if fewer landmarks are detected than expected.
        # Example (conceptual, assuming you have the angle calculation function):
        # if len(pose_landmarks_object.landmark) > 15: # Ensure enough landmarks for left elbow angle
        #     try:
        #         left_shoulder = pose_landmarks_object.landmark[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER.value]
        #         left_elbow = pose_landmarks_object.landmark[mp.solutions.pose.PoseLandmark.LEFT_ELBOW.value]
        #         left_wrist = pose_landmarks_object.landmark[mp.solutions.pose.PoseLandmark.LEFT_WRIST.value]
        #         # You would need to implement calculate_angle_from_landmarks
        #         # angle = calculate_angle_from_landmarks(left_shoulder, left_elbow, left_wrist)
        #         # Apply smoothing (EMA) to the angle before displaying
        #         # self.smoothed_left_elbow_angle = self.apply_smoothing(angle, self.smoothed_left_elbow_angle) # Assuming you have smoothing state and method
        #         # self.angle_label.setText(f"Left Elbow Angle: {self.smoothed_left_elbow_angle:.2f}°")
        #     except IndexError:
        #         print("Not enough landmarks detected to calculate left elbow angle.")
        #     except Exception as e:
        #          print(f"Error calculating or displaying angle: {e}")

    # Add a placeholder for your smoothing method if you implement angle calculation later
    # def apply_smoothing(self, new_value, current_smoothed_value, alpha=0.3):
    #     if current_smoothed_value is None:
    #         return new_value
    #     return alpha * new_value + (1 - alpha) * current_smoothed_value
