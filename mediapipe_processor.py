# mediapipe_processor.py
import cv2
import mediapipe as mp
import numpy as np

class MediaPipeProcessor:
    """
    Handles MediaPipe Pose detection and visualization.
    """
    def __init__(self,
                 static_image_mode=False,
                 model_complexity=1,
                 smooth_landmarks=True,
                 enable_segmentation=False, # Keep segmentation off for performance
                 smooth_segmentation=True,
                 min_detection_confidence=0.5,
                 min_tracking_confidence=0.5):
        """
        Initializes the MediaPipe Pose solution.

        Args:
            static_image_mode: Whether to treat input images as static images or a video stream.
            model_complexity: Complexity of the pose landmark model: 0, 1, or 2.
            smooth_landmarks: Whether to filter landmarks across frames to reduce jitter.
            enable_segmentation: Whether to predict segmentation mask (requires more resources).
            smooth_segmentation: Whether to filter segmentation mask across frames.
            min_detection_confidence: Minimum confidence value ([0.0, 1.0]) for detection to be considered successful.
            min_tracking_confidence: Minimum confidence value ([0.0, 1.0]) for tracking landmarks. Higher values increase robustness but also latency.
        """
        print("Initializing MediaPipe Pose...")
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles

        self.pose = self.mp_pose.Pose(
            static_image_mode=static_image_mode,
            model_complexity=model_complexity,
            smooth_landmarks=smooth_landmarks,
            enable_segmentation=enable_segmentation,
            smooth_segmentation=smooth_segmentation,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        print("MediaPipe Pose initialized successfully.")

    def process_frame(self, frame: np.ndarray):
        """
        Processes a single frame to detect and draw pose landmarks.

        Args:
            frame: The input video frame (in BGR format from OpenCV).

        Returns:
            A tuple containing:
            - annotated_image (np.ndarray): The frame with landmarks and connections drawn.
            - results: The raw pose results object from MediaPipe (or None if processing failed).
        """
        try:
            # 1. Convert the BGR image to RGB for MediaPipe.
            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # To improve performance, optionally mark the image as not writeable to
            # pass by reference.
            image_rgb.flags.writeable = False

            # 2. Process the image and find pose landmarks.
            results = self.pose.process(image_rgb)

            # 3. Prepare the frame for drawing (make a writeable copy in BGR).
            # We draw on the original BGR frame format that OpenCV uses.
            image_rgb.flags.writeable = True # No longer needed
            annotated_image = frame.copy() # Draw on a copy of the original BGR frame

            # 4. Draw the pose annotation on the image if landmarks are detected.
            if results.pose_landmarks:
                self.mp_drawing.draw_landmarks(
                    image=annotated_image,
                    landmark_list=results.pose_landmarks,
                    connections=self.mp_pose.POSE_CONNECTIONS,
                    landmark_drawing_spec=self.mp_drawing_styles.get_default_pose_landmarks_style()
                    # connection_drawing_spec=self.mp_drawing_styles.get_default_pose_landmarks_style() # You can customize connection style too
                )
            else:
                # Optional: Add text if no pose is detected
                # cv2.putText(annotated_image, "No pose detected", (50, 50),
                #             cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
                pass


            return annotated_image, results # Return the annotated BGR image and the results object

        except Exception as e:
            print(f"Error processing frame with MediaPipe: {e}")
            # Return the original frame and None for results in case of error
            return frame, None

    def close(self):
        """Releases MediaPipe resources."""
        print("Closing MediaPipe Pose resources...")
        self.pose.close()
        print("MediaPipe Pose resources closed.")

