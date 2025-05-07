# camera_worker.py
import cv2
import time
import numpy as np
from PySide6.QtCore import QObject, Signal, Slot, QThread, QMutex, QMutexLocker

# Import the new processor
from mediapipe_processor import MediaPipeProcessor

class CameraWorker(QObject):
    """
    Handles camera operations and MediaPipe processing in a separate thread.
    Emits processed frames (with landmarks drawn) via the frame_ready signal.
    """
    frame_ready = Signal(np.ndarray) # Emit numpy array frame (now annotated)
    finished = Signal()              # Signal when the run loop finishes
    error = Signal(str)             # Signal for emitting error messages
    landmarks_ready = Signal(object)   # Signal for emitting landmarks positions           

    def __init__(self, camera_index=0, parent=None):
        super().__init__(parent)
        self._running = False
        self._camera_index = camera_index
        self._cap = None
        self._media_pipe_processor = None # Placeholder for the processor
        self._mutex = QMutex()

    @Slot()
    def run(self):
        """The main loop for capturing, processing, and emitting frames."""
        print("CameraWorker: Run method started.")
        self._mutex.lock()
        self._running = True
        self._mutex.unlock()

        # --- Initialize MediaPipe Processor ---
        # Do this inside the run method so it happens in the worker thread
        try:
            print("CameraWorker: Initializing MediaPipeProcessor...")
            self._media_pipe_processor = MediaPipeProcessor(
                # Adjust parameters here if needed, e.g., model_complexity=0 for lower-end hardware
                model_complexity=1
            )
            print("CameraWorker: MediaPipeProcessor initialized.")
        except Exception as e:
            error_msg = f"Failed to initialize MediaPipe: {e}"
            print(f"CameraWorker: {error_msg}")
            self.error.emit(error_msg)
            self._mutex.lock()
            self._running = False
            self._mutex.unlock()
            self.finished.emit()
            return # Exit if MediaPipe fails

        # --- Initialize Camera ---
        print(f"CameraWorker: Attempting to open camera {self._camera_index}...")
        self._cap = cv2.VideoCapture(self._camera_index, cv2.CAP_DSHOW)

        if not self._cap or not self._cap.isOpened():
            error_msg = f"Error: Could not open camera index {self._camera_index}."
            print(f"CameraWorker: {error_msg}")
            self.error.emit(error_msg)
            self._mutex.lock()
            self._running = False
            self._mutex.unlock()
            # Clean up MediaPipe if camera fails after its initialization
            if self._media_pipe_processor:
                 self._media_pipe_processor.close()
            self.finished.emit()
            return

        print(f"CameraWorker: Camera {self._camera_index} opened successfully.")

        # --- Main Loop ---
        while True:
            self._mutex.lock()
            should_run = self._running
            self._mutex.unlock()

            if not should_run:
                break # Exit loop if stop() was called

            ret, frame = self._cap.read() # Read a frame
            if ret:
                # --- Process with MediaPipe ---
                try:
                    # Pass the raw frame to the processor
                    annotated_frame, pose_results = self._media_pipe_processor.process_frame(frame)

                    # --- Emit the processed frame ---
                    # The frame now potentially has the skeleton drawn on it
                    self.frame_ready.emit(annotated_frame)

                    if pose_results and pose_results.pose_landmarks:
                        self.landmarks_ready.emit(pose_results.pose_landmarks)

                except Exception as e:
                    print(f"CameraWorker: Error processing frame with MediaPipe: {e}")
                    # Decide how to handle processing errors, e.g., emit original frame?
                    # self.frame_ready.emit(frame) # Emit original if processing fails
                    pass # Or just skip emitting this frame
            else:
                print("CameraWorker: Warning - Could not read frame.")
                time.sleep(0.01)

        # --- Cleanup ---
        print("CameraWorker: Exiting run loop.")
        if self._cap:
            self._cap.release()
            print("CameraWorker: Camera released.")
        self._cap = None

        if self._media_pipe_processor:
            self._media_pipe_processor.close() # Release MediaPipe resources
            self._media_pipe_processor = None

        self.finished.emit()
        print("CameraWorker: Run method finished.")


    @Slot()
    def stop(self):
        """Requests the worker loop to stop."""
        print("CameraWorker: Stop requested.")
        self._mutex.lock()
        self._running = False
        self._mutex.unlock()

