# app.py

import os
import traceback
from flask import Flask, request, render_template, send_from_directory, redirect, flash
from audio_io import load_audio
from pitch_detect import detect_midi_notes
from midi_writer import write_midi
from notation import midi_to_sheet
from music21 import environment

# Configure MuseScore path for PNG rendering
us = environment.UserSettings()
mscore_path = os.getenv('MUSESCORE_PATH', '/usr/bin/mscore4')  # Default path for MuseScore 4 on Linux
us['musescoreDirectPNGPath'] = mscore_path

# ─────────────── Flask App Setup ───────────────
app = Flask(__name__)
# Directory where uploaded audio and generated outputs go
app.config['UPLOAD_FOLDER']      = 'static'
# Only accept these audio file extensions
app.config['ALLOWED_EXTENSIONS'] = {'wav', 'mp3', 'flac'}
# Secret key for session cookies & flashing messages
app.secret_key = os.getenv('SECRET_KEY', 'replace-with-secure-secret')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

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
            midi_path = os.path.join(app.config['UPLOAD_FOLDER'], 'output.mid')
            xml_path = os.path.join(app.config['UPLOAD_FOLDER'], 'output.musicxml')
            png_path = os.path.join(app.config['UPLOAD_FOLDER'], 'output_sheet.png')

            # Save uploaded audio to disk
            file.save(audio_path)
            y, sr = load_audio(audio_path)
            notes = detect_midi_notes(y, sr)
            write_midi(notes, midi_path)

            try:
                midi_to_sheet(midi_path, xml_path, png_output=png_path)
            except SystemExit as e:
                app.logger.warning('PNG rendering failed: %s', e)

            return render_template(
                'index.html',
                audio_file=os.path.basename(audio_path),
                midi_file=os.path.basename(midi_path),
                xml_file=os.path.basename(xml_path),
                png_file=None
            )

        return render_template('index.html')
    except BaseException as e:
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