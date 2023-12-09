"""
This module contains the `Adaptive` class, which represents a basic Adaptive test window for convolution-based processing. 
It provides functionality for playing audio files, recording responses, and moving to the next set of sentences.

Attributes
----------
parent : ctk.CTk
    The parent customtkinter widget.
sets : pd.DataFrame
    A DataFrame carrying the prepared randomized sets in the following format:
    | set_id | id | path | transcription |
    |--------|----|------|---------------|
    |set_id  |id  |path  |transcription  |
    This DataFrame can be obtained from the routines of the `listeningpy.set_preparation` module (adaptive_combination, randomization).
    This attribute also stores the responses, number of clicks per iteration, and time between the first and last clicked button.
irs : pd.DataFrame
    A DataFrame containing the item response theory parameters.
set_id : str, optional
    The ID of the set to be used. If None, all sets will be used.
initial_difficulty : int, optional
    The index of the initial difficulty level. Default is -1.
processing_func : Callable, optional
    The processing function to be used. Default is straight.
*args, **kwargs
    Additional arguments and keyword arguments associated with the processing function.
"""
import customtkinter as ctk
import time
import pandas as pd
import logging
import listeningpy.gui.gui as gui
from listeningpy.processing import straight, convolution
from soundfile import read
from typing import Callable
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")
# ctk.set_widget_scaling(2)

