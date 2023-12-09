"""
This module contains the GUI classes for the listeningpy package.
"""
import customtkinter as ctk
import time
import logging
from typing import Callable
from numpy import ndarray
# logging.basicConfig(level=logging.INFO)
import configparser

import sys
from listeningpy.stimuli import play_sound
from listeningpy.processing import straight
from listeningpy.config import person_identifiers

class PlayButton(ctk.CTkButton):
    '''Customized customtkinter.CTkButton
    Attributes
    ----------
    parent
        parent customtkinter widget    

    Methods
    -------
    reset_count()
        Resets the click counter variable to 0.
    '''
    def __init__(self, parent, *args, **kwargs):
        ctk.CTkButton.__init__(self, parent, *args, **kwargs)
        self.click_count = 0
    
    def reset_count(self):
        self.click_count = 0

class InitFrame(ctk.CTkFrame):
    def __init__(self, master, test_frame, cfg_file=None, *args, **kwargs):
        ctk.CTkFrame.__init__(self, master, *args, **kwargs)
        self.test_frame = test_frame
        self.first_name = str
        self.second_name = str
        self.date_of_birth = str
        self.gender = str
        self.hear_impaired = bool
        self.first_name_label = ctk.CTkLabel(self, text='First name:')
        self.second_name_label = ctk.CTkLabel(self, text='Second name:')
        self.date_of_birth_label = ctk.CTkLabel(self, text='Date of birth:')
        self.gender_label = ctk.CTkLabel(self, text='Gender:')
        self.hear_impaired_label = ctk.CTkLabel(self, text='Hearing impaired:')



        self.first_name_entry = ctk.CTkEntry(self)
        self.second_name_entry = ctk.CTkEntry(self)
        
        self.date_of_birth_frame = ctk.CTkFrame(self)
        self.date_of_birth_day_entry = ctk.CTkEntry(
            self.date_of_birth_frame,
            width=35,
            placeholder_text='DD'
            )
        self.label_slash = ctk.CTkLabel(self.date_of_birth_frame, text='/')
        self.date_of_birth_month_entry = ctk.CTkEntry(
            self.date_of_birth_frame,
            width=35,
            placeholder_text='MM'
            )
        self.label_slash2 = ctk.CTkLabel(self.date_of_birth_frame, text='/')
        self.date_of_birth_year_entry = ctk.CTkEntry(
            self.date_of_birth_frame,
            width=50,
            placeholder_text='YYYY'
            )

        self.gender_menu = ctk.CTkComboBox(self, 
            values=['Man', 'Woman', 'Other']
            )
        
        self.hear_impaired_toggle = ctk.CTkSwitch(
            self,
            text='', 
            onvalue=True, 
            offvalue=False)

        if cfg_file is not None:
            self.set_identifiers(cfg_file)

        self.start_button = ctk.CTkButton(self, text='Start test', command=self.button_clicked)

        self.first_name_label.grid(column=0, row=1,
            padx=10,
            pady=5,
            sticky='e')
        self.second_name_label.grid(column=0, row=2,
            padx=10,
            pady=5,
            sticky='e')
        self.date_of_birth_label.grid(column=0, row=3,
            padx=10,
            pady=5,
            sticky='e')
        self.gender_label.grid(column=0, row=4,
            padx=10,
            pady=5,
            sticky='e')
        self.hear_impaired_label.grid(column=0, row=5,
            padx=10,
            pady=5,
            sticky='e')
        
        self.first_name_entry.grid(column=1, row=1,
            padx=10,
            pady=5)
        self.second_name_entry.grid(column=1, row=2,
            padx=10,
            pady=5)
        self.date_of_birth_frame.grid(column=1, row=3)
        self.date_of_birth_day_entry.grid(column=0, row=0,
            padx=1,
            pady=5)
        self.label_slash.grid(column=1, row=0,
            padx=1,
            pady=5)
        self.date_of_birth_month_entry.grid(column=2, row=0,
            padx=1,
            pady=5)
        self.label_slash2.grid(column=3, row=0,
            padx=2,
            pady=5)
        self.date_of_birth_year_entry.grid(column=4, row=0,
            padx=1,
            pady=5)

        self.gender_menu.grid(column=1, row=4,
            padx=10,
            pady=5)
        self.hear_impaired_toggle.grid(column=1, row=5,
            padx=10,
            pady=8, sticky='w')
        self.start_button.grid(column=1, row=6,
            padx=10,
            pady=5)
    
    def set_identifiers(self, cfg_file):
        identifiers = person_identifiers(cfg_file)
        keys = identifiers.keys()
        if 'first_name' in keys:
                self.first_name = identifiers['first_name']
                self.first_name_entry.insert(0, self.first_name)
        if 'second_name' in keys:
            self.second_name = identifiers['second_name']
            self.second_name_entry.insert(0, self.second_name)
        if 'date_of_birth' in keys:
            self.date_of_birth = identifiers['date_of_birth']
            self.date_of_birth_day_entry.insert(0, self.date_of_birth[:2])
            self.date_of_birth_month_entry.insert(0, self.date_of_birth[3:5])
            self.date_of_birth_year_entry.insert(0, self.date_of_birth[6:10])
        if 'gender' in keys:
            self.gender = identifiers['gender']
            self.gender_menu.set(self.gender)
        if 'hear_impaired' in keys:
            print(identifiers['hear_impaired'])
            self.hear_impaired = identifiers['hear_impaired'].lower() == "true"
            print(self.hear_impaired)
            if self.hear_impaired:
                self.hear_impaired_toggle.select()

    def button_clicked(self):
        self.first_name = self.first_name_entry.get()
        self.second_name = self.second_name_entry.get()
        self.date_of_birth = f'{self.date_of_birth_day_entry.get()}/{self.date_of_birth_month_entry.get()}/{self.date_of_birth_year_entry.get()}'
        self.gender = self.gender_menu.get()
        self.hear_impaired = self.hear_impaired_toggle.get()
        self.master.switch_frame(self.test_frame)

