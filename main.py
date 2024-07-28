from flask import Flask, request, render_template, send_from_directory, redirect, url_for
import os
import random
from moviepy.editor import VideoFileClip, vfx
import yt_dlp
from urllib.parse import urlparse, parse_qs

app = Flask(__name__)

VIDEO_DIR = 'videos'
CLIP_DIR = 'clips'
API_KEY = 'AIzaSyDQVz7vWIDCmsUn7MgMwDdfBXROP_4leo4'

def delete_existing_files():
    """Delete existing video and clip files."""
    for filename in os.listdir(VIDEO_DIR):
        file_path = os.path.join(VIDEO_DIR, filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")

    for filename in os.listdir(CLIP_DIR):
        file_path = os.path.join(CLIP_DIR, filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")

def download_youtube_video(youtube_url, output_path="videos/video.mp4"):
    try:
        ydl_opts = {
            'format': 'best',
            'outtmpl': output_path,
            'noplaylist': True,
            'quiet': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])
        return output_path
    except Exception as e:
        print(f"Error downloading video: {e}")
        return None

def ensure_9x16_aspect_ratio_with_padding(clip):
    width, height = clip.size
    target_aspect_ratio = 9 / 16

    current_aspect_ratio = width / height

    if current_aspect_ratio > target_aspect_ratio:
        new_height = int(width / target_aspect_ratio)
        padding_top_bottom = (new_height - height) // 2
        new_clip = clip.margin(top=padding_top_bottom, bottom=padding_top_bottom, color=(0, 0, 0))
    else:
        new_width = int(height * target_aspect_ratio)
        padding_left_right = (new_width - width) // 2
        new_clip = clip.margin(left=padding_left_right, right=padding_left_right, color=(0, 0, 0))

    return new_clip

def create_random_clips(video_path, clip_duration=5, num_clips=1):
    clips = []
    try:
        video = VideoFileClip(video_path)
        video_duration = int(video.duration)

        for _ in range(num_clips):
            start_time = random.randint(0, video_duration - clip_duration)
            end_time = start_time + clip_duration
            clip = video.subclip(start_time, end_time)

            clip = ensure_9x16_aspect_ratio_with_padding(clip)

            clips.append((clip, start_time, end_time))

        return clips
    except Exception as e:
        print(f"Error creating clips: {e}")
        return []

def save_clips(clips, base_filename="clips/clip"):
    filenames = []
    for i, (clip, _, _) in enumerate(clips):
        filename = f"{base_filename}_{i+1}.mp4"
        clip.write_videofile(filename, codec='libx264', audio_codec='aac')
        filenames.append(filename)
    return filenames

def get_video_id_from_url(url):
    parsed_url = urlparse(url)
    if parsed_url.hostname == 'www.youtube.com':
        video_id = parse_qs(parsed_url.query).get('v')
        if video_id:
            return video_id[0]
    return None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        youtube_url = request.form['youtube_url']
        
        # Delete existing files before processing new video
        delete_existing_files()

        video_path = download_youtube_video(youtube_url)

        if video_path:
            clips = create_random_clips(video_path)
            clip_filenames = save_clips(clips)
            print(clip_filenames[0].split('/')[1])
            if clip_filenames:
                return redirect(url_for('show_clip', clip_filename=clip_filenames[0].split('/')[1]))
        return "Failed to process video."
    return render_template('index.html')

@app.route('/clip/<clip_filename>')
def show_clip(clip_filename):
    return render_template('clip.html', clip_filename=clip_filename)

@app.route('/clips/<path:filename>')
def download_file(filename):
    return send_from_directory(CLIP_DIR, filename)

if __name__ == '__main__':
    # Create directories if they do not exist
    os.makedirs(VIDEO_DIR, exist_ok=True)
    os.makedirs(CLIP_DIR, exist_ok=True)
    
    app.run(debug=True)
from flask import Flask, request, render_template, send_from_directory, redirect, url_for
import os
import random
from moviepy.editor import VideoFileClip, vfx
import yt_dlp
from urllib.parse import urlparse, parse_qs

app = Flask(__name__)

VIDEO_DIR = 'videos'
CLIP_DIR = 'clips'
API_KEY = 'AIzaSyDQVz7vWIDCmsUn7MgMwDdfBXROP_4leo4'

def delete_existing_files():
    """Delete existing video and clip files."""
    for filename in os.listdir(VIDEO_DIR):
        file_path = os.path.join(VIDEO_DIR, filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")

    for filename in os.listdir(CLIP_DIR):
        file_path = os.path.join(CLIP_DIR, filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")

def download_youtube_video(youtube_url, output_path="videos/video.mp4"):
    try:
        ydl_opts = {
            'format': 'best',
            'outtmpl': output_path,
            'noplaylist': True,
            'quiet': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])
        return output_path
    except Exception as e:
        print(f"Error downloading video: {e}")
        return None

def ensure_9x16_aspect_ratio_with_padding(clip):
    width, height = clip.size
    target_aspect_ratio = 9 / 16

    current_aspect_ratio = width / height

    if current_aspect_ratio > target_aspect_ratio:
        new_height = int(width / target_aspect_ratio)
        padding_top_bottom = (new_height - height) // 2
        new_clip = clip.margin(top=padding_top_bottom, bottom=padding_top_bottom, color=(0, 0, 0))
    else:
        new_width = int(height * target_aspect_ratio)
        padding_left_right = (new_width - width) // 2
        new_clip = clip.margin(left=padding_left_right, right=padding_left_right, color=(0, 0, 0))

    return new_clip

def create_random_clips(video_path, clip_duration=5, num_clips=1):
    clips = []
    try:
        video = VideoFileClip(video_path)
        video_duration = int(video.duration)

        for _ in range(num_clips):
            start_time = random.randint(0, video_duration - clip_duration)
            end_time = start_time + clip_duration
            clip = video.subclip(start_time, end_time)

            clip = ensure_9x16_aspect_ratio_with_padding(clip)

            clips.append((clip, start_time, end_time))

        return clips
    except Exception as e:
        print(f"Error creating clips: {e}")
        return []

def save_clips(clips, base_filename="clips/clip"):
    filenames = []
    for i, (clip, _, _) in enumerate(clips):
        filename = f"{base_filename}_{i+1}.mp4"
        clip.write_videofile(filename, codec='libx264', audio_codec='aac')
        filenames.append(filename)
    return filenames

def get_video_id_from_url(url):
    parsed_url = urlparse(url)
    if parsed_url.hostname == 'www.youtube.com':
        video_id = parse_qs(parsed_url.query).get('v')
        if video_id:
            return video_id[0]
    return None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        youtube_url = request.form['youtube_url']
        
        # Delete existing files before processing new video
        delete_existing_files()

        video_path = download_youtube_video(youtube_url)

        if video_path:
            clips = create_random_clips(video_path)
            clip_filenames = save_clips(clips)
            print(clip_filenames[0].split('/')[1])
            if clip_filenames:
                return redirect(url_for('show_clip', clip_filename=clip_filenames[0].split('/')[1]))
        return "Failed to process video."
    return render_template('index.html')

@app.route('/clip/<clip_filename>')
def show_clip(clip_filename):
    return render_template('clip.html', clip_filename=clip_filename)

@app.route('/clips/<path:filename>')
def download_file(filename):
    return send_from_directory(CLIP_DIR, filename)

if __name__ == '__main__':
    # Create directories if they do not exist
    os.makedirs(VIDEO_DIR, exist_ok=True)
    os.makedirs(CLIP_DIR, exist_ok=True)
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
