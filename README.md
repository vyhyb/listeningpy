# listeningpy

This library provides a way to design listening tests in Python.

The library contains several functions for audio processing, such as concolution or different types of normalization, including loudness normalization.

Only ABX test protocol is currently supported, but more protocols will be added in the future.

## Installation

It is currently not possible to install this library using `pip` or `conda`, please use the latest [released package](https://github.com/vyhyb/listeningpy/releases) instead and install using [`pip` locally](https://packaging.python.org/en/latest/tutorials/installing-packages/).

## Documentation

API documentation can be found [here](https://vyhyb.github.io/listeningpy/).

## Example usage

The following script implements a basic ABX listening test using the listeningpy library.

More examples are to be added in the future to the [examples](https://github.com/vyhyb/listeningpy/examples) folder.

```python
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
```

## Acknowledgments

This library was created thanks to the [FAST-J-23-8284](https://www.vut.cz/vav/projekty/detail/35091) project.

Special thanks to Prof. Monika Rychtáriková for her help with the theory and design of the listening tests and also to Yannick Sluyts and Dominika Hudokova for their valuable feedback.

Github Copilot was used to generate parts of the documentation and code.

## Author

- [David Jun](https://www.fce.vutbr.cz/o-fakulte/lide/david-jun-12801/)
  
  PhD student at [Brno University of Technology](https://www.vutbr.cz/en/)

## Contributing

Pull requests are welcome. For any changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

Copyright 2023 David Jun

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    [http://www.apache.org/licenses/LICENSE-2.0](http://www.apache.org/licenses/LICENSE-2.0)

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

