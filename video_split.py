#This is a video splitting programme
#Pre-requisites - Python, ffmpeg, ffprobe
#<msenthilm1023@gmail.com>
""" 
    USAGE EXAMPLE
    
    To split a single video file
        python video_split.py /path/to/video.mp4 /path/to/output --num_parts 4 --min_size 10 --max_size 100

    To split all video files (mp4) inside a directory
        python video_split.py /path/to/video.mp4 /path/to/output --num_parts 4 --min_size 10 --max_size 100

    Default parameters can be modified below at def main()
"""

import subprocess
import os
import json
import argparse

# Utility function to get the duration of a video using ffprobe
def get_video_duration(video_path):
    try:
        # Run ffprobe to get video info in JSON format
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'json', video_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Parse the JSON output
        video_info = json.loads(result.stdout)

        # Extract the duration from the JSON output
        if 'format' in video_info and 'duration' in video_info['format']:
            duration_str = video_info['format']['duration']
            print(f"Duration: {duration_str}")
        else:
            print("Duration not found in video info.")
            duration_str = None

        return float(duration_str)

    except Exception as e:
        print(f"Error: {e}")
        return None

# Function to get the file size of the video
def get_video_file_size(video_path):
    try:
        return os.path.getsize(video_path)  # Size in bytes
    except Exception as e:
        print(f"Error: {e}")
        return None

# Function to split a single video
def split_video(video_path, output_dir, num_parts, min_size_mb, max_size_mb):
    # Convert MB to bytes
    min_size = min_size_mb * 1024 * 1024
    max_size = max_size_mb * 1024 * 1024

    # Get the duration of the video
    video_duration = get_video_duration(video_path)
    if video_duration is None:
        return

    # Get the file size of the video
    video_size = get_video_file_size(video_path)
    if video_size is None:
        return

    print(f"File size: {video_size / (1024 * 1024):.2f} MB")

    # Check if the file size is within the allowed limits
    if video_size < min_size or video_size > max_size:
        print(f"File size {video_size / (1024 * 1024):.2f} MB is out of the specified range!")
        return

    # Calculate the duration of each part
    part_duration = video_duration / num_parts
    print(f"Each part will be {part_duration:.2f} seconds long.")

    # Make sure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Extract the original file name without the extension
    base_filename = os.path.splitext(os.path.basename(video_path))[0]

    # Use ffmpeg to split the video into parts
    for i in range(num_parts):
        start_time = i * part_duration
        # Construct the output filename: original filename + " - part N.mp4"
        output_file = os.path.join(output_dir, f"{base_filename} - part {i+1}.mp4")
        
        # ffmpeg command with additional flags
        ffmpeg_command = [
            'ffmpeg', '-i', video_path, 
            '-ss', str(start_time), 
            '-t', str(part_duration), 
            '-loglevel', 'quiet',
            '-avoid_negative_ts', 'auto', 
            '-map', '0:0', 
            '-c:0', 'copy', 
            '-map', '0:1', 
            '-c:1', 'copy', 
            '-map_metadata', '0', 
            '-map_chapters', '-1', 
            '-movflags', '+faststart', 
            '-default_mode', 'infer_no_subs', 
            '-ignore_unknown', 
            '-f', 'mp4',
            output_file
        ]
        
        subprocess.run(ffmpeg_command)
        print(f"Created {output_file}")

# Function to split all MP4 files in a given directory with size limits
def split_all_videos_in_directory(input_dir, output_dir, num_parts, min_size_mb, max_size_mb):
    # Get a list of all MP4 files in the input directory
    for file_name in os.listdir(input_dir):
        if file_name.endswith('.mp4'):
            video_path = os.path.join(input_dir, file_name)
            print(f"Processing video: {file_name}")
            split_video(video_path, output_dir, num_parts, min_size_mb, max_size_mb)

# Command-line interface using argparse
def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Split MP4 videos into parts.")
    
    # Arguments for file path, output directory, number of parts, and file size limits in MB
    parser.add_argument('input', type=str, nargs='?', default=os.getcwd(), help="Input video file or directory (default: current working directory).")
    parser.add_argument('output', type=str, nargs='?', default=os.path.join(os.getcwd(), "output_parts"), help="Directory to save the split parts (default: 'split_videos' in current directory).")
    parser.add_argument('--num_parts', type=int, default=4, help="Number of parts to split each video into (default: 4).")
    parser.add_argument('--min_size', type=int, default=100, help="Minimum file size in MB (default: 100MB).")
    parser.add_argument('--max_size', type=int, default=2000, help="Maximum file size in MB (default: 2000MB).")
    
    # Parse the command-line arguments
    args = parser.parse_args()
    
    # Check if input is a directory or file
    if os.path.isdir(args.input):
        print(f"Processing all MP4 files in directory: {args.input}")
        split_all_videos_in_directory(args.input, args.output, args.num_parts, args.min_size, args.max_size)
    elif os.path.isfile(args.input) and args.input.endswith('.mp4'):
        print(f"Processing single video: {args.input}")
        split_video(args.input, args.output, args.num_parts, args.min_size, args.max_size)
    else:
        print("Invalid input. Please provide a valid MP4 file or directory.")

# Run the script
if __name__ == "__main__":
    main()