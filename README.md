# Image & Video Utilities

## resize_image_keep_ratio.py

Resize one or more images by specific percentage. Can also set the minimum dimension the resized image can reach.

Usage:

`` python resize_image_keep_ratio.py /path/to/input.jpg /path/to/output.jpg --percent 0.8 --min_dim 480 ``

## record_screen.py

A simple tool that records the entire or part of the screen. Can set resolution and fps.

Usage:

`` python record_screen.py --output /path/to/output.mp4 --resolution 1920x1080 --fps 30 ``

After executing the above command a transparent window will appear and a cursor, to select the desired part of the screen (press 'Enter' for the entire screen).

Ater selecting, the tool will start recording. Press Ctrl + C in the console to stop recording. The video will be saved in the specified location.
