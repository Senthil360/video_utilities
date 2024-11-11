import os
import subprocess
import argparse

def get_video_codec(input_path):
    # Use ffprobe to get the codec of the video stream
    cmd = [
        'ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries',
        'stream=codec_name', '-of', 'default=noprint_wrappers=1:nokey=1', input_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return result.stdout.strip()

def transcode_video(input_path, output_path, frame_rate):
    # FFmpeg command with multithreading, and veryfast preset, no downscaling
    cmd = [
        'ffmpeg', '-i', input_path, '-r', str(frame_rate),  # Set frame rate from original video
        '-c:v', 'libx264', '-preset', 'veryfast',  # Set veryfast preset for quicker processing
        '-c:a', 'aac', '-strict', 'experimental',  # Use AAC for audio encoding
        '-movflags', '+faststart',  # Optimize for streaming
        '-threads', '0',  # Enable multithreading
        output_path
    ]
    
    # Run the FFmpeg command
    subprocess.run(cmd, check=True)

def get_frame_rate(input_path):
    # Use ffprobe to get the frame rate of the video
    cmd = [
        'ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries',
        'stream=r_frame_rate', '-of', 'default=noprint_wrappers=1:nokey=1', input_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    # Parse frame rate (e.g., "30/1" to "30")
    num, denom = map(int, result.stdout.strip().split('/'))
    return num / denom if denom else num

def transcode_videos_in_directory(input_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    for filename in os.listdir(input_dir):
        if filename.lower().endswith('.mp4'):
            input_path = os.path.join(input_dir, filename)
            codec = get_video_codec(input_path)
            
            # Only transcode if codec is neither h264 nor h265
            if codec not in ['h264', 'hevc']:
                frame_rate = get_frame_rate(input_path)
                output_filename = f"{os.path.splitext(filename)[0]}_transcoded.mp4"
                output_path = os.path.join(output_dir, output_filename)
                transcode_video(input_path, output_path, frame_rate)
                print(f"Transcoded {filename} to {output_path}")
            else:
                print(f"Skipped {filename} (Codec: {codec})")

def transcode_single_file(input_path):
    directory = os.path.dirname(input_path)
    filename = os.path.basename(input_path)
    codec = get_video_codec(input_path)
    
    # Only transcode if codec is neither h264 nor h265
    if codec not in ['h264', 'hevc']:
        frame_rate = get_frame_rate(input_path)
        output_filename = f"{os.path.splitext(filename)[0]}_transcoded.mp4"
        output_path = os.path.join(directory, output_filename)  # Save in the same directory
        transcode_video(input_path, output_path, frame_rate)
        print(f"Transcoded {filename} to {output_path}")
    else:
        print(f"Skipped {filename} (Codec: {codec})")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Transcode videos to H.264 with no downscaling.")
    parser.add_argument("-i", "--input", default=os.getcwd(), help="Input directory or video file (default: current directory)")
    parser.add_argument("-o", "--output", default=os.getcwd(), help="Output directory (default: current directory)")
    args = parser.parse_args()

    # If the input is a directory, transcode all mp4 files in that directory
    if os.path.isdir(args.input):
        transcode_videos_in_directory(args.input, args.output)
    # If the input is a file, transcode that specific file
    elif os.path.isfile(args.input):
        transcode_single_file(args.input)
    else:
        print("Invalid input. Please provide a valid file or directory.")
