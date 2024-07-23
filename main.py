from flask import Flask, request, jsonify, render_template,send_from_directory
import os
from googleapiclient.discovery import build
from urllib.parse import urlparse, parse_qs
import random
from moviepy.editor import VideoFileClip
import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

app = Flask(__name__, static_folder='clips')

@app.route('/')
def index():
    return render_template('index.html')


def get_video_id_from_url(url):
    parsed_url = urlparse(url)
    if parsed_url.hostname == 'www.youtube.com':
        video_id = parse_qs(parsed_url.query).get('v')
        if video_id:
            return video_id[0]
    return None


def list_and_select_audio_tracks(youtube_url):
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'quiet': True,
            'dumpjson': True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(youtube_url, download=False)
            formats = info_dict.get('formats', [])

            audio_tracks = [
                f for f in formats if 'audio' in f.get('format', '')]
            tracks = []
            for index, track in enumerate(audio_tracks):
                format_id = track['format_id']
                print(
                    f"{index + 1}: {format_id} - {track.get('format', 'Unknown Format')}")
                tracks.append(
                    f"{index + 1}: {format_id} - {track.get('format', 'Unknown Format')}")
            return tracks

    except Exception as e:
        print(f"Error listing audio tracks: {e}")
        return None


def download_youtube_video(youtube_url, audio_format_id=None, output_path="video.mp4"):
    print("audio_format_id - ", audio_format_id)
    try:
        ydl_opts = {
            'format': f'bestaudio[format_id={audio_format_id}]' if audio_format_id else 'best',
            'outtmpl': output_path,
            'noplaylist': True,
            'quiet': True,
            'merge_output_format': 'mp4',
            'writesubtitles': True,
            'writeinfojson': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])
        return output_path
    except Exception as e:
        print(f"Error downloading video: {e}")
        # Fallback to download the original video
        try:
            print("Falling back to download the original video.")
            ydl_opts = {
                'format': 'best',
                'outtmpl': output_path,
                'noplaylist': True,
                'quiet': True,
                'merge_output_format': 'mp4',
                'writesubtitles': True,
                'writeinfojson': True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([youtube_url])
            return output_path
        except Exception as fallback_e:
            print(f"Error downloading the original video: {fallback_e}")
            return None


def ensure_9x16_aspect_ratio_with_padding(clip):
    width, height = clip.size
    target_aspect_ratio = 9 / 16

    current_aspect_ratio = width / height

    if current_aspect_ratio > target_aspect_ratio:
        new_height = int(width / target_aspect_ratio)
        padding_top_bottom = (new_height - height) // 2
        new_clip = clip.margin(top=padding_top_bottom,
                               bottom=padding_top_bottom, color=(0, 0, 0))
    else:
        new_width = int(height * target_aspect_ratio)
        padding_left_right = (new_width - width) // 2
        new_clip = clip.margin(left=padding_left_right,
                               right=padding_left_right, color=(0, 0, 0))

    return new_clip


def create_random_clips(video_path, clip_duration=50, num_clips=1):
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


def save_clips(clips, base_filename="clip"):
    filenames = []
    for i, (clip, _, _) in enumerate(clips):
        filename = f"{base_filename}_{i+1}.mp4"
        clip.write_videofile(os.path.join('clips', filename), codec='libx264', audio_codec='aac')
        filenames.append(filename)
    return filenames


@app.route('/process-url', methods=['POST'])
def process_url():
    try:
        data = request.get_json()
        youtube_url = data['url']
        video_id = get_video_id_from_url(youtube_url)
        if video_id:
            audio_format = list_and_select_audio_tracks(youtube_url)
            # Extracting format IDs
            audio_format_ids = [track.split(' ')[1] for track in audio_format]
            return jsonify({'audio_format_ids': audio_format_ids, 'youtube_url': youtube_url})
    except Exception as e:
        print(f"Error processing URL: {e}")
        return jsonify({'error': 'Failed to process URL'}), 400


@app.route('/process-selectors', methods=['POST'])
def process_selectors():
    try:
        data = request.get_json()
        selector1 = data['selector1']
        youtube_url = data['youtube_url']
        video_path = download_youtube_video(youtube_url, selector1)
        if video_path:
            clips = create_random_clips(video_path)
            clip_filenames = save_clips(clips)

            dynamic_html = ''.join([f'<video src="/clips/{filename}" controls></video><br>' for filename in clip_filenames])
            return dynamic_html
        else:
            return "Error processing video", 500
    except Exception as e:
        print(f"Error processing selectors: {e}")
        return "Error processing selectors", 500


@app.route('/clips/<path:filename>')
def serve_clip(filename):
    return send_from_directory(app.static_folder, filename)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
