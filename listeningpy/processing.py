"""
This module contains functions for processing audio signals.
It contains functions for basic processing, such as normalization, convolution, etc.
"""

import numpy.fft as fft
from numpy import ndarray, where, zeros_like
import scipy.signal as signal
import logging
import pyloudnorm as pyln
from listeningpy.normalization import (
    peak_normalize,
    rms_normalize,
    ir_sum_normalize,
    lufs_normalize
    )
from listeningpy.audiotools import audio_stats

FILTERS = ['hp', 'lp']

# logging.basicConfig(level=logging.DEBUG)

### BASIC PROCESSING ###

def straight(
        audio: ndarray, 
        fs: int,
        **kwargs
        ) -> tuple[ndarray, int]:
    '''Passes the audio without further processing.
    
    Parameters
    ----------
    audio : numpy.ndarray
        2-D audio array

    Returns
    -------
    audio : numpy.ndarray
        2-D audio array
    '''
    return audio, fs

def gain_adjustment(
        stimuli: ndarray,
        fs_stimuli: int,
        gain: float
        ) -> tuple[ndarray, int]:
    """Adjusts the gain of the stimuli.

    This function applies a gain adjustment to the input stimuli based on the specified gain value.
    The gain adjustment is applied by multiplying the stimuli by a factor calculated from the gain value.

    Parameters
    ----------
    stimuli : ndarray
        The input stimuli to be adjusted.
    fs_stimuli : int
        The sampling rate of the stimuli.
    gain : float
        The gain value in decibels (dB) to be applied.

    Returns
    -------
    tuple[ndarray, int]
        A tuple containing the adjusted stimuli and the sampling rate.

    """
    factor = 10**(gain/20)
    stimuli *= factor
    audio_stats_logging(stimuli, fs_stimuli)
    return stimuli, fs_stimuli

def convolution(
        in1: ndarray,
        fs_in1: int,
        in2: ndarray,
        fs_in2: int,
        fade_out: bool=True,
        normalization: str='ir_sum',
        normalization_target: float=-6,
        normalization_prefilter: str='',
        prefilter_critical_freq = 200
        ) -> tuple[ndarray, int]:
    '''Performs convolution between IR and stimuli.

    Should accept both mono and stereo signals, 
    but both in a form of 2D array.
    
    Parameters
    ----------
    in1 : numpy.ndarray
        2-D audio array (IR)
    fs_in1 : int
        IR sampling frequency
    in2 : numpy.ndarray
        2-D audio array (stimulus)
    fs_in2 : int
        sampling frequency of stimuli
    fade_out : bool, optional
        Flag indicating whether to apply fade-out to the IR signal, by default True
    normalization : str, optional
        Type of normalization to apply, by default 'ir_sum'. The alternatives can be peak, rms, lufs, ir_sum.
    normalization_target : float, optional
        Target value for normalization, by default -6
    normalization_prefilter : str, optional
        Type of prefiltering to apply before normalization, by default ''
    prefilter_critical_freq : int, optional
        Critical frequency for the prefilter, by default 200

    Returns
    -------
    audio : numpy.ndarray
        2-D audio array
    fs_in1 : int
        IR sampling frequency
    '''
    if fs_in1 == fs_in2:
        logging.debug('IR and Stimuli sample rates are equal, no resampling needed.')
    else:
        logging.debug('IR and Stimuli sample rates differs, IR audio was resampled.')
        in1, fs_in1 = match_fs(in1, fs_in2, fs_in1)
    
    logging.debug(f'Stimuli shape before convolution: {in2.shape}')
    logging.debug(f'IR shape before convolution:      {in1.shape}')
    logging.debug(f"The peak values are {abs(in2).max()} and {abs(in1).max()}")

    if fade_out:
        HFT90D = [1, 1.942604, 1.340318, 0.440811, 0.043097]
        size = int(fs_in2/12.5)
        fade_out_win = signal.windows.general_cosine(2*size,HFT90D)[-size:]
        fade_out_win = fade_out_win/fade_out_win.max()
        for i in in1.T:
            i[-size:] *= fade_out_win
        logging.debug(f'HFT90D Fade-out applied to last 0.1 s of IR.')
    
    # convolution
    audio = signal.oaconvolve(in2.T, in1.T)[[0,-1]]
    audio = audio.T
    
    # prefiltering for normalization
    if normalization_prefilter == '':
        audio_prefiltered = audio
    elif normalization_prefilter in FILTERS:
        sos = signal.butter(
            12,
            prefilter_critical_freq,
            normalization_prefilter,
            fs=fs_in1,
            output='sos')
        audio_prefiltered = signal.sosfilt(sos, audio, axis=0)
    else:
        logging.warning('Specified normalization prefilter is not implemented.')

    # normalization
    if normalization == 'peak':
        audio,_ = peak_normalize(
            audio, 
            fs_in1, 
            peak=normalization_target,
            reference=audio_prefiltered
            )
    elif normalization == 'ir_sum':
        audio,_ = ir_sum_normalize(
            audio, 
            ir = in1, 
            fs = fs_in1, 
            ir_sum=normalization_target
            )
    elif normalization == 'rms':
        audio,_ = rms_normalize(
            audio, 
            fs_in1, 
            rms=normalization_target,
            reference=audio_prefiltered
            )
    elif normalization == 'lufs':
        audio,_ = lufs_normalize(
            audio, 
            fs_in1, 
            lufs=normalization_target,
            reference=audio_prefiltered
            )
    elif normalization is None:
        logging.info('Normalization was not applied.')
    else:
        logging.info('Specified normalization type not implemented.')
    
    logging.debug(f'Stimuli shape after convolution: {audio.shape}')
    
    audio_stats_logging(audio, fs_in1)
    return audio, fs_in1

