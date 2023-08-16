import os
import requests
from pytube import YouTube
import moviepy.editor as mp
import eyed3

def download_audio_and_thumbnail(url):
    yt = YouTube(url)
    title = yt.title
    safe_title = ''.join([c if c.isalnum() or c.isspace() else "_" for c in title])
    
    # Download thumbnail
    thumbnail_url = yt.thumbnail_url
    thumbnail_filename = f"{safe_title}.jpg"
    with open(thumbnail_filename, 'wb') as file:
        file.write(requests.get(thumbnail_url).content)

    # Download audio and save as mp3 directly
    audio_stream = yt.streams.filter(only_audio=True).first()
    audio_filename = audio_stream.download(output_path='', filename=safe_title)
    
    return audio_filename, thumbnail_filename, safe_title

def boost_audio_and_save_as_mp3(audio_filename, boost_factor, safe_title):
    clip = mp.AudioFileClip(audio_filename)
    boosted_audio = clip.volumex(boost_factor)
    mp3_filename = f"{safe_title}_boosted.mp3"
    boosted_audio.write_audiofile(mp3_filename)
    return mp3_filename

def embed_thumbnail(mp3_filename, thumbnail_filename):
    audio = eyed3.load(mp3_filename)
    if audio.tag is None:
        audio.tag = eyed3.id3.Tag()
        audio.tag.file_info = eyed3.id3.FileInfo(mp3_filename)
    
    with open(thumbnail_filename, 'rb') as img_data:
        audio.tag.images.set(3, img_data.read(), 'image/jpeg')
    audio.tag.save()

def main():
    url = input("Enter the YouTube video URL: ")
    boost_factor = float(input("Enter audio boost factor (e.g., 2 for double volume): "))
    
    print("Downloading audio and thumbnail...")
    audio_filename, thumbnail_filename, safe_title = download_audio_and_thumbnail(url)
    
    print("Boosting audio and saving as MP3...")
    mp3_filename = boost_audio_and_save_as_mp3(audio_filename, boost_factor, safe_title)
    
    # Embed thumbnail into mp3
    print("Embedding thumbnail...")
    embed_thumbnail(mp3_filename, thumbnail_filename)
    
    # Optionally, remove the temporary audio and thumbnail files
    os.remove(audio_filename)
    os.remove(thumbnail_filename)
    
    print(f"Audio saved as {mp3_filename}")

if __name__ == "__main__":
    main()
