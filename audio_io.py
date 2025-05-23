# audio_io.py

import librosa               # Core library for audio processing (loading, analysis)
import librosa.display       # Submodule for visualizing audio (waveforms, spectrograms)
import matplotlib.pyplot as plt  # Plotting library used for displaying the waveform

def load_audio(path, sr=None):
    """
    Load an audio file as a time-series waveform.
    
    :param path: Path to the audio file (e.g., .wav, .mp3, .flac).
    :param sr:  Target sampling rate in Hz. If None, preserves the file’s original rate.
    :return:    Tuple (y, sr) where:
                - y:   1D numpy array of audio samples.
                - sr:  Sampling rate of y.
    """
    # librosa.load reads the file at `path` and returns the waveform (y) and its sample rate (sr)
    y, sr = librosa.load(path, sr=sr)
    return y, sr

def plot_waveform(y, sr, figsize=(10, 3), title="Waveform"):
    """
    Render a visual plot of the audio waveform.
    
    :param y:       1D numpy array of audio samples (time series).
    :param sr:      Sampling rate of y, in samples per second (Hz).
    :param figsize: Figure size as (width, height) in inches.
    :param title:   Title text for the plot.
    """
    # Create a new matplotlib figure window with the specified size
    plt.figure(figsize=figsize)
    
    # Draw the waveform: x-axis = time (s), y-axis = amplitude
    librosa.display.waveshow(y, sr=sr)
    
    # Add a title and axis labels for clarity
    plt.title(title)
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")
    
    # Tighten layout to eliminate excess padding around the plot
    plt.tight_layout()
    
    # Display the plot window (pauses code execution until closed)
    plt.show()