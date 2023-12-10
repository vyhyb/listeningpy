"""
This module contains functions for normalizing audio signals.
"""
import numpy as np
from scipy.signal import resample
import pyloudnorm as pyln
import mosqito
import logging

def fs_to_pressure(
        audio : np.ndarray,
        dbfs_db : float,
        p0 : float=2e-5):
    """Converts audio from full-scale (FS) to pressure (Pa).

    Parameters
    ----------
    audio : np.ndarray
        The input audio signal.
    dbfs_db : float
        The sound pressure level associated with 0 dBFS.
    p0 : float, optional
        The reference sound pressure in pascals (Pa), by default 2e-5.

    Returns
    -------
    np.ndarray
        The audio signal converted to pressure (Pa).
    """
    ratio_db = p0 * 10 ** (dbfs_db/20)
    audio_pressure = audio * ratio_db
    return audio_pressure

def eq_loudness_lvl(
        audio_pressure : np.ndarray, 
        fs : int, 
        field_type : str="diffuse"):
    """
    Calculate the log average loudness level of an audio signal.

    Parameters
    ----------
    audio_pressure : ndarray
        Array containing the audio pressure values.
    fs : int
        Sampling frequency of the audio signal.
    field_type : str, optional
        Type of sound field. Possible values are "diffuse" (default) or "free".
    
    Returns
    -------
    float
        The loudness level in phon.
    tuple
        A tuple containing the loudness values and corresponding time values.
    """
    audio_pressure = audio_pressure.mean(axis=1)
    audio_pressure = resample(audio_pressure, int(audio_pressure.shape[0]*48000/fs))
    fs=48000
    N, N_spec, _, time = mosqito.loudness_zwtv(
        audio_pressure, 
        fs, 
        field_type=field_type
    )
    loud_lvl = 40 + 10*np.log2(N.mean())
    return loud_lvl, (N, time)

def peak_normalize(
        audio : np.ndarray, 
        fs : int, 
        peak : float=0, 
        reference : np.ndarray=None
        ) -> tuple[np.ndarray, float]:
    """
    Normalize the peak level of an audio signal.

    Parameters
    ----------
    audio : np.ndarray
        The input audio signal.
    fs : int
        The sample rate of the audio signal.
    peak : float, optional
        The desired peak level in decibels (dB), by default 0.
    reference : np.ndarray, optional
        The reference audio signal for normalization, by default None.

    Returns
    -------
    tuple[np.ndarray, float]
        A tuple containing the normalized audio signal and the sample rate.

    Notes
    -----
    This function normalizes the peak level of the input audio signal to the specified peak level.
    If a reference audio signal is provided, the normalization is performed relative to the peak level of the reference signal.
    If no reference signal is provided, the normalization is performed relative to the peak level of the input audio signal itself.
    The normalization factor is calculated based on the desired peak level and the maximum absolute value of the reference signal.
    """
    if type(reference) == type(None):
        reference = audio
    factor = 10**(peak/20) / abs(reference).max()
    logging.info(f'Stimuli was peak normalized to {peak:.1f} dB')
    return audio * factor, fs

def rms_normalize(
        audio : np.ndarray, 
        fs : int, 
        rms : float=-9, 
        reference : np.ndarray=None
        ) -> tuple[np.ndarray, float]:
    """
    Normalize the audio signal to a target RMS level.

    Parameters
    ----------
    audio : np.ndarray
        The input audio signal.
    fs : int
        The sample rate of the audio signal.
    rms : float, optional
        The target RMS level in decibels (dB), by default -9 dB.
    reference : np.ndarray, optional
        The reference audio signal used for normalization, by default None.

    Returns
    -------
    tuple[np.ndarray, float]
        A tuple containing the normalized audio signal and the sample rate.

    Notes
    -----
    This function normalizes the audio signal to a target RMS level specified in decibels (dB).
    If a reference audio signal is provided, the normalization is performed relative to the RMS level of the reference signal.
    If no reference signal is provided, the normalization is performed relative to the RMS level of the input audio signal.
    The resulting normalized audio signal is multiplied by a scaling factor to achieve the target RMS level.
    """
    if type(reference) == type(None):
        reference = audio
    factor = 10**(rms/20) / np.sqrt(np.mean(reference**2))
    logging.info(f'Stimuli was normalized to RMS average of {rms:.1f} dB')
    return audio * factor, fs

