import os
from datetime import time, datetime, timedelta, timezone
import ffmpeg
import subprocess
from typing import Optional, Tuple
import logging

def image_capture(rtsp_url: str, save_location: str, filename_prefix: str, max_frames: int):
    try:
        # Create save directory if it doesn't exist
        os.makedirs(save_location, exist_ok=True)
        
        saved_frames = []
        frames_captured = 0
        
        while frames_captured < max_frames:
            # Generate timestamp for filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            filename = f"{filename_prefix}_{timestamp}.jpg"
            filepath = os.path.join(save_location, filename)
            
            # FFmpeg command to capture a single frame
            ffmpeg_cmd = [
                'ffmpeg',
                '-y',  # Overwrite output files without asking
                '-i', rtsp_url,  # Input RTSP stream
                '-vframes', '1',  # Capture only one frame
                '-f', 'image2',  # Force image2 format
                filepath
            ]
            
            # Execute FFmpeg command
            process = subprocess.run(
                ffmpeg_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            if process.returncode != 0:
                raise Exception(f"FFmpeg error: {process.stderr.decode()}")
            saved_frames.append(filepath)
            frames_captured += 1
    except subprocess.CalledProcessError as e:
        return False
    except Exception as e:
        return False
    return True

def audio_capture(server_url: str,):
    pass

def video_capture():
    pass