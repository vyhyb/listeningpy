"""
This script implements a basic ABX listening test using the listeningpy library.

The ABX listening test is a method used in audio evaluation to compare the perceived quality
or difference between two audio samples. In this test, the listener is presented with three
audio stimuli: A, B, and X. The listener's task is to determine which of the two stimuli is the same as X.

This script uses the listeningpy library to perform the ABX test. It imports the necessary modules
and defines the ABXTest class, which extends the customtkinter.CTk class. The ABXTest class provides
a graphical user interface for the test.

The script starts by parsing command-line arguments to specify the directory path for the audio sounds.
It then generates combinations of audio stimuli using the abx_combination function from the
listeningpy.set_preparation module. The combinations are randomized using the randomization function.

The root window is created using the ABXTest class, and the title is set to 'ABX test v0.0.1'. The ABX
class from the abx module is instantiated with the root window, the generated combinations, and the
processing function straight. The InitFrame class from the gui module is also instantiated with the
root window and the ABX instance.

The mainloop is called to start the GUI event loop. After the test is completed, the user's information
and the test results are saved to CSV files using the pandas library.

Example usage:
- Run the script with the desired command-line arguments to specify the directory path for the audio sounds:
    python _basic_abx_test.py -sounds /path/to/sounds

- Follow the instructions on the GUI to perform the ABX listening test.
- The user's information and test results will be saved to CSV files.

Note: Make sure to have the listeningpy library and its dependencies installed before running this script.
"""
import customtkinter as ctk
import logging
import argparse

from pandas import DataFrame
from time import strftime
from listeningpy.gui import abx
from listeningpy.gui.gui import InitFrame
from listeningpy.set_preparation import abx_combination, randomization
from listeningpy.processing import straight

logging.basicConfig(datefmt='%H:%M:%S',
                    level=logging.INFO)

class ABXTest(ctk.CTk):
    """Main class for the ABX test GUI."""
    def __init__(self, **kwargs):
        ctk.CTk.__init__(self, **kwargs)
        self._frame = None

    def switch_frame(self, new_frame):
        """Destroys current frame and replaces it with a new one."""
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        self._frame.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-sounds', default='stimuli', help='Directory path for sounds')
    args = parser.parse_args()

    sounds_dir = args.sounds

    # Read files in the specified folder and generate combinations for ABX test
    df = abx_combination(sounds_dir, '.', constant_reference=False)
    df = randomization(df)

    # Create root window and GUI
    root = ABXTest()
    root.title('ABX test v0.0.1')
    test = abx.Abx(root,
        df, 
        processing_func=straight,
        )
    init = InitFrame(root, test)
    root._frame = init
    init.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)

    root.mainloop()
    
    init_dict = {
        'first_name': init.first_name,
        'second_name': init.second_name,
        'date_birth': init.date_of_birth,
        'gender': init.gender,
        'hearing_impaired': init.hear_impaired
    }
    timestamp = strftime("%y-%m-%d_%H-%M")
    
    # Save user's information and test results to CSV files
    DataFrame(init_dict, index=[0]).to_csv(
        f'{timestamp}_{init.first_name}_'+
        f'{init.second_name}_info.csv'
    )
    test.combinations.to_csv(
        f'{timestamp}_{init.first_name}_'+
        f'{init.second_name}_results.csv'
    )