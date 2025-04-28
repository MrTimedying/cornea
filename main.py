import sys
import cv2
import numpy as np
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton
)
from PySide6.QtCore import Qt, QThread, Slot  
from PySide6.QtGui import QImage, QPixmap


from camera_worker import CameraWorker


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Gait Analyzer")
        self.setGeometry(100, 100, 800, 650) 

        
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        self.layout = QVBoxLayout(central_widget)

        
        self.video_label = QLabel("Press 'Start Camera' to begin")
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setStyleSheet("border: 1px solid black; background-color: #dddddd;")
        self.video_label.setMinimumSize(640, 480)

        self.start_stop_button = QPushButton("Start Camera")
        self.start_stop_button.clicked.connect(self.toggle_camera) 

        
        self.layout.addWidget(self.video_label)
        self.layout.addWidget(self.start_stop_button)

        
        self.camera_thread = None 
        self.camera_worker = None 
        self.is_camera_running = False

        print("Main window initialized.")

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

        self.camera_thread = QThread(self) 
        self.camera_worker = CameraWorker(camera_index=0) 

        self.camera_worker.moveToThread(self.camera_thread)

        self.camera_thread.started.connect(self.camera_worker.run)

        self.camera_worker.frame_ready.connect(self.update_video_label)
        self.camera_worker.finished.connect(self.on_camera_worker_finished) 
        self.camera_worker.error.connect(self.on_camera_error)

        self.camera_worker.finished.connect(self.camera_thread.quit)

        
        self.camera_thread.finished.connect(self.camera_worker.deleteLater)
        self.camera_thread.finished.connect(self.camera_thread.deleteLater)


        self.camera_thread.start()

        self.is_camera_running = True
        self.start_stop_button.setText("Stop Camera")
        self.start_stop_button.setEnabled(True) 
        print("Camera thread started signal sent.")


    def stop_camera_thread(self):
        """Signals the camera worker to stop and handles UI state."""
        print("Attempting to stop camera thread...")
        if self.camera_worker:
            self.camera_worker.stop()

        self.start_stop_button.setText("Stopping...")
        self.start_stop_button.setEnabled(False) 


    @Slot(np.ndarray) 
    def update_video_label(self, frame):
        """Updates the QLabel with the new frame received from the worker."""
        try:
            
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)

           
            qt_pixmap = QPixmap.fromImage(qt_image)

            
            scaled_pixmap = qt_pixmap.scaled(self.video_label.size(),
                                              Qt.KeepAspectRatio,
                                              Qt.SmoothTransformation)

            
            self.video_label.setPixmap(scaled_pixmap)
        except Exception as e:
            print(f"Error updating video label: {e}")



    @Slot()
    def on_camera_worker_finished(self):
        """Cleans up and resets state after the camera worker finishes."""
        print("Camera worker finished signal received.")
        self.is_camera_running = False
        self.start_stop_button.setText("Start Camera")
        self.start_stop_button.setEnabled(True)

        self.camera_thread = None
        self.camera_worker = None
        print("Camera thread and worker references reset.")


    @Slot(str)
    def on_camera_error(self, error_message):
        """Displays camera errors in the UI and resets state."""
        print(f"Received camera error: {error_message}")
        self.video_label.setText(f"Camera Error: {error_message}")

        self.is_camera_running = False
        self.start_stop_button.setText("Start Camera")
        self.start_stop_button.setEnabled(True)

        self.camera_thread = None
        self.camera_worker = None



    def closeEvent(self, event):
        """Ensures the camera thread is stopped cleanly when the window closes."""
        print("Closing application...")
        if self.is_camera_running and self.camera_worker:
            print("Requesting camera worker stop...")

            self.camera_worker.stop()


            if self.camera_thread and self.camera_thread.isRunning():
                print("Waiting for camera thread to finish...")

                finished = self.camera_thread.wait(5000)
                if not finished:
                    print("Warning: Camera thread did not finish gracefully. Terminating.")
                    self.camera_thread.terminate() 
                    self.camera_thread.wait() 
                else:
                    print("Camera thread finished gracefully.")
            else:
                 print("Camera thread was not running or already finished.")
        else:
             print("Camera was not running.")

        event.accept() 


if __name__ == "__main__":
    print("Initializing application...")
    
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)

    print("Creating main window...")
    window = MainWindow()
    window.show()

    print("Starting event loop...")
    sys.exit(app.exec())

