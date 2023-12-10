"""
This module contains functions for describing audio signals.
"""
import pyloudnorm as pyln
import numpy as np
import soundfile as sf
import os

def audio_stats(audio: np.ndarray, fs: int):
    """
    Calculate various audio statistics.

    Parameters
    ----------
    audio : np.ndarray
        The audio signal as a numpy array.
    fs : int
        The sample rate of the audio signal.

    Returns
    -------
    tuple
        A tuple containing the peak amplitude, RMS amplitude, and integrated loudness of the audio signal.
    """
    peak = 20*np.log10(abs(audio).max())
    rms = 20*np.log10(np.sqrt(np.mean(audio**2)))
    meter = pyln.Meter(fs)
    loudness = meter.integrated_loudness(audio)
    return peak, rms, loudness

def write_audio(
        audio: np.ndarray, 
        fs: int, 
        destination: str, 
        filename: str
        ) -> None:
    """
    Write audio data to a file.

    Parameters
    ----------
    audio : np.ndarray
        The audio data to be written.
    fs : int
        The sample rate of the audio data.
    destination : str
        The destination directory where the file will be saved.
    filename : str
        The name of the file.

    Returns
    -------
    None
    """
    if not os.path.exists(destination):
        os.makedirs(destination)
    sf.write(os.path.join(destination, filename), audio, fs)