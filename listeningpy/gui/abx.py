"""
This module defines the `Abx` class, which represents a basic ABX test window with a counter.
"""

import customtkinter as ctk
import time
from pandas import DataFrame
import logging
import listeningpy.gui.gui as gui
from listeningpy.processing import straight
from typing import Callable

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

class Abx(ctk.CTkFrame):
    '''A basic ABX test window with a counter

    Attributes
    ----------
    parent
        parent customtkinter widget
    combinations : pandas.DataFrame
        A dataframe carrying the prepaired randomized combinations in a format

        |   0   |   1   |  Ref  |
        |-------|-------|-------|
        |path   |path   |path   |
        
        This can be obtained from the routines of 
        listeningpy.set_preparation module (abx_combination, 
        randomization).
        This attribute also stores the responses, number of clicks per 
        iteration and time between the first and last clicked button. 
    processing_func : func
        One of the listeningpy.processing functions, defaults to
        straight. The alternatives can be convolution, lf_convolution.
    args, kwargs
        The necessary kwargs depend on the processing function.
    '''
    def __init__(self,
                master : ctk.CTk,
                combinations: DataFrame,
                processing_func : Callable=straight,
                *args, **kwargs
                ):
        """Initialize the ABX GUI.

        Parameters
        ----------
        master : CTk
            The master widget.
        combinations : DataFrame
            The combinations of stimuli.
        processing_func : Callable, optional
            The processing function to apply, by default straight.
        *args, **kwargs : 
            Additional arguments and keyword arguments.
        """
        ctk.CTkFrame.__init__(self, master)
        self.combinations = combinations
        self.last_idx = combinations.index[-1]
        self.processing_func = processing_func
        self.kwargs = kwargs
        self.choice = ctk.StringVar()
        self.progress = ctk.IntVar()
        self.progress.set(0)
        self.progress_label_var = ctk.StringVar()
        self.progress_label_var.set(f"{self.progress.get()+1}/{self.last_idx+1}")

        self.question = ctk.CTkLabel(self, 
            text="Which stimulus is the same as reference?")
        self.question.grid(row=0, column=0, columnspan=3)

        self.label_set = ctk.CTkLabel(self, 
            textvariable=self.progress_label_var
            )
        self.label_set.grid(row=1, column=2, columnspan=1, 
            padx=20, 
            pady=10, 
            sticky="E"
            )

        self.button_a = gui.PlayButton(self, 
            text="A", 
            command=lambda:gui.play_click(
                combinations.loc[self.progress.get(), '0'],
                button=self.button_a,
                next_buttons=[self.button_b],
                processing_func=self.processing_func,
                **self.kwargs
                ), 
            state=ctk.NORMAL)
        self.button_a.grid(row=1, column=0, columnspan=1, 
            padx=20, pady=10)

        self.button_b = gui.PlayButton(self, text="B", 
            command=lambda: gui.play_click(
                combinations.loc[self.progress.get(), '1'],
                button=self.button_b,
                next_buttons=[self.button_ref],
                processing_func=self.processing_func,
                **self.kwargs
                ),
            state=ctk.DISABLED)
        self.button_b.grid(row=2, column=0, columnspan=1,
            padx=20,
            pady=10)

        self.choice_A = ctk.CTkRadioButton(self, 
            variable=self.choice, 
            value='0', 
            text="", 
            width=22, 
            state=ctk.DISABLED)
        self.choice_A.grid(row=1, column=1, columnspan=1,
            padx=20,
            pady=10
            )

        self.choice_B = ctk.CTkRadioButton(self, 
            variable=self.choice, 
            value='1', 
            text="", 
            width=22, 
            state=ctk.DISABLED)
        self.choice_B.grid(row=2, column=1, columnspan=1,
            padx=20,
            pady=10
            )

        self.button_ref = gui.PlayButton(self, 
            text="Reference", 
            width=202, 
            command=lambda:gui.play_click(
                combinations.loc[self.progress.get(), "Ref"],
                self.button_ref,
                [self.choice_A, self.choice_B],
                processing_func=self.processing_func,
                **self.kwargs
                ),
            state=ctk.DISABLED)
        self.button_ref.grid(row=3, column=0, columnspan=2, 
            padx=20, 
            pady=10, 
            sticky="W")

        self.button_next = ctk.CTkButton(self, 
            text="Next", 
            width=100, 
            command=self.move_to_next,
            state=ctk.DISABLED)
        self.button_next.grid(row=3, column=2, rowspan=2,
            padx=20,
            pady=10
            )

        self.choice_A.configure(
            command=lambda: gui.check_choice(self.button_b, self.button_next)
            )
        self.choice_B.configure(
            command=lambda: gui.check_choice(self.button_b, self.button_next)
            )
    
    def right_answer(self):
        '''Checks which answer is correct for each set.

        Returns
        -------
        column : str
            the right answer column name
        '''
        a = self.combinations.loc[self.progress.get(), '0']
        ref = self.combinations.loc[self.progress.get(), "Ref"]
        if a == ref:
            return '0' # this is in line with radio button values
        else:
            return '1'
        
    def store_response(self):
        '''Returns response, number of clicks and time
        needed for the set.

        Returns
        -------
        right_choice : int
            1 is for right, 0 for wrong choice
        clicks : int
            number of clicks (illustrates hesitation)
        time : float
            number of seconds needed for completion
        '''
        choice = self.choice.get()
        right = self.right_answer()
        if right == choice:
            right_choice = 1
        else:
            right_choice = 0
        buttons = [self.button_b, self.button_ref, self.button_a]
        radios = [self.choice_A, self.choice_B]
        clicks = 0
        for b in buttons:
            # print(b.click_count)
            clicks += b.click_count
            b.reset_count()
            b.configure(state=ctk.DISABLED)
        for r in radios:
            r.deselect()
            r.configure(state=ctk.DISABLED)
        self.progress.set(self.progress.get()+1)
        gui.first_clicked(self.button_next)
        t = gui.stopwatch(buttons[-1], self.button_next)
        buttons[-1].configure(state=ctk.NORMAL)
        self.button_next.configure(state=ctk.DISABLED)
        return right_choice, clicks, t
    
    def move_to_next(self):
        '''Stores response to self.combinations dataframe and moves
        to the next set.

        '''
        row = self.progress.get()
        cols = ["Right choice", "Clicks", "Time"]
        right_choice, clicks, t = self.store_response()
        self.combinations.loc[row, cols] = [right_choice, clicks, t]
        if self.progress.get() > self.last_idx:
            self.master.destroy()
        self.progress_label_var.set(f"{self.progress.get()+1}/{self.last_idx+1}")
        # logging.info(self.combinations.loc[row, :])
    