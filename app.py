from flask import Flask, jsonify, render_template, request, send_from_directory, redirect, url_for
import os
from download_and_boost import download_audio_and_thumbnail, boost_audio_and_save_as_mp3, embed_thumbnail
from pytube import Playlist
from werkzeug.utils import secure_filename
import zipfile
import threading
import time  # For simulating a delay

app = Flask(__name__)

UPLOAD_FOLDER = 'downloads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

tasks = {}

def process_conversion(url, boost_factor, task_id):
    if True:
        if "list=" in url:  # It's a playlist
            playlist = Playlist(url)
            # Fetch and sanitize the playlist title
            playlist_title = secure_filename(playlist.title)

            filenames = []

            i = 0

            for video_url in playlist.video_urls:
                tasks[task_id]["prog"] = 100 * i / len(playlist.video_urls)
                try:
                    audio_filename, thumbnail_filename, safe_title = download_audio_and_thumbnail(video_url)
                    mp3_filename = boost_audio_and_save_as_mp3(audio_filename, boost_factor,UPLOAD_FOLDER + "/" + safe_title)
                    embed_thumbnail(mp3_filename, thumbnail_filename)
                    filenames.append(mp3_filename)

                    # Cleanup
                    os.remove(audio_filename)
                    os.remove(thumbnail_filename)
                    i += 1
                except Exception as e:
                    i += 1
                    pass
            
            # Creating a zip file
            zip_filename = os.path.join(app.config['UPLOAD_FOLDER'], f"{playlist_title}.zip")
            with zipfile.ZipFile(zip_filename, 'w') as zf:
                for fname in filenames:
                    zf.write(fname)
                    os.remove(fname)  # removing the individual mp3 files

            tasks[task_id]['status'] = 'completed'
            tasks[task_id]['result'] = f"{playlist_title}.zip"

        else:
            audio_filename, thumbnail_filename, safe_title = download_audio_and_thumbnail(url)
            mp3_filename = boost_audio_and_save_as_mp3(audio_filename, boost_factor, UPLOAD_FOLDER + "/" + safe_title)
            embed_thumbnail(mp3_filename, thumbnail_filename)
            
            # Cleanup
            os.remove(audio_filename)
            os.remove(thumbnail_filename)

            tasks[task_id]['status'] = 'completed'
            tasks[task_id]['result'] = os.path.basename(mp3_filename)
        

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/convert", methods=['POST'])
def convert():
    if request.method == 'POST':
        url = request.form['url']
        boost_factor = float(request.form['boost_factor'])
        
        task_id = str(time.time())
        tasks[task_id] = {"status": "processing", "prog": 0}

        thread = threading.Thread(target=process_conversion, args=(url, boost_factor, task_id))
        thread.start()

        return jsonify({"status": "Task started", "task_id": task_id})

@app.route('/status/<task_id>', methods=['GET'])
def task_status(task_id):
    task = tasks.get(task_id, {})
    return jsonify(task)

@app.route('/downloads/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)