import os
from datetime import time, datetime, timedelta, timezone
import ffmpeg
import subprocess
from typing import Optional, Tuple
import logging

def image_capture(rtsp_url: str, save_location: str, filename_prefix: str):
    try:
        
        os.makedirs(save_location, exist_ok=True)
        
        saved_frames = []
        frames_captured = 0
        
        while frames_captured < 1:
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            filename = f"{filename_prefix}_{timestamp}.jpg"
            filepath = os.path.join(save_location, filename)
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

def audio_capture(rtsp_url, save_location: str, filename_prefix:str, duration):
    
    os.makedirs(save_location, exist_ok=True)

    saved_clips = []
    audio_extracted = 0

    while audio_extracted < 1:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"{filename_prefix}_{timestamp}.aac"
        filepath = os.path.join(save_location, filename)

        ffmpeg_cmd = [
            'ffmpeg',
            '-y',  # Overwrite output files without asking
            '-i', rtsp_url,  # Input RTSP stream
            '-t', str(duration),  # Duration of the audio clip
            '-vn',  # Exclude video
            '-acodec', 'copy',  # Copy the audio codec
            filepath
        ]

        # Execute the FFmpeg command
        process = subprocess.run(
            ffmpeg_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Check for errors in the FFmpeg process
        if process.returncode != 0:
            raise Exception(f"FFmpeg error: {process.stderr}")

        # Add the saved file to the list and increment counter
        saved_clips.append(filepath)
        audio_extracted += 1

    return saved_clips


# def video_capture():
#     pass