def lufs_normalize(
        audio : np.ndarray, 
        fs : int, 
        lufs : float=-16, 
        reference : np.ndarray=None
        ) -> tuple[np.ndarray, int]:
    """Normalize the loudness of an audio signal to a target LUFS level.

    Parameters
    ----------
    audio : np.ndarray
        The input audio signal as a NumPy array.
    fs : int
        The sample rate of the audio signal.
    lufs : float, optional
        The target loudness level in LUFS (Loudness Units Full Scale). Default is -16 LUFS.
    reference : np.ndarray, optional
        The reference audio signal to calculate the loudness. If not provided, the input audio signal is used as the reference.

    Returns
    -------
    tuple[np.ndarray, int]
        A tuple containing the normalized audio signal as a NumPy array and the sample rate as an int.
    """
    if type(reference) == type(None):
        reference = audio
    meter = pyln.Meter(fs)
    loudness = meter.integrated_loudness(reference)
    delta = lufs - loudness
    factor = 10**(delta/20)
    logging.info(f'Stimuli was loudness normalized to {lufs:.1f} dB LUFS')
    return audio * factor, fs

def ir_sum_normalize(
        audio : np.ndarray, 
        ir : np.ndarray, 
        fs : int, 
        ir_sum : float=-9):
    """Normalize the audio based on the sum of the impulse response (IR).

    This function normalizes the given audio signal based on the sum of the absolute values of the impulse response (IR).
    The normalization factor is calculated as 10^(ir_sum/20) divided by the sum of the absolute values of the IR.
    The audio signal is then multiplied by this factor to achieve the desired normalization.

    Parameters
    ----------
    audio : np.ndarray
        The input audio signal.
    ir : np.ndarray
        The impulse response (IR) signal.
    fs : int
        The sampling rate of the audio signal.
    ir_sum : float, optional
        The desired sum of the IR in decibels (dB), by default -9.

    Returns
    -------
    np.ndarray
        The normalized audio signal.
    int
        The sampling rate of the normalized audio signal.
    """
    factor = 10**(ir_sum/20) / abs(ir).sum()
    logging.info(f'Stimuli was normalized based IR sum to {ir_sum:.1f} dB')
    return audio * factor, fs

def zwicker_loudness_normalize(
        audio : np.ndarray,
        fs : int,
        target_phon : float,
        dbfs_db: float,
        return_ratio: bool = False
        ) -> tuple[np.ndarray, int]:
    audio_pressure = fs_to_pressure(audio, dbfs_db)
    loud_lvl, loudness = eq_loudness_lvl(audio_pressure, fs)
    loud_diff = target_phon - loud_lvl
    logging.info(f"Before normalization: N={loud_lvl:.1f}")
    ratio_loud = 1
    n = 0
    while abs(loud_diff) > 0.1:
        ratio_loud *= 10 ** ((loud_diff)/20)
        audio_pressure_it = audio_pressure * ratio_loud
        loud_lvl, loudness = eq_loudness_lvl(audio_pressure_it, fs)
        loud_diff = target_phon - loud_lvl
        print(loud_diff)
        n += 1
    logging.info(f" After {n}th normalization: N={loud_lvl:.1f}")
    audio *= ratio_loud
    headroom = 1/abs(audio).max()
    headroom_db = 20*np.log10(headroom)
    if abs(audio).max() > 1:
        logging.warning("Audio signal clipped after normalization.")
        raise ValueError("Audio signal clipped after normalization. "+
                         f"The level overflows for {headroom_db:.2f} dB. "+
                         "Adjust headphone level.")
    else:
        logging.info(f"Audio signal normalized to {target_phon:.2f} phons.")
        logging.info(f"Normalization factor: {ratio_loud:.2f}")
        logging.info(f"Headroom: {-headroom_db:.2f} dB")
    
    if return_ratio:
        ret = audio, fs, ratio_loud
    else:
        ret = audio, fs
    return ret


