# app.py

import os
import traceback
from flask import (
    Flask,            # Core Flask application class
    request,          # To access incoming request data (files, form data)
    render_template,  # For rendering HTML templates
    send_from_directory,  # To serve static files from a directory
    redirect,         # To redirect the client to a different endpoint
    flash             # To show one-time messages to the user
)
from audio_io import load_audio             # Load & preprocess audio
from pitch_detect import detect_midi_notes  # Pitch-to-note conversion
from midi_writer import write_midi          # Write detected notes to MIDI
from notation import midi_to_sheet          # Convert MIDI → MusicXML (and optionally PNG)
from music21 import environment             # For configuring MuseScore path

# ─────────────── MuseScore Configuration ───────────────
# Allow user to specify their local MuseScore executable via environment var
mscore = os.getenv('MUSESCORE_PATH')
if mscore:
    us = environment.UserSettings()
    # Tell music21 where to find MuseScore for PNG rendering
    us['musescoreDirectPNGPath'] = mscore

# ─────────────── Flask App Setup ───────────────
app = Flask(__name__)
# Directory where uploaded audio and generated outputs go
app.config['UPLOAD_FOLDER']      = 'static'
# Only accept these audio file extensions
app.config['ALLOWED_EXTENSIONS'] = {'wav', 'mp3', 'flac'}
# Secret key for session cookies & flashing messages
app.secret_key = os.getenv('SECRET_KEY', 'replace-with-secure-secret')

def allowed_file(filename):
    """
    Check that a filename has one of the allowed extensions.
    """
    return (
        '.' in filename and
        filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']
    )

# ─────────────── Main Route ───────────────
@app.route('/', methods=['GET', 'POST'])
def index():
    try:
        # Handle form submission
        if request.method == 'POST':
            file = request.files.get('audio')
            # Validate upload presence and extension
            if not file or not allowed_file(file.filename):
                flash('Please upload a valid WAV, MP3, or FLAC file.')
                return redirect(request.url)

            # Build file paths for input audio and outputs
            ext        = file.filename.rsplit('.', 1)[1].lower()
            audio_path = os.path.join(app.config['UPLOAD_FOLDER'], f'input.{ext}')
            midi_path  = os.path.join(app.config['UPLOAD_FOLDER'], 'output.mid')
            xml_path   = os.path.join(app.config['UPLOAD_FOLDER'], 'output.musicxml')
            # We skip PNG rendering here to save resources
            # png_path = os.path.join(app.config['UPLOAD_FOLDER'], 'output_sheet.png')

            # Save uploaded audio to disk
            file.save(audio_path)

            # 1) Load audio into waveform array y, sampling rate sr
            y, sr = load_audio(audio_path)
            # 2) Detect MIDI notes from waveform
            notes = detect_midi_notes(y, sr)
            # 3) Write those notes out as a .mid file
            write_midi(notes, midi_path)
            # 4) Convert .mid to MusicXML (skipping PNG)
            midi_to_sheet(midi_path, xml_path, png_output=None)

            # Render results page with links to generated files
            return render_template(
                'index.html',
                audio_file=os.path.basename(audio_path),
                midi_file=os.path.basename(midi_path),
                xml_file=os.path.basename(xml_path),
                png_file=None
            )

        # On GET, just show the upload form
        return render_template('index.html')

    except BaseException:
        # Catch any error, log its traceback, and show a friendly message
        tb = traceback.format_exc()
        app.logger.error('Unhandled exception in index():\n%s', tb)
        flash('Something went wrong. Please try again.')
        return render_template('index.html'), 500

# ─────────────── Static File Serving ───────────────
@app.route('/static/<path:filename>')
def static_files(filename):
    """
    Serve files from the UPLOAD_FOLDER so the browser can fetch
    audio, MIDI, MusicXML (and PNG if used).
    """
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ─────────────── App Entry Point ───────────────
if __name__ == '__main__':
    # Run Flask’s built-in server in debug mode for local development
    app.run(debug=True)