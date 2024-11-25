# A script to split the conetents between 2 bookmarks and output as new video file
# Note - It will extract the content between [even - odd] bookmarks, 
# So if you have 1,2,3,4 bookmarks, content between 1 and 2 & content between 3 and 4 will be extracted, content between 2 and 3 won't be extracted

import os
import subprocess
import json
from glob import glob

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
            return float(video_info['format']['duration'])
        else:
            print("Duration not found in video info.")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def parse_bookmarks(bookmarks_file):

    """
    Parses a bookmarks file to extract numerical keys and associated times in seconds.
    In my case I use PoPlayer and it bookmark file is of the '.pbf' extension and encoded in utf-16, 
    please modify the bookmark capture phenomenon to suit your needs

    Args:
        bookmarks_file (str): Path to the bookmarks file.

    Returns:
        dict: A dictionary where keys are integer indices and values are times in seconds.
    """

    bookmarks = {}

    try:
        # Open the file with the correct encoding (UTF-16LE based on symptoms)
        with open(bookmarks_file, 'r', encoding='utf-16') as file:
            for line in file:
                # Strip whitespace and skip empty lines
                line = line.strip()
                if not line:
                    continue

                # Split by '=' to extract key-value pairs
                parts = line.split("=", 1)  # Split only on the first '='
                if len(parts) != 2:
                    #Log to check if error occurs - comment this out now
                    #print(f"Skipping invalid line: {line}")
                    continue

                key, value = parts
                key = key.strip()

                # Ensure the key is numeric
                if not key.isdigit():
                    print(f"Invalid key (not numeric): {key}")
                    continue

                # Split the value by '*' to extract the time
                time_and_name = value.split("*", 1)
                if not time_and_name or not time_and_name[0].isdigit():
                    #Log to check if error occurs - comment this out now
                    #print(f"Invalid or missing time in value: {value}")
                    continue

                # Convert the time from milliseconds to seconds
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
    for i in range(0, len(sorted_keys) - 1, 2):  # Process even-odd pairs
        even_key = sorted_keys[i]
        odd_key = sorted_keys[i + 1]
        
        start_time = bookmarks[odd_key]  # Odd bookmark comes first
        end_time = bookmarks[even_key]  # Even bookmark comes next

        output_filename = f"{os.path.splitext(video_path)[0]}_clip_{odd_key + 1}_to_{even_key + 1}.mp4"
        
        try:
            # Run ffmpeg to extract the clip
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

# Main script logic
if __name__ == "__main__":
    # Get all video files in the current directory
    video_extensions = ["*.mp4", "*.mkv", "*.avi", "*.mov"]
    video_files = []
    for ext in video_extensions:
        video_files.extend(glob(ext))

    if not video_files:
        print("No video files found in the current directory.")
    else:
        for video_file in video_files:
            # Find the corresponding .pbf file
            base_name = os.path.splitext(video_file)[0]
            bookmarks_file = f"{base_name}.pbf"

            if not os.path.exists(bookmarks_file):
                print(f"Bookmark file not found for {video_file}. Skipping...")
                continue

            # Get video duration (optional for validation)
            duration = get_video_duration(video_file)
            if duration:
                print(f"Processing {video_file} (Duration: {duration:.2f} seconds)")

            # Parse bookmarks
            bookmarks = parse_bookmarks(bookmarks_file)
            if bookmarks:
                print(f"Parsed bookmarks for {video_file}: {bookmarks}")

                # Split video based on bookmarks
                split_video(video_file, bookmarks)
            else:
                print(f"No valid bookmarks found in {bookmarks_file}. Skipping...")
