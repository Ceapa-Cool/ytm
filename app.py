from flask import Flask, render_template, request, send_from_directory, redirect, url_for
import os
from download_and_boost import download_audio_and_thumbnail, boost_audio_and_save_as_mp3, embed_thumbnail
from pytube import Playlist
from werkzeug.utils import secure_filename
import zipfile

app = Flask(__name__)

UPLOAD_FOLDER = 'downloads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        boost_factor = float(request.form['boost_factor'])
        
        if "list=" in url:  # It's a playlist
            playlist = Playlist(url)
            # Fetch and sanitize the playlist title
            playlist_title = secure_filename(playlist.title)

            filenames = []
            for video_url in playlist.video_urls:
                try:
                    audio_filename, thumbnail_filename, safe_title = download_audio_and_thumbnail(video_url)
                    mp3_filename = boost_audio_and_save_as_mp3(audio_filename, boost_factor,UPLOAD_FOLDER + "/" + safe_title)
                    embed_thumbnail(mp3_filename, thumbnail_filename)
                    filenames.append(mp3_filename)

                    # Cleanup
                    os.remove(audio_filename)
                    os.remove(thumbnail_filename)
                except Exception as e:
                    pass
            
            # Creating a zip file
            zip_filename = os.path.join(app.config['UPLOAD_FOLDER'], f"{playlist_title}.zip")
            with zipfile.ZipFile(zip_filename, 'w') as zf:
                for fname in filenames:
                    zf.write(fname)
                    os.remove(fname)  # removing the individual mp3 files

            return send_from_directory(app.config['UPLOAD_FOLDER'], f"{playlist_title}.zip", as_attachment=True)
        else:
            audio_filename, thumbnail_filename, safe_title = download_audio_and_thumbnail(url)
            mp3_filename = boost_audio_and_save_as_mp3(audio_filename, boost_factor, UPLOAD_FOLDER + "/" + safe_title)
            embed_thumbnail(mp3_filename, thumbnail_filename)
            
            # Cleanup
            os.remove(audio_filename)
            os.remove(thumbnail_filename)
            
            return send_from_directory(app.config['UPLOAD_FOLDER'], os.path.basename(mp3_filename), as_attachment=True)

    return render_template('index.html')

@app.route('/downloads/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)