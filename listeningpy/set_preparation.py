"""
Functions for preparing sets for listening tests.
"""

from pandas import DataFrame, concat
import logging
from itertools import combinations
import os
# logging.basicConfig(level=logging.INFO)

### GENERAL ###

def filter_wavs(paths: list[str]) -> list[str]:
    '''Filters files with '.wav' extension from a list of paths.

    Parameters
    ----------
    paths : list[str]
        list of file paths

    Returns
    -------
    paths : list[str]
        list of filtered file paths
    '''
    paths = filter(lambda file: file.lower().endswith('.wav'), paths)
    return list(paths)

def read_folder(
        folder,
        parent=None,
        filterwav=True
        ) -> list[str]:
    '''Reads files inside a specified folder and keeps '.wav' files
    inside it. 

    Parameters
    ----------
    folder : str
        folder containing wav files
    parent : str
        path to project folder
    filterwav : bool
        True value filters out other than '.wav' files

    Returns
    -------
    audio_paths : list[str]
        list containing paths to audio files inside a specified folder
    '''
    if parent == None:
        audio_folder = folder
    else:
        audio_folder = os.path.join(parent, folder)
    audio_paths = os.scandir(audio_folder)
    audio_paths = [
        os.path.join(audio_folder, p.name) for p in audio_paths if p.is_file()
        ]
    if filterwav:
        audio_paths = filter_wavs(audio_paths)
    logging.info(f"Read these files: {audio_paths}")
    return audio_paths

def sub_folders(
        folder : str,
        ) -> list[str]:
    """Return a list of sub-folders within the specified folder.

    Parameters
    ----------
    folder : str
        The name of the folder.
    parent : str
        The parent directory of the folder.

    Returns
    -------
    list[str]
        A list of sub-folders within the specified folder.
    """
    parent = os.path.split(folder)[0]
    main_folder = os.path.join(parent, folder)
    subs = os.scandir(main_folder)
    subs = [
        os.path.join(parent, folder, p.name)
        for p in subs if p.is_dir()
        ]
    return subs

def randomization(df: DataFrame) -> DataFrame:
    '''
    Shuffles rows in a provided DataFrame. In this context, it randomizes
    sets for discrimination listening tests.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing sets for the listening test, one per row.

    Returns
    -------
    df : pandas.DataFrame
        DataFrame with randomly shuffled rows.
    '''
    return df.sample(frac=1).reset_index(drop=True)

### COMBINATIONS PREPARATION ###

def abx_combination(
        folder: str,
        parent: str=".",
        constant_reference: bool=False
        ) -> DataFrame:
    '''Reads files in a specified folder and generates combinations for
    ABX test.

    Parameters
    ----------
    folder : str
        Folder containing wav files.
    parent : str, optional
        Path to the project folder. Default is the current directory.
    constant_reference : bool, optional
        Determines whether to generate combinations for standard ABX (False) or CR-ABX (True).
        For CR-ABX, the combinations will have half the length of ABX. Default is False.

    Returns
    -------
    audio_path_comb : pandas.DataFrame
        Sorted sets for ABX test.

    Notes
    -----
    - The function reads the files in the specified folder and generates combinations of pairs.
    - Each combination is represented as a row in the returned DataFrame.
    - The DataFrame contains columns for the two audio paths in each combination, as well as an ID column.
    - If constant_reference is True, the reference audio path will be the same for all combinations.
      Otherwise, the reference audio path will vary for each combination.
    - The DataFrame is sorted by the first audio path in each combination.

    Examples
    --------
    >>> abx_combination("audio_folder", parent="project_folder", constant_reference=True)
    Returns combinations for CR-ABX with a constant reference audio path.

    >>> abx_combination("audio_folder")
    Returns combinations for standard ABX.

    '''
    audio_path_list = read_folder(folder, parent)
    audio_path_comb = DataFrame(combinations(audio_path_list, 2), columns=['0', '1'])
    audio_path_comb['ID'] = audio_path_comb.index.format(name=False, formatter="{0:0=2d}".format)
    if constant_reference:
        audio_path_comb["Ref"] = audio_path_comb.loc[:, '0']
    else:
        audio_path_comb_copy = audio_path_comb.copy()
        audio_path_comb["Ref"] = audio_path_comb.loc[:, '0']
        audio_path_comb_copy["Ref"] = audio_path_comb_copy.loc[:, '1']
        audio_path_comb = concat([audio_path_comb, audio_path_comb_copy])
        
    audio_path_comb_inv = audio_path_comb.copy()
    audio_path_comb_inv.loc[:, ['1', '0']] = audio_path_comb_inv.loc[:, ['0', '1']].values
    audio_path_comb = concat([audio_path_comb, audio_path_comb_inv]).reset_index(drop=True)
    audio_path_comb = audio_path_comb.sort_values(by=['0'])
    logging.info("ABX combinations returned.")
    return audio_path_comb

