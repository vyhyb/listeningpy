"""
This module contains functions for describing audio signals.
"""
import pyloudnorm as pyln
import numpy as np

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