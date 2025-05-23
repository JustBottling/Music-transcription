# notation.py
from music21 import converter, environment

def midi_to_sheet(midi_path, xml_output, png_output=None, musescore_path=None):
    """
    Convert a MIDI file into MusicXML (and optionally render a PNG image of the score).
    
    :param midi_path: str
        File path to the input .mid file to be parsed.
    :param xml_output: str
        File path where the resulting .musicxml will be saved.
    :param png_output: str or None, optional
        If provided, this is the file path where a rendered PNG of the score will be saved.
    :param musescore_path: str or None, optional
        If provided, overrides the default MuseScore binary path for PNG rendering.
    """

    # Parse the MIDI file into a music21 Stream (Score) object
    score = converter.parse(midi_path)

    # If the user supplied a custom MuseScore executable, configure music21 to use it
    if musescore_path:
        us = environment.UserSettings()
        # Tell music21 where to find the MuseScore CLI for direct PNG export
        us['musescoreDirectPNGPath'] = musescore_path

    # Write out the parsed score as MusicXML
    score.write('musicxml', fp=xml_output)
    print(f"[INFO] MusicXML written to {xml_output}")

    # If the caller requested a PNG rendering...
    if png_output:
        # music21 can directly produce a PNG via its internal write method:
        # 'musicxml.png' tells it to write MusicXML then render to PNG
        auto_png = score.write('musicxml.png')
        
        # The above returns the path to an automatically generated PNG.
        # Move/rename it to the caller’s desired location.
        import os, shutil
        shutil.move(auto_png, png_output)
        print(f"[INFO] PNG score written to {png_output}")