"""
This module contains functions for reading and parsing configuration files.
"""
import configparser
import logging
from typing import Dict



def person_identifiers(path: str) -> Dict[str, str]:
    """
    Read a configuration file and extract person identifiers.

    Parameters
    ----------
    path : str
        The path to the configuration file.

    Returns
    -------
    dict
        A dictionary containing person identifiers.

    Raises
    ------
    IOError
        If something goes wrong while reading the config file.
    """
    person_dict = {}
    try:
        cfg = configparser.ConfigParser()
        cfg.read(path)
        logging.info('Config file read.')
        keys = cfg['Identifiers'].keys()
        if 'FirstName' in keys:
            person_dict['first_name'] = cfg.get('Identifiers', 'FirstName')
        if 'SecondName' in keys:
            person_dict['second_name'] = cfg.get('Identifiers', 'SecondName')
        if 'DateOfBirth' in keys:
            person_dict['date_of_birth'] = cfg.get('Identifiers', 'DateOfBirth')
        if 'Gender' in keys:
            person_dict['date_of_birth_day'] = cfg.get('Identifiers', 'Gender')
        if 'HearingImpaired' in keys:
            person_dict['hear_impaired'] = cfg.get('Identifiers', 'HearingImpaired')
    except:
        IOError('Something went wrong while reading config file.')
    return person_dict



def test_settings(path: str) -> Dict[str, str]:
    """
    Read and parse the configuration file at the given path.

    Parameters
    ----------
    path : str
        The path to the configuration file.

    Returns
    -------
    Dict[str, str]
        A dictionary containing the settings parsed from the configuration file.

    Raises
    ------
    IOError
        If something goes wrong while reading the configuration file.

    """
    settings = {}
    try:
        cfg = configparser.ConfigParser()
        cfg.optionxform = str
        cfg.read(path)
        logging.info('Config file read.')
        settings = dict(cfg.items('Settings'))
    except:
        raise IOError('Something went wrong while reading config file.')
    print(settings)
    return settings

if __name__ == '__main__':
    test_settings('config.ini')




