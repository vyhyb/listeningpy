"""Module for playing back stimuli."""
from soundfile import SoundFile
from sounddevice import play
from numpy import ndarray
import logging
from typing import Callable
from listeningpy.processing import straight

# logging.basicConfig(level=logging.INFO)

def play_sound(
        path: str=None,
        sound: ndarray=None,
        processing_func: Callable[[ndarray, int], ndarray]=straight,
        fs: int=None,
        **kwargs
        ) -> None:
    '''Opens the file, performs requested processing and plays it back.

    This will be probably (not tested yet) useful for no or light-weight
    signal processing. Heavy-weight processing (convolution, etc.) should
    be probably prebaked when moving to another step inside
    a listening test.

    Parameters
    ----------
    path : str
        path to a Wave file
    processing_func : function
        processing to be performed in real time on a sound
    '''
    if path is not None:
        with SoundFile(path, 'r') as f:
            logging.info(f'File {path} was succesfully opened.')
            sound = f.read(always_2d=True)
            sound, fs = processing_func(sound, f.samplerate, **kwargs)
            play(sound, fs)
            logging.info(f'Stimuli of a of a shape {sound.shape} was played.')
    elif sound is not None and fs is not None:
        play(sound, fs)
        logging.info(f'Provided stimuli of a shape {sound.shape} was' +
            ' played without further processing.')
    else:
        logging.warning('You need to specify either path to soundfile' + 
            ' or sound and its sample rate.')