def abx_combination_subset(
        folder: str,
        parent: str=".",
        constant_reference: bool=False
        ) -> DataFrame:
    '''Reads files in a specified folder and generates combinations for
    ABX test. Creates a subset of combinations containing the first path
    read.

    Parameters
    ----------
    folder : str
        Folder containing wav files.
    parent : str, optional
        Path to the project folder. Default is the current directory.
    constant_reference : bool, optional
        Determines whether to return combinations for standard ABX (False)
        or CR-ABX (True) with half the length of ABX. Default is False.

    Returns
    -------
    audio_path_comb : pandas.DataFrame
        Sorted sets for ABX test.

    Notes
    -----
    This function reads the files in the specified folder and generates
    combinations for an ABX test. It creates a subset of combinations
    that contain the first path read. The resulting combinations are
    returned as a pandas DataFrame.

    If `constant_reference` is True, the function generates combinations
    for CR-ABX, where the reference path remains constant. If False, it
    generates combinations for standard ABX, where the reference path
    changes for each combination.

    Examples
    --------
    >>> abx_combination_subset("audio_folder", parent="project_folder", constant_reference=True)
    Returns combinations for CR-ABX with the first path as the reference.

    >>> abx_combination_subset("audio_folder", constant_reference=False)
    Returns combinations for standard ABX with the first path as the reference.
    '''
    audio_path_list = read_folder(folder, parent)
    audio_path_comb = DataFrame(combinations(audio_path_list, 2), columns=['0', '1'])
    audio_path_comb = audio_path_comb[audio_path_comb.loc[:,'0'] == audio_path_list[0]]
    audio_path_comb['ID'] = audio_path_comb.index.format(name=False, formatter="{0:0=2d}".format)
    if constant_reference:
        audio_path_comb["Ref"] = audio_path_comb.loc[:, '0']
    else:
        audio_path_comb_copy = audio_path_comb.copy()
        audio_path_comb["Ref"] = audio_path_comb.loc[:, '0']
        audio_path_comb_copy["Ref"] = audio_path_comb_copy.loc[:, '1']
        audio_path_comb = concat([audio_path_comb, audio_path_comb_copy])
        
    audio_path_comb_inv = audio_path_comb.copy()
    audio_path_comb_inv.loc[:, ['0', '1']] = audio_path_comb_inv.loc[:, ['0', '1']].values
    audio_path_comb = concat([audio_path_comb, audio_path_comb_inv]).reset_index(drop=True)
    audio_path_comb = audio_path_comb.sort_values(by=['0'])
    logging.info("ABX combinations returned.")
    return audio_path_comb

def adaptive_combination(folder: str, parent: str):
    '''Reads files in a specified folder and generates combinations for
    adaptive method test.

    Parameters
    ----------
    folder : str
        Folder containing set subfolders.
    parent : str
        Path to project folder.

    Returns
    -------
    audio_path_df : pandas.DataFrame
        Sorted sets for adaptive method test.
    '''
    audio_path_df = DataFrame()
    sets = sub_folders(folder, parent)
    for s in sets:
        paths = read_folder(s)
        ids = [os.path.split(p)[1][:-4] for p in paths]
        set_list = [os.path.split(s)[1] for p in paths]
        dict_ = {'set': set_list, 'id': ids, 'path':paths}
        df = DataFrame(dict_)
        audio_path_df = concat([audio_path_df, df])
    return audio_path_df

def adaptive_irs(folder: str):
    '''Reads files in a specified folder and generates DataFrame

    Parameters
    ----------
    folder : str
        folder containing set subfolders

    Returns
    -------
    audio_path_df : pandas.DataFrame
        sorted irs for adaptive method test
    '''
    paths = read_folder(folder)
    paths.sort()
    ids = [os.path.split(p)[1][:-4] for p in paths]
    dict_ = {'id': ids, 'path':paths}
    audio_path_df = DataFrame(dict_)
    
    return audio_path_df


