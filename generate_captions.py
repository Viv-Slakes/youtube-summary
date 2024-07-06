import yt_dlp
import ffmpeg
import whisper
import os

def download_video(url, video_file="video.mp4"):
    if os.path.exists(video_file):
        os.remove(video_file)


    ydl_opts = {
        'format': 'best',
        'outtmpl': video_file,
        'quiet': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

def extract_audio(video_file, audio_file):
    if os.path.exists(audio_file):
        os.remove(audio_file)
    ffmpeg.input(video_file).output(audio_file).run(capture_stdout=True, capture_stderr=True)

def generate_captions(audio_file):
    model = whisper.load_model("base")
    result = model.transcribe(audio_file)
    return result

def format_timestamp(seconds):
    millis = int((seconds - int(seconds)) * 1000)
    h, m, s = int(seconds // 3600), int((seconds % 3600) // 60), int(seconds % 60)
    return f"{h:02}:{m:02}:{s:02}.{millis:03}"

def save_captions_vtt(captions, caption_file):
    with open(caption_file, 'w', encoding='utf-8') as f:
        f.write("WEBVTT\n")
        f.write("Kind: captions\n")
        f.write("Language: en\n\n")

        for segment in captions['segments']:
            start = format_timestamp(segment['start'])
            end = format_timestamp(segment['end'])
            text = segment['text']
            f.write(f"{start} --> {end}\n{text}\n\n")

def download_and_generate(url, video_file, audio_file, caption_file):
    download_video(url, video_file)
    extract_audio(video_file, audio_file)
    captions = generate_captions(audio_file)
    save_captions_vtt(captions, caption_file)
    print("Captions generated and saved to", caption_file)
