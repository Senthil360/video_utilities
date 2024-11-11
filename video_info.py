import cv2
import os
import argparse
import pandas as pd
from datetime import timedelta

# Utility function to convert seconds into HH:MM:SS format
def convert_seconds_to_hms(seconds):
    return str(timedelta(seconds=seconds))

def get_video_info(video_path):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count / fps
    file_size = os.path.getsize(video_path) / (1024 * 1024)  # in MB
    
    # Getting video codec (as an integer)
    codec = int(cap.get(cv2.CAP_PROP_FOURCC))  # Cast to int
    codec = chr((codec & 0xFF)) + chr((codec >> 8) & 0xFF) + chr((codec >> 16) & 0xFF) + chr((codec >> 24) & 0xFF)
    
    return {
        'filename': os.path.basename(video_path),
        'duration': convert_seconds_to_hms(duration),
        'file_size': f"{file_size:.2f} MB",
        'fps': fps,
        'resolution': f"{width}x{height}",
        'codec': codec
    }

def save_to_excel(video_info_list, output_path):
    # Creating a DataFrame from the list of video info
    df = pd.DataFrame(video_info_list)

    # Saving the DataFrame to Excel
    excel_path = os.path.join(output_path, "video_info.xlsx")
    df.to_excel(excel_path, index=False)

    print(f"Video info saved to {excel_path}")

def main():
    parser = argparse.ArgumentParser(description="Extract and display video information from a file or directory.")
    parser.add_argument('input', type=str, nargs='?', default=os.getcwd(), help="Path to the video file or directory containing video files (default is current directory)")
    parser.add_argument('--output', type=str, default=os.getcwd(), help="Path to the output directory for saving metadata (default is current directory)")
    args = parser.parse_args()

    input_path = args.input
    output_path = args.output

    # Check if the input is a file or directory
    if os.path.isdir(input_path):
        video_files = [os.path.join(input_path, f) for f in os.listdir(input_path) if f.endswith('.mp4')]
    elif os.path.isfile(input_path) and input_path.endswith('.mp4'):
        video_files = [input_path]
    else:
        print(f"Error: {input_path} is not a valid directory or mp4 file.")
        return

    video_info_list = []

    # Process each video file
    for video_file in video_files:
        video_info = get_video_info(video_file)
        
        # Add the video info to the list
        video_info_list.append(video_info)

        # Optionally, print the video information
        print(f"Processing {video_info['filename']}")
        print(f"Duration: {video_info['duration']}")
        print(f"File Size: {video_info['file_size']}")
        print(f"FPS: {video_info['fps']}")
        print(f"Resolution: {video_info['resolution']}")
        print(f"Codec: {video_info['codec']}")
        print('-' * 40)
    
    # Save all video info to an Excel file
    save_to_excel(video_info_list, output_path)

if __name__ == "__main__":
    main()