import sys
import cv2
import numpy as np
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QDockWidget
)
from PySide6.QtCore import Qt, QThread, Slot
from PySide6.QtGui import QImage, QPixmap
from widgets.databar_widget import DatabarContentWidget
try:
    from widgets.sidebar_widget import SidebarContentWidget
except ImportError as e:
    print(f"Error importing SidebarContentWidget: {e}")
    print("Make sure 'widgets/sidebar_widget.py' exists and the 'widgets' folder is in your Python path.")
    # Provide a fallback dummy class if needed for the app to run partially
    class SidebarContentWidget(QWidget):
        def __init__(self, parent=None):
            super().__init__(parent)
            layout = QVBoxLayout(self)
            layout.addWidget(QLabel("Error: Sidebar content failed to load."))
            print("Using dummy SidebarContentWidget due to import error.")

from camera_worker import CameraWorker


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Initialize storage first
        self._widgets = {}
        print(f"Debug: Widget dictionary initialized: {self._widgets}")
        
        # --- Camera Thread Variables ---
        self.camera_thread = None
        self.camera_worker = None
        self.is_camera_running = False

        # Window setup
        self.setWindowTitle("Gait Analyzer")
        # Increased default width slightly to accommodate sidebar comfortably
        self.setGeometry(100, 100, 950, 650)

        # --- Central Widget Setup ---
        # The central widget will primarily hold the video feed
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        # Layout for the central widget (video + button below)
        self.central_layout = QVBoxLayout(central_widget) # Renamed for clarity
        self.central_layout.setContentsMargins(5, 5, 5, 5) # Add some margin around video/button area

        # Video Display Label
        self.video_label = QLabel("Press 'Start Camera' to begin")
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setStyleSheet("border: 1px solid black; background-color: #dddddd;")
        self.video_label.setMinimumSize(640, 480)
        # Set size policy to expanding so it takes available space
        # self.video_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Start/Stop Button
        self.start_stop_button = QPushButton("Start Camera")
        self.start_stop_button.clicked.connect(self.toggle_camera)
        # Set a fixed or maximum width for the button if desired
        # self.start_stop_button.setMaximumWidth(200)

        # Add widgets to central layout
        self.central_layout.addWidget(self.video_label) # Video takes most space
        self.central_layout.addWidget(self.start_stop_button, alignment=Qt.AlignCenter) # Button centered below

        # --- Create and Add Sidebar ---
        self.create_sidebar()
        self.create_databar() # <-- *** ADDED THIS CALL ***

        # --- Status Bar ---
        self.statusBar().showMessage("Ready") # Good practice to have a status bar

        print("Main window initialized.")

    @property
    def databar_content(self):
        """Safe access to databar widget"""
        return self._widgets.get('databar')

    def create_sidebar(self):
        print("Creating sidebar...")
        self.sidebar_dock = QDockWidget("Tools", self) # Title bar of the dock
        self.sidebar_dock.setObjectName("SidebarDockWidget")
        self.sidebar_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        try:
            sidebar_content = SidebarContentWidget(self.sidebar_dock) 
            self.sidebar_dock.setWidget(sidebar_content)
        except Exception as e:
             print(f"Error creating or setting SidebarContentWidget: {e}")
             error_label = QLabel(f"Error loading sidebar content:\n{e}", self.sidebar_dock)
             self.sidebar_dock.setWidget(error_label)


        # Add the dock widget to the main window
        self.addDockWidget(Qt.LeftDockWidgetArea, self.sidebar_dock)
        print("Sidebar added to the main window.")

    def create_databar(self):
        print("Creating data widget")
        self.databar_dock = QDockWidget("Tools", self)
        self.databar_dock.setObjectName("DataOutputWidget")
        self.databar_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        try:
            print("Creating DatabarContentWidget instance...")
            # Create and store widget with explicit parent
            databar_widget = DatabarContentWidget(parent=self)
            print(f"Debug: Created databar_content - type: {type(databar_widget)}")
            print(f"Debug: databar_content value: {databar_widget}")
            
            # Store in our widgets dictionary
            self._widgets['databar'] = databar_widget
            # Set as dock widget content
            self.databar_dock.setWidget(databar_widget)
            
            print("DatabarContentWidget set as dock widget")
            print(f"Debug: Widget parent after setting: {databar_widget.parent()}")
            print(f"Debug: Is widget valid: {bool(databar_widget)}")
        except Exception as e:
            print(f"Error creating or setting DatabarContentWidget: {e}")
            error_label = QLabel(f"Error loading data content:\n{e}", self.databar_dock)
            self.databar_dock.setWidget(error_label)


        # Add the dock widget to the main window
        self.addDockWidget(Qt.RightDockWidgetArea, self.databar_dock)
        print(f"Data output bar added to the main window. Final databar_content: {self.databar_content}")
        print(f"Debug: Final widget from dictionary: {self._widgets.get('databar')}")


    def toggle_camera(self):
        """Starts or stops the camera thread."""
        if not self.is_camera_running:
            self.start_camera_thread()
        else:
            self.stop_camera_thread()

    def start_camera_thread(self):
        """Creates, configures, and starts the camera worker thread."""
        print("Attempting to start camera thread...")
        if self.camera_thread is not None and self.camera_thread.isRunning():
             print("Warning: Camera thread already seems to be running.")
             return

        # Clear previous thread/worker just in case (belt and suspenders)
        if self.camera_thread:
            self.camera_thread.quit()
            self.camera_thread.wait()

        self.camera_thread = QThread(self)
        # Pass camera index, could be configurable later
        self.camera_worker = CameraWorker(camera_index=0)

        self.camera_worker.moveToThread(self.camera_thread)

        # Debug prints to check databar_content state
        databar_widget = self.databar_content
        print(f"Debug: databar_content property value: {databar_widget}")
        print(f"Debug: databar_content property type: {type(databar_widget)}")
        print(f"Debug: Raw widget dictionary value: {self._widgets.get('databar')}")
        
        # Connect signals/slots
        self.camera_thread.started.connect(self.camera_worker.run)
        self.camera_worker.frame_ready.connect(self.update_video_label)
        
        # Use the databar widget from our property getter
        if databar_widget is not None:
            print("Connecting landmarks_ready signal to databar widget")
            self.camera_worker.landmarks_ready.connect(databar_widget.update_landmarks_display)
        else:
            print("Warning: DatabarContentWidget instance is None, cannot connect landmarks signal.")
        self.camera_worker.finished.connect(self.on_camera_worker_finished)
        self.camera_worker.error.connect(self.on_camera_error)

        # Proper cleanup connections
        self.camera_worker.finished.connect(self.camera_thread.quit)
        self.camera_thread.finished.connect(self.camera_worker.deleteLater)
        self.camera_thread.finished.connect(self.camera_thread.deleteLater)
        # Also ensure thread reference is cleared on finish
        self.camera_thread.finished.connect(self._clear_thread_references)


        self.camera_thread.start()

        self.is_camera_running = True
        self.start_stop_button.setText("Stop Camera")
        self.start_stop_button.setEnabled(True)
        self.statusBar().showMessage("Camera Running...")
        print("Camera thread started signal sent.")


    def stop_camera_thread(self):
        """Signals the camera worker to stop and handles UI state."""
        print("Attempting to stop camera thread...")
        if self.camera_worker:
            self.camera_worker.stop() # Signal the worker object to stop its loop

        # Update UI immediately for responsiveness
        self.start_stop_button.setText("Stopping...")
        self.start_stop_button.setEnabled(False)
        self.statusBar().showMessage("Stopping Camera...")
        # The worker finishing will trigger on_camera_worker_finished for final UI state


    @Slot(np.ndarray)
    def update_video_label(self, frame):
        """Updates the QLabel with the new frame received from the worker."""
        try:
            if frame is None or frame.size == 0:
                print("Warning: Received empty frame in update_video_label.")
                return # Don't process empty frames

            # Convert BGR (OpenCV) to RGB (Qt)
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w

            # Create QImage
            qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)

            # Create QPixmap from QImage
            qt_pixmap = QPixmap.fromImage(qt_image)

            # Scale pixmap to fit the label while maintaining aspect ratio
            scaled_pixmap = qt_pixmap.scaled(self.video_label.size(),
                                              Qt.KeepAspectRatio,
                                              Qt.SmoothTransformation)

            # Set the pixmap on the label
            self.video_label.setPixmap(scaled_pixmap)
        except cv2.error as e:
             print(f"OpenCV Error updating video label: {e}")
             # Maybe show error on label itself if conversion fails often
             # self.video_label.setText(f"Display Error: {e}")
        except Exception as e:
            # Catch potential errors during QImage/QPixmap creation or scaling
            print(f"Error updating video label: {e}")
            # Optionally reset label or show an error message
            self.video_label.setText(f"Error displaying frame")


    @Slot()
    def on_camera_worker_finished(self):
        """Cleans up and resets state after the camera worker finishes."""
        print("Camera worker finished signal received in main thread.")
        self._reset_camera_ui()


    @Slot(str)
    def on_camera_error(self, error_message):
        """Displays camera errors in the UI and resets state."""
        print(f"Received camera error signal in main thread: {error_message}")
        self.video_label.setText(f"Camera Error: {error_message}")
        self.statusBar().showMessage(f"Error: {error_message}")
        self._reset_camera_ui()
        # Make sure thread/worker are cleaned up even on error path
        # Note: The finished signal should still emit from worker even after error signal,
        # which triggers _clear_thread_references via thread.finished. If not, add cleanup here.


    def _reset_camera_ui(self):
        """Resets the UI elements related to the camera state."""
        print("Resetting camera UI elements.")
        self.is_camera_running = False
        self.start_stop_button.setText("Start Camera")
        self.start_stop_button.setEnabled(True)
        # Don't reset label text here if an error message is showing
        if "Error" not in self.video_label.text():
            self.video_label.setText("Camera Stopped. Press 'Start Camera'.")
            self.video_label.setPixmap(QPixmap()) # Clear the pixmap explicitly
        if "Error" not in self.statusBar().currentMessage():
             self.statusBar().showMessage("Camera Stopped.")


    @Slot()
    def _clear_thread_references(self):
        """Slot connected to QThread.finished to clear references."""
        print("QThread finished signal received. Clearing references.")
        self.camera_thread = None
        self.camera_worker = None
        print("Camera thread and worker references cleared.")


    def closeEvent(self, event):
        """Ensures the camera thread is stopped cleanly when the window closes."""
        print("Close event triggered. Stopping camera if running...")
        if self.is_camera_running and self.camera_worker:
            print("Requesting camera worker stop...")
            self.camera_worker.stop()  # Signal the worker loop to end

            # Store local reference to thread before potential cleanup
            camera_thread = self.camera_thread
            if camera_thread and camera_thread.isRunning():
                print("Waiting for camera thread to finish...")
                # Increased timeout slightly, adjust if needed
                finished = camera_thread.wait(5000)  # 5 seconds timeout
                if not finished:
                    print("Warning: Camera thread did not finish gracefully on close. Terminating.")
                    camera_thread.terminate()  # Force stop if wait fails
                    camera_thread.wait()  # Wait after terminate ensure resources are released
                else:
                    print("Camera thread finished gracefully on close.")
            else:
                print("Camera thread was not running or already finished when closing.")
        else:
            print("Camera was not running on close.")

        print("Accepting close event.")
        event.accept()  # Accept the close event to allow window to close


if __name__ == "__main__":
    print("Initializing application...")
    # Enable High DPI support - Important for modern displays
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)

    print("Creating main window...")
    window = MainWindow()
    window.show() # Display the window

    print("Starting application event loop...")
    exit_code = app.exec() # Start the Qt event loop
    print(f"Application event loop finished with exit code: {exit_code}")
    sys.exit(exit_code) # Exit the script
