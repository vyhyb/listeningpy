"""Helper functions for preparing ABX test stimuli. 
"""
import soundfile as sf
import os
import logging
from scipy.signal import resample
import mosqito
import numpy as np
from typing import List, Tuple, Union
import numpy as np

from listeningpy.processing import convolution
from listeningpy.normalization import peak_normalize
logging.basicConfig(format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.INFO)

def read_ir_list(
        ir_folder_path: str
        ) -> Tuple[List[np.ndarray], List[int], List[str]]: 
    """
    Read a list of impulse response (IR) files from a given folder path.

    Parameters
    ----------
    ir_folder_path : str
        The path to the folder containing the IR files.

    Returns
    -------
    Tuple[List[np.ndarray], List[int], List[str]]
        A tuple containing the following:
        - irs (List[np.ndarray]): A list of impulse response arrays.
        - fs_irs (List[int]): A list of sample rates corresponding to each IR.
        - variants (List[str]): A list of variant names for each IR file.
    """    
    irs = []
    fs_irs = []
    ir_files = os.listdir(ir_folder_path)
    ir_paths = []
    variants = []
    for i in ir_files:
        ir_paths.append(os.path.join(ir_folder_path, i))
        char_idx_low = i.rfind("_")+1
        variants.append(i[char_idx_low:-4])

    logging.debug(variants)

    for i in ir_paths:
        ir, fs_ir = sf.read(i, always_2d=True)
        irs.append(ir)
        fs_irs.append(fs_ir)
    return irs, fs_irs, variants

def batch_convolution(
        irs: List[np.ndarray], 
        fs_irs: List[int], 
        stimuli: np.ndarray, 
        fs_stimuli: int, 
        variants: List[str], 
        stim_str: str, 
        peak_lvl: int = -12, 
        prefix: str = "13ab00ad", 
        destination: str = "."
        ) -> None:
    """
    Perform batch convolution of impulse responses with stimuli and save the resulting audio files.

    Parameters
    ----------
    irs : List[np.ndarray]
        List of impulse response arrays.
    fs_irs : List[int]
        List of sample rates corresponding to the impulse response arrays.
    stimuli : np.ndarray
        Stimuli array.
    fs_stimuli : int
        Sample rate of the stimuli array.
    variants : List[str]
        List of variant names.
    stim_str : str
        Stimulus name.
    peak_lvl : int, optional
        Peak level for normalization, in dBFS. Default is -12.
    prefix : str, optional
        Prefix for the output file names. Default is "13ab00ad".
    destination : str, optional
        Destination directory to save the output files. Default is current directory.
    """
    if not os.path.exists(destination):
        os.makedirs(destination)
    test_audio, fs = convolution(irs[0], fs_irs[0], stimuli, fs_stimuli,
            normalization=None
            )
    _test_audio, fs = peak_normalize(test_audio, fs, peak_lvl)

    factor = _test_audio.max()/test_audio.max()

    for ir, fs_ir, v in zip(irs, fs_irs, variants):
        test_audio, fs = convolution(ir, fs_ir, stimuli, fs_stimuli,
            normalization=None
            )
        test_audio *= factor
        sf.write(os.path.join(destination, f'{prefix}_{v}_{stim_str}.wav'), test_audio, fs)


def fs_to_pressure(
        audio: np.ndarray, 
        dbfs_db: float, 
        p0: float = 2e-5
        ) -> np.ndarray:
    """
    Convert audio signal from dBFS to pressure level.

    Parameters
    ----------
    audio : ndarray
        The audio signal in dBFS (decibels relative to full scale).
    dbfs_db : float
        The reference level in dBFS.
    p0 : float, optional
        The reference pressure level in pascals, by default 2e-5.

    Returns
    -------
    ndarray
        The audio signal converted to pressure level.

    """
    ratio_db = p0 * 10 ** (dbfs_db/20)
    audio_pressure = audio * ratio_db
    return audio_pressure

def eq_loudness_lvl(
        audio_pressure: np.ndarray, 
        fs: int, 
        field_type: str = "diffuse"
        ) -> Tuple[float, Tuple[np.ndarray, np.ndarray]]:
    """Calculate the log mean loudness level of an audio signal.

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
        The equal loudness level in dB.
    tuple
        A tuple containing the loudness values and corresponding time values.
    """
    audio_pressure = audio_pressure.mean(axis=1)
    audio_pressure = resample(audio_pressure, int(audio_pressure.shape[0]*48000/fs))
    fs=48000
    N, N_spec, _, time = mosqito.loudness_zwtv(
        audio_pressure.T, 
        fs, 
        field_type=field_type
    )
    loud_lvl = 40 + 10*np.log2(N.mean())
    return loud_lvl, (N, time)

def loudness_lvl_normalize(
        audio: np.ndarray, 
        fs: int, 
        target_phon: float, 
        dbfs_db: float, 
        return_ratio: bool = False
        ) -> Union[float, Tuple[np.ndarray, int]]:
    """
    Normalize the loudness level of an audio signal.

    Parameters
    ----------
    audio : ndarray
        The audio signal.
    fs : int
        The sampling frequency of the audio signal.
    target_phon : float 
        The target loudness level in phons.
    dbfs_db : float
        The reference level in dBFS.
    return_ratio : bool, optional
        If True, the normalization factor is returned, by default False.

    Returns
    -------
    float
        The normalization factor.
    ndarray
        The normalized audio signal.
    int
        The sampling frequency of the normalized audio signal.

    """
    audio_pressure = fs_to_pressure(audio, dbfs_db)
    loud_lvl, loudness = eq_loudness_lvl(audio_pressure, fs)
    loud_diff = target_phon - loud_lvl
    ratio = 1
    while abs(loud_diff) > 0.1:
        ratio *= 10 ** ((loud_diff)/20)
        audio_pressure_it = audio_pressure * ratio
        loud_lvl, loudness = eq_loudness_lvl(audio_pressure_it, fs)
        loud_diff = target_phon - loud_lvl
        logging.debug(loud_diff)
    audio *= ratio
    headroom = 1/abs(audio).max()
    headroom_db = 20*np.log10(headroom)
    if abs(audio).max() > 1:
        logging.warning("Audio signal clipped after normalization.")
        raise ValueError("Audio signal clipped after normalization. "+
                         f"The level overflows for {headroom_db:.2f} dB. "+
                         "Adjust headphone level.")
    else:
        logging.info(f"Audio signal normalized to {target_phon:.2f} phons.")
        logging.info(f"Normalization factor: {ratio:.2f}")
        logging.info(f"Headroom: {headroom_db:.2f} dB")
    
    if return_ratio:
        return ratio
    else:
        return audio, fs
    
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