class InitFrameAdaptive(ctk.CTkFrame):
    """A class representing the initial frame for an adaptive test.

    This frame allows the user to input the participant identifier and the sentence set for the test.

    Parameters
    ----------
    master : cTK.Widget
        The master widget.
    test_frame : _type_
        The frame representing the test.

    Attributes
    ----------
    test_frame : _type_
        The frame representing the test.
    timestamp : str
        The current timestamp in the format "yy-mm-dd_HH-MM".
    participant : str
        The participant identifier.
    sentence_set : str
        The sentence set for the test.
    participant_label : ctk.CTkLabel
        The label for the participant identifier.
    sentence_set_label : ctk.CTkLabel
        The label for the sentence set.
    participant_entry : ctk.CTkEntry
        The entry field for the participant identifier.
    sentence_set_entry : ctk.CTkEntry
        The entry field for the sentence set.
    start_button : ctk.CTkButton
        The button to start the test.

    Methods
    -------
    button_clicked()
        Event handler for the button click event. Sets the participant identifier and sentence set,
        loads the sentences for the test, and switches to the test frame.
    """
    def __init__(self, master, test_frame, *args, **kwargs):
        ctk.CTkFrame.__init__(self, master, *args, **kwargs)
        self.test_frame : ctk.CTkFrame = test_frame
        self.timestamp = time.strftime("%y-%m-%d_%H-%M")
        self.participant = str
        self.sentence_set = str
        self.participant_label = ctk.CTkLabel(self, text='Participant identifier:')
        self.sentence_set_label = ctk.CTkLabel(self, text='Sentence set:')
        self.participant_entry = ctk.CTkEntry(self)
        self.sentence_set_entry = ctk.CTkEntry(self)
        self.start_button = ctk.CTkButton(
            self, 
            text='Start test', 
            command=self.button_clicked)
        
        self.participant_label.grid(column=0, row=1,
            padx=10,
            pady=5,
            sticky='e')
        self.sentence_set_label.grid(column=0, row=2,
            padx=10,
            pady=5,
            sticky='e')
        self.participant_entry.grid(column=1, row=1,
            padx=10,
            pady=5)
        self.sentence_set_entry.grid(column=1, row=2,
            padx=10,
            pady=5)
        self.start_button.grid(column=1, row=3,
            padx=10,
            pady=5)
        
    def button_clicked(self):
        """Handles the button click event.

        This method retrieves the participant and sentence set information from the GUI,
        sets the ID of the sentence set, loads the sentences, and switches to the test frame.

        """
        self.participant = self.participant_entry.get()
        self.sentence_set = self.sentence_set_entry.get()
        self.test_frame.set_id = self.sentence_set
        self.test_frame.load_sentences()
        self.master.switch_frame(self.test_frame)
        
