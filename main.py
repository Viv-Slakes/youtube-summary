import configparser
import os
import generate_captions
import captions
import summarize
import highlight

#parse config file
config = configparser.ConfigParser()
config.read('config.ini')

#get the captions file name from the config file
caption_file = f"{config['FILES']['captions_file']}.vtt"
video_file = f"{config['FILES']['video_file']}.mp4"
audio_file = f"{config['FILES']['audio_file']}.wav"

#get the highlight detection model name from the config file
highlight_model = config['MODEL']['highlight_model']

#get the summarization model name from the config file
summarization_model = config['MODEL']['summarization_model']

#get subtitle languages from the config file and convert them to a list
subtitle_languages = config['CAPTIONS']['subtitle_languages'].split(',')

if __name__ == "__main__":
    video_url = input("Enter the video URL: ")
    try:
        caption_download = captions.download_english_captions(video_url, caption_file, subtitle_languages)
    except Exception as e:
        print(f"Error downloading captions: {e}")
        exit(1)
    
    match caption_download:
        case False:
            try:
                generate_captions.download_and_generate(video_url, video_file, audio_file, caption_file)
            except Exception as e:
                print(f"Error downloading or generating captions: {e}")
                exit(1)

    summary = summarize.summarize_text(caption_file, summarization_model)

    timestamp = highlight.generate_highlights(caption_file, highlight_model, video_url)

    with open("Summary.txt", "w") as file:
        file.write(f"Summary: {summary}\n")
        file.write(f"\n\n\nHighlight: {timestamp}\n")

