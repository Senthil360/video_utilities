#This is a programme which creates a preview collage picture from a video grabbing frames at equal intervals
#Pre-requisites - Python (libraries - cv2, PIL)
#<msenthilm1023@gmail.com>
""" 
    USAGE
    
    To grab screenshot from a single video file (mp4)
        python screenshot.py /path/to/video.mp4 /path/to/output

    To grab screenshot from all video files (mp4) inside a directory
        python screenshot.py /path/to/video /path/to/output

    Default parameters can be modified below at def main()
"""
#This program grabs 36 frames from a video file and outputs it as a jpg file, it will have filename, filesize, duration, resolution information

import cv2
import os
import time
import argparse
from PIL import Image, ImageDraw, ImageFont

# Utility function to convert seconds into HH:MM:SS format
def convert_seconds_to_hms(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"

def create_video_preview(video_path, output_path, preview_size=(3820, 2384), rows=6, cols=6, border_size=10, shadow_offset=(5, 5), width_to_height_ratio=16/9):
    start_time = time.time()  # Start time for performance measurement
    
    # Open video file and get properties
    cap = cv2.VideoCapture(video_path)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    duration = frame_count / fps
    file_size = os.path.getsize(video_path) / (1024 * 1024)  # Convert to MB

    # Metadata text
    filename = os.path.basename(video_path)
    duration_str = convert_seconds_to_hms(duration)
    file_size_str = f"{file_size:.2f} MB"
    metadata_text_line_1 = f"File: {filename}"
    metadata_text_line_2 = f"Resolution: {width}x{height}  |  Duration: {duration_str}  |  File Size: {file_size_str}"
    
    # Metadata section height
    metadata_height = 224  # Updated metadata height (224px)
    grid_height = 2160  # Increased height for grid area
    grid_width = 3820  # Increased width for grid area
    
    # Create the preview canvas with a white background
    preview_image = Image.new("RGB", preview_size, color="white")
    
    # Font setup for text (increased font size)
    try:
        font = ImageFont.truetype("arial.ttf", 30)  # Increased font size for metadata
        bold_font = ImageFont.truetype("arialbd.ttf", 40)  # Bold font with larger size
    except IOError:
        font = ImageFont.load_default()
        bold_font = font
    
    # Draw simplified metadata text
    draw = ImageDraw.Draw(preview_image)
    metadata_text_line_1 = f"File: {filename}"
    metadata_text_line_2 = f"Resolution: {width}x{height}"
    metadata_text_line_3 = f"Duration: {duration_str}"
    metadata_text_line_4 = f"File Size: {file_size_str}"
    
    # Start Y position for metadata lines
    y_offset = 20
    
    # Draw each metadata line
    draw.text((10, y_offset), metadata_text_line_1, font=bold_font, fill="black")
    y_offset += 50
    draw.text((10, y_offset), metadata_text_line_2, font=bold_font, fill="black")
    y_offset += 50
    draw.text((10, y_offset), metadata_text_line_3, font=bold_font, fill="black")
    y_offset += 50
    draw.text((10, y_offset), metadata_text_line_4, font=bold_font, fill="black")

    # Sample interval calculation
    sample_interval = frame_count // (rows * cols)

    frame_idx = 0
    # Element dimensions for the grid (fixed to 16:9 aspect ratio)
    cell_width = grid_width // cols  # Each element width including padding
    cell_height = grid_height // rows  # Each element height including padding

    for row in range(rows):
        for col in range(cols):
            # Set video capture to the correct frame
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            success, frame = cap.read()
            if not success:
                print("Failed to retrieve frame at index", frame_idx)
                continue

            # Convert frame from BGR (OpenCV) to RGB (Pillow)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_pil = Image.fromarray(frame_rgb).resize((cell_width - 2 * border_size, cell_height - 2 * border_size))
            
            # Calculate position for frame on the grid
            x = col * (cell_width) + border_size
            y = metadata_height + row * (cell_height) + border_size

            # Draw shadow and border
            shadow_x = x + shadow_offset[0]
            shadow_y = y + shadow_offset[1]
            shadow_width = cell_width - 2 * border_size
            shadow_height = cell_height - 2 * border_size
            draw.rectangle([shadow_x, shadow_y, shadow_x + shadow_width, shadow_y + shadow_height], fill="gray")
            draw.rectangle([x - border_size, y - border_size, x + cell_width + border_size, y + cell_height + border_size], outline="black")
            
            # Paste frame into preview image
            preview_image.paste(frame_pil, (x, y))

            # Add timestamp text
            timestamp = frame_idx / fps
            timestamp_str = convert_seconds_to_hms(timestamp)
            text_bbox = draw.textbbox((0, 0), timestamp_str, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            timestamp_x = x + (cell_width - text_width) // 2
            timestamp_y = y + cell_height - text_height - 30  # Slightly move it up by adjusting the 30px margin

            # Draw timestamp with stroke effect
            for dx in [-2, 0, 2]:
                for dy in [-2, 0, 2]:
                    draw.text((timestamp_x + dx, timestamp_y + dy), timestamp_str, font=font, fill="black")
            draw.text((timestamp_x, timestamp_y), timestamp_str, font=font, fill="white")
            
            # Move to next frame
            frame_idx += sample_interval

    # Save the final image with high quality (quality set to 100 for the best JPEG quality)
    preview_image.save(output_path, quality=100)
    
    end_time = time.time()
    print(f"Preview image saved to {output_path}")
    print(f"Time taken: {end_time - start_time:.2f} seconds")

# Function to process all MP4 files in the directory
def generate_previews_for_directory(input_directory, output_directory):
    # Check if output directory exists, if not create it
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    
    for filename in os.listdir(input_directory):
        if filename.endswith(".mp4"):
            video_path = os.path.join(input_directory, filename)
            output_path = os.path.join(output_directory, f"{os.path.splitext(filename)[0]}_preview.jpg")
            create_video_preview(video_path, output_path)
            print(f"Preview for {filename} saved as {output_path}")

# Command-line interface using argparse
def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Generating preview collage picture of video files")
    
    # Arguments for file path, output directory, number of parts, and file size limits in MB
    parser.add_argument('input', type=str, nargs='?', default=os.getcwd(), help="Input video file or directory (default: current working directory).")
    parser.add_argument('output', type=str, nargs='?', default=os.path.join(os.getcwd(), "screencap"), help="Directory to save the split parts (default: 'split_videos' in current directory).")
    
    # Parse the command-line arguments
    args = parser.parse_args()
    
    # Check if input is a directory or file
    if os.path.isdir(args.input):
        print(f"Getting screenshot of all MP4 files in directory: {args.input}")
        generate_previews_for_directory(args.input, args.output)
    elif os.path.isfile(args.input) and args.input.endswith('.mp4'):
        print(f"Getting screenshot of single video: {args.input}")
        output_name = os.path.join(os.getcwd(), "screencap")
        output_name = os.path.join(output_name, f"{os.path.splitext(os.path.basename(args.input))[0]}_preview.jpg")
        create_video_preview(args.input, output_name)
    else:
        print("Invalid input. Please provide a valid MP4 file or directory.")

# Run the script
if __name__ == "__main__":
    main()