class IntermediateFrameAdaptive(ctk.CTkFrame):
    """A custom frame for intermediate adaptive testing.

    This frame is used to display the intermediate adaptive testing interface.
    It contains widgets for entering the next sentence set, starting the test,
    and ending the test.

    Parameters
    ----------
    master : tk.Tk
        The master widget.
    test_frame : TestFrame
        The test frame to switch to after starting the test.
    *args : tuple
        Additional positional arguments.
    **kwargs : dict
        Additional keyword arguments.
    """
    def __init__(self, master, test_frame, *args, **kwargs):
        ctk.CTkFrame.__init__(self, master, *args, **kwargs)
        self.test_frame = test_frame
        self.sentence_set = str
        self.sentence_set_label = ctk.CTkLabel(self, text='Next sentence set:')
        self.sentence_set_entry = ctk.CTkEntry(self)
        self.start_button = ctk.CTkButton(
            self, 
            text='Start test', 
            command=self.button_clicked)
        self.end_button = ctk.CTkButton(
            self, 
            text='End test', 
            command=self.master.destroy)
        
        self.sentence_set_label.grid(column=0, row=2,
            padx=10,
            pady=5,
            sticky='e')
        self.sentence_set_entry.grid(column=1, row=2,
            padx=10,
            pady=5)
        self.start_button.grid(column=1, row=3,
            padx=10,
            pady=5)
        self.end_button.grid(column=1, row=4,
            padx=10,
            pady=5,
            )
        
    def button_clicked(self):
        """Callback function for the start button click event.

        This function is called when the start button is clicked. It retrieves
        the sentence set entered by the user, sets it in the test frame, loads
        the sentences for the test, and switches to the test frame.
        """
        self.sentence_set = self.sentence_set_entry.get()
        self.test_frame.set_id = self.sentence_set
        self.test_frame.load_sentences()
        self.master.switch_frame(self.test_frame)

def count_add(button: PlayButton):
    '''Adds 1 to click counter attribute of a PlayButton

    Parameters
    ----------
    button : PlayButton
    '''
    button.click_count += 1

def first_clicked(button: ctk.CTkButton):
    '''Checks whether the button is clicked for the first time. In case
    it is, the current time is stored for future duration evaluation.

    Parameters
    ----------
    button : ctk.CTkButton
    '''
    if not hasattr(button, 'time') or button.time == 0:
        button.time = time.time()
        logging.info("clicked!")

def stopwatch(
        button_start: PlayButton,
        button_end: ctk.CTkButton
        ) -> float:
    '''Calculates the time needed for the completion of current set.

    Parameters
    ----------
    button_start : PlayButton
        first button clicked
    button_end : ctk.CTkButton
        last button clicked ('Next')
    Returns
    -------
    t : float
        time between first and last click
    '''
    t = button_end.time-button_start.time
    button_start.time = 0
    button_end.time = 0
    return t

def play_click(
        stimuli_path: str,
        button: PlayButton,
        next_buttons: list[ctk.CTkButton, ctk.CTkRadioButton],
        processing_func: Callable[[ndarray, int], ndarray]=straight,
        **kwargs
        ) -> None:
    '''Defines actions for playback buttons.

    - adding 1 to button.click_count
    - playing stimuli
    - enables next button

    Parameters
    ----------
    stimuli_path : str
        path to stimuli
    button : PlayButton
        button just clicked (for counter)
    next_buttons : list[ctk.CTkButton, ctk.CTkRadioButton]
        list of buttons to be enabled after click
    '''
    count_add(button)
    first_clicked(button)
    logging.info(f"Playing {stimuli_path}")
    play_sound(path=stimuli_path, processing_func=processing_func, **kwargs)
    for n in next_buttons:
        n.configure(state=ctk.NORMAL)

def check_choice(
        last_played: PlayButton,
        button_end: ctk.CTkButton
        ):
    '''Enables the 'Next' button. Checks whether all stimuli were played and
    one chosen.

    Parameters
    ----------
    last_played : PlayButton
        last enabled PlayButton
    button_end : ctk.CTkButton
        'Next' button
    '''
    if last_played.cget("state") == ctk.NORMAL:
        button_end.configure(state=ctk.NORMAL)