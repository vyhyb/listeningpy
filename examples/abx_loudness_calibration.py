import os
import logging
import soundfile as sf
import argparse, sys
from argparse import RawTextHelpFormatter
from _abx_test_straight_preparation import loudness_lvl_normalize, write_audio

desc_str = """
Program for loudness normalization used primarily for ABX listening tests.

The expected folder structure is:

source
│
├── subfolder1
│   ├── file1
│   ├── file2
│   ├── file3
│   └── ...
│
├── subfolder2
│   ├── file1
│   ├── file2
│   ├── file3
│   └── ...
│
└── ...

The program takes the first file in each subfolder and calculates its 
normalization factor for the aimed loudness level. This factor is then 
applied to all the files in that subfolder and exported to another folder 
(parent to source) called `calibrated`, which mimics the source folder 
structure.

calibrated
│
├── subfolder1
│   ├── file1
│   ├── file2
│   ├── file3
│   └── ...
│
├── subfolder2
│   ├── file1
│   ├── file2
│   ├── file3
│   └── ...
│
└── ...
"""

parser = argparse.ArgumentParser(description=desc_str, formatter_class=RawTextHelpFormatter)


parser.add_argument(
    "-dbfs", 
    "--dBFS-to-dB",
    type=float,
    help="dBFS to dB SPL headphones calibration."
    )
parser.add_argument(
    "-phon", 
    "--loudness-lvl",
    type=float,
    help="Target loudness level after calibration."
    )
parser.add_argument(
    "-loc", 
    "--location",
    type=str,
    help="Path to the folder with pre-baked sounds."
    )


args =  parser.parse_args()

print(args)

stim = os.listdir(args.location)  # list of subfolders
dbfs_db = args.dBFS_to_dB  # dBFS to dB SPL headphones calibration
target_phon = args.loudness_lvl  # target loudness level after calibration
source_dir = args.location  # path to the folder with pre-baked sounds
destination_dir = os.path.join(os.path.dirname(source_dir), "calibrated")  # path to the folder where the normalized sounds will be saved

for s in stim:
    # read whole folder with pre-baked sounds
    source = os.path.join(source_dir, s)
    destination = os.path.join(destination_dir, s)
    file_paths = os.listdir(source)

    # read single file used for normalization
    logging.info(f"==={file_paths[0]}===")
    stimulus, fs_stimulus = sf.read(os.path.join(source,file_paths[0]), always_2d=True)

    # loudness normalize
    ratio = loudness_lvl_normalize(
        stimulus, 
        fs_stimulus, 
        target_phon, 
        dbfs_db, 
        return_ratio=True
        )
    for f in file_paths:
        audio, fs = sf.read(os.path.join(source,f), always_2d=True)
        audio *= ratio
        write_audio(audio, fs, destination, f)

logging.info("Succesfully exported normalized files.")