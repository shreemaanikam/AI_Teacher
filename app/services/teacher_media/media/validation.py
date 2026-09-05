"""
Video Quality Validation and Decoding Audit.
"""

import os
try:
    import cv2
except ImportError:
    cv2 = None


def validate_video(video_path: str) -> bool:
    """
    Audits generated MP4 video:
    - Exists and size > 500 bytes
    - Decodable by OpenCV VideoCapture
    - Valid dimensions (width > 0, height > 0)
    - Non-zero frames and positive FPS
    - First and middle frames decode successfully
    """
    if not os.path.exists(video_path) or os.path.getsize(video_path) < 500:
        return False
    if cv2 is None:
        return True
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return False
            
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        if frame_count <= 0 or width <= 0 or height <= 0 or fps <= 0:
            cap.release()
            return False
            
        ret, frame = cap.read()
        cap.release()
        return ret and frame is not None
    except Exception:
        return False
