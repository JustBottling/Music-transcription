# main.py

import os

# Import core functions from each module:
from audio_io import load_audio, plot_waveform
from pitch_detect import detect_midi_notes
from midi_writer import write_midi
from notation import midi_to_sheet

def main():
    # 1) Define the filenames we'll use throughout the pipeline:
    audio_file = "input.wav"                          # Input audio (must exist in working directory)
    midi_file  = "transcription_output.mid"           # Where detected notes will be saved as MIDI
    xml_file   = "output_sheet.musicxml"              # Where MusicXML (notation) will be written
    png_file   = "output_sheet.png"                   # Where a rendered PNG of the score will go

    # 2) (Optional) Path to your local MuseScore executable.
    #    Leave blank ("") if you want to skip PNG rendering.
    #    On Windows, you might have MuseScore 4 installed here:
    musescore_exe = r"C:/Program Files/MuseScore 4/bin/MuseScore4.exe"

    # 3) Load the audio and (optionally) display its waveform:
    #    - load_audio returns the waveform array y and the sample rate sr
    y, sr = load_audio(audio_file)
    plot_waveform(y, sr)                              # Visual check: displays a plot of amplitude vs. time

    # 4) Run pitch detection to extract (time, MIDI note) pairs:
    notes = detect_midi_notes(y, sr)
    print(f"[INFO] Detected {len(notes)} notes")      # Log how many note events were found

    # 5) Create a MIDI file from those detected notes:
    write_midi(notes, midi_file)

    # 6) Convert the resulting MIDI into MusicXML—and if you provided a MuseScore path,
    #    generate a PNG rendering of the notation as well.
    midi_to_sheet(
        midi_path=midi_file,
        xml_output=xml_file,
        png_output=png_file if musescore_exe else None,
        musescore_path=musescore_exe
    )

if __name__ == "__main__":
    # Before running the pipeline, ensure the input WAV actually exists:
    if not os.path.exists(audio_file := "input.wav"):
        print("[ERROR] Please put an 'input.wav' file in the project folder.")
    else:
        main()