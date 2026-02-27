import tkinter as tk
import subprocess
import sys
import signal
import argparse
import os
import threading
import time

ffmpeg_process = None
recording_area = None

def parse_arguments():
    parser = argparse.ArgumentParser(description='Simple screen recorder')
    
    parser.add_argument('--resolution', '-r', required=True, help='Output resolution (e.g., 1280x720)')
    parser.add_argument('--fps', '-f', type=int, required=True, help='Frames per second')
    parser.add_argument('--output', '-o', required=True, help='Output file path')
    
    return parser.parse_args()

def select_area():
    
    global recording_area
    
    root = tk.Tk()
    
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    # Setup transparent fullscreen window
    root.attributes('-fullscreen', True)
    root.attributes('-alpha', 0.3)
    root.attributes('-topmost', True)
    root.overrideredirect(True)
    root.configure(bg='grey')
    
    canvas = tk.Canvas(root, cursor='cross', bg='grey', highlightthickness=0)
    canvas.pack(fill=tk.BOTH, expand=True)
    
    instructions = ['Click and drag to select area',
                    'Press ENTER for full screen',
                    'Press ESC to cancel']

    canvas.create_text(screen_width // 2, 50, 
                      text='\n'.join(instructions),
                      fill='white', font=('Arial', 16))
    
    start_x = start_y = None
    rect = None
    area_selected = False
    
    def on_press(event):
        nonlocal start_x, start_y, rect
        start_x, start_y = event.x, event.y
        if rect:
            canvas.delete(rect)
        rect = canvas.create_rectangle(start_x, start_y, start_x, start_y,
                                      outline='red', width=3)
    
    def on_drag(event):
        nonlocal rect
        if rect and start_x is not None:
            canvas.coords(rect, start_x, start_y, event.x, event.y)
    
    def on_release(event):
        nonlocal start_x, start_y, area_selected
        if start_x is not None and start_y is not None:
            x1 = min(start_x, event.x)
            y1 = min(start_y, event.y)
            x2 = max(start_x, event.x)
            y2 = max(start_y, event.y)
            
            if x2 - x1 > 10 and y2 - y1 > 10:
                global recording_area
                recording_area = {
                    'x': x1, 'y': y1,
                    'width': x2 - x1,
                    'height': y2 - y1
                }
                area_selected = True
                root.quit()
    
    def on_enter(event):
        nonlocal area_selected
        global recording_area
        
        recording_area = {
            'x': 0, 'y': 0,
            'width': screen_width,
            'height': screen_height
        }
        area_selected = True
        root.quit()
    
    def on_escape(event):
        root.quit()
    
    canvas.bind('<ButtonPress-1>', on_press)
    canvas.bind('<B1-Motion>', on_drag)
    canvas.bind('<ButtonRelease-1>', on_release)
    root.bind('<Return>', on_enter)
    root.bind('<Escape>', on_escape)
    
    root.mainloop()
    root.destroy()
    
    return area_selected


def start_recording(area, resolution, fps, output_path):
    
    global ffmpeg_process
    
    # Parse resolution
    out_width, out_height = map(int, resolution.split('x'))
    
    # Windows command
    cmd = [
        'ffmpeg',
        '-y',
        '-f', 'gdigrab',
        '-framerate', str(fps),
        '-offset_x', str(area['x']),
        '-offset_y', str(area['y']),
        '-video_size', f"{area['width']}x{area['height']}",
        '-i', 'desktop',
        '-vf', f'scale={out_width}:{out_height}',
        '-c:v', 'libx264',
        '-preset', 'ultrafast',
        '-crf', '23',
        '-pix_fmt', 'yuv420p',
        output_path
    ]
    
    print("\n" + "="*50)
    print("FFmpeg command:")
    print(' '.join(cmd))
    print("="*50 + "\n")
    
    # Run FFmpeg in the same console
    # Use CREATE_NO_WINDOW on Windows to avoid new window
    if sys.platform == 'win32':
        ffmpeg_process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # Combine stdout and stderr
            universal_newlines=True,    # Use text mode
            bufsize=1                   # Line buffered
        )
    else:
        ffmpeg_process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
    
    print(f"Recording started! Press Ctrl+C to stop...")
    print("FFmpeg output:\n")
    
    # Create a thread to read and print FFmpeg output
    def read_output():
        for line in ffmpeg_process.stdout:
            print(f"  {line}", end='')
    
    output_thread = threading.Thread(target=read_output, daemon=True)
    output_thread.start()
    
    return True

def signal_handler(sig, frame):
    
    global ffmpeg_process
    print("\n\nStopping recording...")
    
    if ffmpeg_process:

        # Handle Ctrl+C to stop recording
        try:
            ffmpeg_process.stdin.write('q\n')
            ffmpeg_process.stdin.flush()
        except:
            ffmpeg_process.terminate()
        
        # Wait for FFmpeg to finish
        try:
            ffmpeg_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            ffmpeg_process.kill()
        
        # Check file
        if os.path.exists(args.output):
            size = os.path.getsize(args.output)
            print(f"Output file: {args.output} ({size} bytes)")
    
    sys.exit(0)

def main():
    global args
    args = parse_arguments()
    
    print("Click and drag to select recording area...")
    print("(Press ESC to cancel)\n")
    
    area_selected = select_area()
    
    if not area_selected or not recording_area:
        print("\nNo area selected. Exiting.")
        return
    
    print(f"\nSelected area: {recording_area}")
    
    # Register Ctrl+C handler
    signal.signal(signal.SIGINT, signal_handler)
    
    start_recording(
        area=recording_area,
        resolution=args.resolution,
        fps=args.fps,
        output_path=args.output
    )
    
    # Keep script running
    try:
        while True:
            time.sleep(1)
            # Check if FFmpeg died
            if ffmpeg_process and ffmpeg_process.poll() is not None:
                print("\nFFmpeg stopped unexpectedly!")
                # Read any remaining output
                remaining = ffmpeg_process.stdout.read()
                if remaining:
                    print(remaining)
                break
    except KeyboardInterrupt:
        signal_handler(None, None)

if __name__ == "__main__":
    main()
