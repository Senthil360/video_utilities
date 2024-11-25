# A script to split the conetents between 2 bookmarks and output as new video file
# Note - It will extract the content between [even - odd] bookmarks, 
# So if you have 1,2,3,4 bookmarks, content between 1 and 2 & content between 3 and 4 will be extracted, content between 2 and 3 won't be extracted

# Usage python mark_split.py , use  [ python mark_split.py --merge ] merge flag to merge the split segments into 1 file

import os
import subprocess
import json
from glob import glob
import argparse  # Import argparse for command-line arguments

# Utility function to get the duration of a video using ffprobe
def get_video_duration(video_path):
    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'json', video_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        video_info = json.loads(result.stdout)
        if 'format' in video_info and 'duration' in video_info['format']:
            return float(video_info['format']['duration'])
        else:
            print("Duration not found in video info.")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def parse_bookmarks(bookmarks_file):
    bookmarks = {}

    """
    Parses a bookmarks file to extract numerical keys and associated times in seconds.
    In my case I use PoPlayer and it bookmark file is of the '.pbf' extension and encoded in utf-16, 
    please modify the bookmark capture phenomenon to suit your needs
    Args:
        bookmarks_file (str): Path to the bookmarks file.
    Returns:
        dict: A dictionary where keys are integer indices and values are times in seconds.
    """
    try:
        # Open the file with the correct encoding (UTF-16 for my system)
        with open(bookmarks_file, 'r', encoding='utf-16') as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue
                parts = line.split("=", 1)
                if len(parts) != 2:
                    continue
                key, value = parts
                key = key.strip()
                if not key.isdigit():
                    print(f"Invalid key (not numeric): {key}")
                    continue
                time_and_name = value.split("*", 1)
                if not time_and_name or not time_and_name[0].isdigit():
                    continue
                try:
                    time_ms = int(time_and_name[0])
                    bookmarks[int(key)] = time_ms / 1000
                except ValueError:
                    print(f"Invalid time format in line: {line}")
    except FileNotFoundError:
        print(f"Error: File not found - {bookmarks_file}")
    except UnicodeDecodeError as e:
        print(f"Encoding error while reading the file: {e}")
    except Exception as e:
        print(f"Unexpected error parsing file {bookmarks_file}: {e}")
    return bookmarks

# Function to split the video based on bookmarks
def split_video(video_path, bookmarks):
    sorted_keys = sorted(bookmarks.keys(), reverse=True)  # Sort keys in descending order
    clips = []
    for i in range(0, len(sorted_keys) - 1, 2):  # Process even-odd pairs
        even_key = sorted_keys[i]
        odd_key = sorted_keys[i + 1]
        start_time = bookmarks[odd_key]  # Odd bookmark comes first
        end_time = bookmarks[even_key]  # Even bookmark comes next

        output_filename = f"{os.path.splitext(video_path)[0]}_clip_{odd_key + 1}_to_{even_key + 1}.mp4"
        clips.append(output_filename)

        try:
            subprocess.run(
                [
                    "ffmpeg",
                    "-i", video_path,
                    "-ss", str(start_time),
                    "-to", str(end_time),
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
                    output_filename
                ],
                check=True
            )
            print(f"Created clip: {output_filename}")
        except subprocess.CalledProcessError as e:
            print(f"Error creating clip {output_filename}: {e}")
    return clips

# Function to merge video clips using ffmpeg
def merge_videos(clips, video_path):
    try:
        # Get the base name of the original video (without extension)
        base_name = os.path.splitext(os.path.basename(video_path))[0]
        
        # Set the output file name with the desired format
        output = f"{base_name} - BSE - merged_video.mp4"
        
        # Create a file list for the merge operation
        file_list = "file_list.txt"
        with open(file_list, 'w') as f:
            for clip in clips:
                f.write(f"file '{clip}'\n")
        
        # Run ffmpeg to merge the clips
        subprocess.run(
            ["ffmpeg", "-f", "concat", '-loglevel', 'quiet', "-safe", "0", "-i", file_list, "-c", "copy", output],
            check=True
        )
        print(f"Merged videos into {output}")
    except subprocess.CalledProcessError as e:
        print(f"Error merging videos: {e}")


# Main script logic
if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Split and optionally merge video clips based on bookmarks.")
    
    # Add argument for merge option
    parser.add_argument(
        '--merge', 
        action='store_true',  # This flag means the argument is a boolean (True/False)
        help="If specified, the clips will be merged after splitting."
    )
    
    # Parse command-line arguments
    args = parser.parse_args()
    
    # Get all video files in the current directory
    video_extensions = ["*.mp4", "*.mkv", "*.avi", "*.mov"]
    video_files = []
    for ext in video_extensions:
        video_files.extend(glob(ext))

    if not video_files:
        print("No video files found in the current directory.")
    else:
        for video_file in video_files:
            base_name = os.path.splitext(video_file)[0]
            bookmarks_file = f"{base_name}.pbf"

            if not os.path.exists(bookmarks_file):
                print(f"Bookmark file not found for {video_file}. Skipping...")
                continue

            duration = get_video_duration(video_file)
            if duration:
                print(f"Processing {video_file} (Duration: {duration:.2f} seconds)")

            bookmarks = parse_bookmarks(bookmarks_file)
            if bookmarks:
                print(f"Parsed bookmarks for {video_file}: {bookmarks}")
                clips = split_video(video_file, bookmarks)

                # If the --merge flag is passed, merge the clips
                if args.merge:
                    merge_videos(clips, video_file)
                else:
                    print("Skipping merge step.")
            else:
                print(f"No valid bookmarks found in {bookmarks_file}. Skipping...")
