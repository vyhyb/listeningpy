"""
This script provides functionality for measuring the root mean square (RMS) of audio files in a folder,
generating white noise with a desired RMS value, and playing the generated noise on the left or right channel
with a specified correction in decibels.

To use this script, run it as the main module. It will create a GUI window with options to load a folder,
calculate the RMS of the audio files in the folder, and play the generated noise on the left or right channel
with a specified correction in decibels.
"""
from customtkinter import CTk, CTkFrame, CTkButton, CTkLabel, CTkEntry, StringVar, CENTER
import numpy as np
from numpy import ndarray, empty, mean, concatenate, sqrt, zeros
from numpy.random import uniform
import sounddevice as sd
import soundfile as sf
import os
from dataclasses import dataclass
import logging

logging.basicConfig(level=logging.DEBUG)

@dataclass
class Noise:
    """
    Represents a noise object with mono, left, and right channels.
    """
    noise_mono: ndarray = None
    noise_L: ndarray = None
    noise_R: ndarray = None

def measure_rms_folder(parent):
    """Measure the root mean square (RMS) of audio files in a folder.

    Parameters
    ----------
    parent : str
        The path to the parent folder containing the audio files.

    Returns
    -------
    float
        The root mean square (RMS) value of the audio files.

    Raises
    ------
    IOError
        If there is an error reading the audio files.

    """
    paths = os.listdir(parent)
    print(paths[:5])
    audio = []
    for p in paths:
        try:
            f = sf.read(os.path.join(parent, p))[0]
            logging.debug(f"File with shape {f.shape} successfully read.")
            audio.append(f)
        except:
            IOError("Incorrect path.")
            logging.exception(f"Unable to read file {p}")
    long_array = empty(0)
    for a in audio:
        long_array = concatenate([long_array, a])
    rms = sqrt(mean(long_array**2))
    return rms

def prepare_noise(rms_material, length=5, fs=44100):
    """
    Generate white noise and normalize it based on the desired RMS value.

    Parameters
    ----------
    rms_material : float
        The desired RMS value of the material.
    length : int, optional
        The length of the generated white noise in seconds. Default is 5 seconds.
    fs : int, optional
        The sampling rate of the generated white noise. Default is 44100 Hz.

    Returns
    -------
    numpy.ndarray
        The generated white noise, normalized to the desired RMS value.
    """
    white_noise = uniform(-1, 1, length*fs)
    rms_noise = sqrt(mean(white_noise**2))
    print(rms_noise.shape)
    white_noise_audio_norm = white_noise * rms_material/rms_noise
    rms_white_noise_an = sqrt(mean(white_noise_audio_norm**2))
    logging.debug(f"audio (RMS): {rms_material:.3f}, noise (RMS): {rms_noise:.3f}, normalized noise (RMS): {rms_white_noise_an:.3f}")
    return white_noise_audio_norm

def button_load_clicked(str_var_parrent: StringVar, noise: Noise, button: CTkButton):
    """Load button click event handler.

    This function is called when the load button is clicked. It performs the following steps:
    1. Measures the RMS of the folder specified by the parent string variable.
    2. Prepares the mono noise using the measured RMS material.
    3. Initializes the stereo noise arrays with zeros.
    4. Assigns the mono noise to the left and right channels of the stereo noise arrays.
    5. Configures the button's foreground and hover colors to green.

    Parameters
    ----------
    str_var_parrent : StringVar
        The string variable containing the path of the parent folder.
    noise : Noise
        The Noise object used to store the noise data.
    button : CTkButton
        The button widget that triggered the event.
    """
    rms_material = measure_rms_folder(parent=str_var_parrent.get())
    noise.noise_mono = prepare_noise(rms_material=rms_material)
    zeros_stereo = zeros((2, noise.noise_mono.shape[0]))
    noise.noise_L = zeros_stereo.copy()
    noise.noise_L[0] = noise.noise_mono
    noise.noise_L = noise.noise_L.T
    noise.noise_R = zeros_stereo.copy()
    noise.noise_R[1] = noise.noise_mono
    noise.noise_R = noise.noise_R.T
    button.configure(fg_color="green", hover_color="green")

def button_play_noise(noise: Noise, ch: str, corr_db: float, fs=44100):
    """Play the specified noise on the specified channel with a specified correction in decibels.

    Parameters
    ----------
    noise : Noise
        The noise object containing the left and right channel noise signals.
    ch : str
        The channel to play the noise on. Valid values are 'L' for left channel and 'R' for right channel.
    corr_db : float
        The correction in decibels to apply to the noise signal.
    fs : int, optional
        The sample rate of the noise signal, in Hz. Default is 44100 Hz.
    """
    frac = 10**(corr_db/20)
    if ch.lower() == "l":
        sd.play(noise.noise_L*frac, samplerate=fs)
    elif ch.lower() == "r":
        sd.play(noise.noise_R*frac, samplerate=fs)

if __name__ == '__main__':
    root = CTk()
    root.geometry("800x400")
    # root.iconbitmap(bitmap='icon.ico')
    root.title('Noise based calibration v0.1')

    # variables
    path = StringVar()
    correction_str = StringVar()
    correction_str.set(str(0))
    noise = Noise()
    

    # main frame and widgets
    main_frame = CTkFrame(root)

    path_label = CTkLabel(main_frame, text="Folder containing test audio (for RMS calculation):")
    path_entry = CTkEntry(main_frame, width=400, textvariable=path)
    path_load_button = CTkButton(main_frame, text="Load", command=lambda:button_load_clicked(path, noise, path_load_button))

    correction_label = CTkLabel(main_frame, text="Level correction (dB):")
    correction_entry = CTkEntry(main_frame, textvariable=correction_str)

    play_button_l = CTkButton(main_frame, text="Play (L)", command=lambda:button_play_noise(noise, ch="L", corr_db=float(correction_str.get())))
    play_button_r = CTkButton(main_frame, text="Play (R)", command=lambda:button_play_noise(noise, ch="R", corr_db=float(correction_str.get())))

    path_label.grid(row=0, column=0, columnspan=2)
    path_entry.grid(row=1, column=0, columnspan=2)
    path_load_button.grid(row=2, column=0, columnspan=2)

    correction_label.grid(row=3, column=0, columnspan=1)
    correction_entry.grid(row=3, column=1, columnspan=1, pady=20)

    play_button_l.grid(row=4, column=0, columnspan=1)
    play_button_r.grid(row=4, column=1, columnspan=1)

    main_frame.place(relx=0.5, rely=0.5, anchor=CENTER)
    root.mainloop()