class Adaptive(ctk.CTkFrame):
    '''A basic Adaptive test window for convolution based processing.

    Attributes
    ----------
    parent
        parent customtkinter widget
    sets : pandas.DataFrame
        A dataframe carrying the prepaired randomized sets in a format
        | set_id |   id   |  path  | transcription |
        |--------|--------|--------|---------------|
        |set_id  |id      |path    |transcription  |
        This can be obtained from the routines of 
        listeningpy.set_preparation module (adaptive_combination, 
        randomization).
        This attribute also stores the responses, number of clicks per 
        iteration and time between the first and last clicked button. 
    '''
    def __init__(self, 
                master: ctk.CTk, 
                sets: pd.DataFrame,
                irs: pd.DataFrame,
                set_id: str = None,
                initial_difficulty: int = -1,
                processing_func : Callable = straight,
                *args, **kwargs
                ):
            """Initialize the AdaptiveGUI class.

            Parameters
            ----------
            master : ctk.CTk
                The master widget.
            sets : pd.DataFrame
                The DataFrame containing the sets.
            irs : pd.DataFrame
                The DataFrame containing the item response theory parameters.
            set_id : str, optional
                The ID of the set to be used. If None, all sets will be used.
            initial_difficulty : int, optional
                The index of the initial difficulty level. Default is -1.
            processing_func : Callable, optional
                The processing function to be used. Default is straight.
            *args, **kwargs
                Additional arguments and keyword arguments 
                associated with the processing function.
            """
            ctk.CTkFrame.__init__(self, master)
            self.sets = sets
            self.irs = irs
            self.set_id = set_id
            if self.set_id is not None:
                self.current_set = self.sets[self.sets['set'] == set_id]
            else:
                self.current_set = self.sets
            self.initial_difficulty = initial_difficulty
            self.difficulty = self.irs.index[initial_difficulty]
            self.last_idx = self.current_set.index[-1]
            self.processing_func = processing_func
            self.kwargs = kwargs

            self.choice = ctk.StringVar()
            self.progress = ctk.IntVar()
            self.progress.set(0)
            self.progress_label_var = ctk.StringVar()
            self.progress_label_var.set(f"{self.progress.get()+1}")
            self.current_sentence = ctk.StringVar()
            self.current_sentence.set(self.current_set["transcription"].iloc[self.progress.get()])

            self.label_set = ctk.CTkLabel(self, textvariable=self.progress_label_var)
            self.label_set.grid(row=0, column=2, columnspan=1, 
                padx=20, 
                pady=5, 
                sticky="E")

            self.label_question = ctk.CTkLabel(self, text="")
            self.label_question.grid(row=0, column=0, columnspan=2)
            
            self.sentence_frame = ctk.CTkFrame(self)
            self.sentence_frame.grid(row=1, column=0, columnspan=3,
                pady=10,)
            self.label_sentence = ctk.CTkLabel(self.sentence_frame, 
                textvariable=self.current_sentence,
                anchor='w',
                width=350,
                height=32)
            self.label_sentence.grid(row=1, column=0, columnspan=2,
                padx=20,
                pady=10,
                sticky='W'
                )

            self.button_play = gui.PlayButton(self.sentence_frame,
                text='Play',
                width=50,
                height=50,
                command=self.play
                # command=lambda:print(sets.loc[self.progress.get(), "path"])
            )
            self.button_play.grid(row=1, column=2, columnspan=1,
                padx=20,
                pady=10,
                sticky='E'
                )

            self.answer_frame = ctk.CTkFrame(self)
            self.answer_frame.grid(row=2, column=0, columnspan=3)
            self.segmented_button = ctk.CTkSegmentedButton(self.answer_frame,
                values=['Wrong', 'Correct'],
                width=400,
                height=50,
                dynamic_resizing=False,
                state=ctk.DISABLED,
                command=self.toggle_segmented,
                variable=self.choice)
            self.segmented_button.grid(row=4, column=0, columnspan=3, 
                padx=20,
                pady=10,
                )

            self.button_next = ctk.CTkButton(self,
                text="Next sentence",
                width=200,
                height=48,
                state=ctk.DISABLED,
                command=self.move_to_next)
            self.button_next.grid(row=3, column=0, columnspan=3, 
                padx=20,
                pady=10,
                )
    
    def play(self):
        """
        Plays the audio file with adaptive settings.

        This method reads the impulse response (IR) file based on the current difficulty level,
        and then plays the audio file with the specified processing function and additional arguments.

        Args:
            None

        Returns:
            None
        """
        ir, fs_ir = read(self.irs['path'].iloc[self.difficulty], always_2d=True)
        print(self.kwargs.keys())
        gui.play_click(
            self.current_set.loc[self.progress.get(), "path"],
            button=self.button_play,
            next_buttons=[self.segmented_button, self.button_next],
            processing_func=self.processing_func,
            in2 = ir,
            fs_in2 = fs_ir,
            **self.kwargs)

    def toggle_segmented(self, value):
            """Toggle the segmented button based on the given value.

            Parameters
            ----------
            value : str
                The value to determine the state of the segmented button.
                Possible values are 'Wrong' and 'Correct'.
            """
            if value == 'Wrong':
                self.segmented_button.configure(
                    selected_color=('#eb0000', '#8c0000'),
                    selected_hover_color=('#8c0000', '#710000')
                    )
            elif value == 'Correct':
                self.segmented_button.configure(
                    selected_color=('#00eb00', '#007000'),
                    selected_hover_color=('#007000', '#005000')
                    )
            
    def reset_buttons(self):
        """Reset the state of the buttons.

        This method disables the segmented_button and button_next buttons.

        """
        self.segmented_button.configure(state=ctk.DISABLED)
        self.button_next.configure(state=ctk.DISABLED)

    def move_to_next(self):
        '''Stores response to self.current_set dataframe and moves
        to the next set.
        '''
        row = self.progress.get()
        cols = ["answer", "ir_id"]
        self.current_set.loc[row, cols] = [self.choice.get(), self.irs["id"].iloc[self.difficulty]]
        
        if self.choice.get() == "Correct":
            self.current_set.loc[row, cols] = [1, self.irs["id"].iloc[self.difficulty]]
            self.difficulty = self.difficulty + 1
            self.progress.set(self.progress.get()+1)
        elif self.progress.get() != 0:
            self.current_set.loc[row, cols] = [0, self.irs["id"].iloc[self.difficulty]]
            self.difficulty = self.difficulty - 1
            self.progress.set(self.progress.get()+1)
        else:
            self.difficulty = self.difficulty - 1

        print(f"Difficulty: {self.difficulty}\nSentence: {self.progress.get()}")
        self.reset_buttons()
        if self.progress.get() > self.last_idx:
            self.master.responses = pd.concat(
                [self.master.responses, self.current_set]
            )
            self.master.switch_frame(self.master.intermediate_frame)
            return
        self.progress_label_var.set(f"{self.progress.get()+1}")
        self.current_sentence.set(self.current_set["transcription"].iloc[self.progress.get()])
        # logging.info(self.current_set)
    
    def load_sentences(self):
        """Load the sentences from the given path.
        """
        self.current_set = self.sets[self.sets['set'] == self.set_id].reset_index(drop=True)
        print("===Current set:===", self.current_set)
        self.progress.set(0)
        self.progress_label_var.set(f"{self.progress.get()+1}")
        self.difficulty = self.irs.index[self.initial_difficulty]
        self.current_sentence.set(self.current_set["transcription"].iloc[self.progress.get()])