# def lf_dirac_combination(
#         lf_ir: ndarray,
#         fs_lf_ir: int,
#         crossover: int=200,
#         span: int=2,
#         norm_factor=None
#         ) -> tuple[ndarray, int]:
#     """NOT RECOMMENDED, USE lf_convolution INSTEAD.
#     """
#     dirac = zeros_like(lf_ir)
#     logging.debug(f'dirac shape {dirac.shape}')
#     dirac[where(lf_ir.sum(axis=1) == lf_ir.sum(axis=1).max())] = 1
#     logging.debug(f'dirac shape {dirac.shape}')

#     sos = signal.butter(12, crossover, 'hp', fs=fs_lf_ir, output='sos')
#     dirac_filtered = signal.sosfilt(sos, dirac, axis=0)
#     sos2 = signal.butter(12, crossover, 'lp', fs=fs_lf_ir, output='sos')
#     lf_ir_filtered = signal.sosfilt(sos2, lf_ir, axis=0)

#     tf_low = fft.fft(lf_ir, axis=0)
#     tf_high = fft.fft(dirac_filtered, axis=0)
    
#     freqs = fft.fftfreq(tf_low.shape[0], 1/fs_lf_ir)
#     crossover_idx = int(crossover/freqs[1])
#     if norm_factor == None:
#         norm_factor = (
#             (abs(tf_low).sum(axis=1)[crossover_idx:int(crossover_idx*span)]).sum(axis=0)/
#             (abs(tf_high).sum(axis=1)[crossover_idx:int(crossover_idx*span)]).sum(axis=0)
#         )
#     logging.info(f'norm factor {norm_factor}')

#     lf_ir_filtered = lf_ir_filtered/norm_factor
#     dirac_norm_filtered = dirac_filtered

    

#     ir_full = dirac_norm_filtered +lf_ir_filtered
#     return ir_full

def match_fs(
        in1 : ndarray,
        fs_in2 : int,
        fs_in1 : int
        ) -> tuple[ndarray, int]:
    '''Resamples in1 to match fs_in2.'''
    logging.info(f'old length:{in1.shape[0]}, old fs:{fs_in1}')
    new_len = int(in1.shape[0]*fs_in2/fs_in1)
    new_in1 = signal.resample(in1, new_len)
    fs_in1 = fs_in2
    logging.info(f'new length:{new_in1.shape[0]}, new fs:{fs_in1}')
    return new_in1, fs_in1

### BASIC ADAPTIVE PROCESSING METHODS ###

def up_down(
        audio: ndarray, 
        direction: bool, 
        last: float=0, 
        step: float=2
        ) -> ndarray:
    '''Changes the volume of audio based on direction and step in dB.
    
    Parameters
    ----------
    audio : numpy.ndarray
        2-D audio array
    direction : bool
        True value means up, False means down
    last : float
        volume level for previous stimuli
    step : float
        step size in dB, 2 dB by default

    Returns
    -------
    audio : numpy.ndarray
        2-D audio array
    '''
    audio *= 10**(last/20)
    ratio = 10**(step/20)
    if direction:
        audio*ratio
    else:
        audio/ratio    
    return audio

def up_down_noise(
        audio: ndarray,
        noise: ndarray,
        direction: bool,
        last: float=0,
        step: float=2
        ) -> ndarray:
    """Add noise to the audio signal in an up or down direction.

    Parameters
    ----------
    audio : ndarray
        The audio signal to which the noise will be added.
    noise : ndarray
        The noise signal to be added to the audio.
    direction : bool
        The direction of the noise addition. True for up, False for down.
    last : float, optional
        The last value of the noise added in the previous call, by default 0.
    step : float, optional
        The step size for the noise addition, by default 2.

    Returns
    -------
    ndarray
        The audio signal with the added noise.
    """
    noise = noise[:audio.shape[0]]
    noise = up_down(audio, direction, last, step)
    audio += noise
    return audio

def audio_stats_logging(
        audio : ndarray, 
        fs : int
        ) -> None:
    peak, rms, loudness = audio_stats(audio, fs)
    logging.info(f'Processed audio stats: peak: {peak:.2f} dBFS, '+
        f'rms: {rms:.2f} dBFS, loudness: {loudness:.2f} dB LUFS.')
    if abs(audio).max() > 1:
        logging.warning(f'Clipping occured on full scale after processing!')

