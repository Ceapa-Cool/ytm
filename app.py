from flask import Flask, render_template, request, send_from_directory, redirect, url_for
import os
from download_and_boost import download_audio_and_thumbnail, boost_audio_and_save_as_mp3, embed_thumbnail


app = Flask(__name__)

UPLOAD_FOLDER = 'downloads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/downloads/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)


@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        boost_factor = float(request.form['boost_factor'])
        
        audio_filename, thumbnail_filename, safe_title = download_audio_and_thumbnail(url)
        mp3_filename = boost_audio_and_save_as_mp3(audio_filename, boost_factor,UPLOAD_FOLDER + "/" + safe_title)
        embed_thumbnail(mp3_filename, thumbnail_filename)
        
        # Cleanup
        os.remove(audio_filename)
        os.remove(thumbnail_filename)
        
        return redirect(url_for('download_file', filename=os.path.basename(mp3_filename)))
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)
