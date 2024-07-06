import yt_dlp
import os
import glob

def download_english_captions(video_url, caption_file="captions.vtt", subtitle_languages=['en']):

    
    if os.path.exists(caption_file):
        os.remove(caption_file)

    ydl_opts = {
        'writesubtitles': True,
        'subtitleslangs': subtitle_languages,
        'skip_download': True,
        'outtmpl': caption_file,
        'quiet': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(video_url, download=False)
        subtitles = info_dict.get('subtitles', {})
        
        #check for predefined subtitle languages
        english_subtitle_keys = [key for key in subtitles if any(key.startswith(pref) for pref in subtitle_languages)]
        
        if not english_subtitle_keys:
            # If predefined keys are not found, look for any keys starting with 'en'
            english_subtitle_keys = [key for key in subtitles if key.startswith('en')]
        
        if english_subtitle_keys:
            print("Available subtitles:")
            for idx, key in enumerate(english_subtitle_keys):
                print(f"{idx + 1}: {key}")
            print(f"{len(english_subtitle_keys) + 1}: None (Do not download any subtitles)")

            choice = input(f"Choose a subtitle to download (1-{len(english_subtitle_keys) + 1}): ")
            if int(choice) == len(english_subtitle_keys) + 1:
                return False
            else:
                chosen_key = english_subtitle_keys[int(choice) - 1]
                
                # Update ydl_opts to specify the chosen subtitle
                ydl_opts['subtitleslangs'] = [chosen_key]
                
                print(f"Downloading subtitles: {chosen_key}")
                with yt_dlp.YoutubeDL(ydl_opts) as ydl_with_download:
                    ydl_with_download.download([video_url])
                
                # Step 2: Identify the downloaded subtitle file
                # Assuming the download happens in the current directory and only one .vtt file is expected
                vtt_files = glob.glob('*.vtt')
                for vtt_file in vtt_files:
                    if chosen_key in vtt_file:  # Check if the chosen subtitle key is part of the filename
                        # Step 3: Rename the file
                        new_filename = vtt_file.split('.vtt')[0] + '.vtt'
                        os.rename(vtt_file, new_filename)
                print("Captions downloaded successfully.")
                return True
        else:
            print("Captions are not available for this video.")
            return False

