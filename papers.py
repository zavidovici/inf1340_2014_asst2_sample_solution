#!/usr/bin/env python3

""" Computer-based immigration office for Kanadia """

__author__ = 'Susan Sim'
__email__ = "ses@drsusansim.org"

__copyright__ = "2014 Susan Sim"
__license__ = "MIT License"

__status__ = "Prototype"

# imports one per line
import re
import datetime
import json

# global variables
RECORDS = None
WATCHLIST = None
COUNTRIES = None


def decide(input_file, watchlist_file, countries_file):
    """
    Decides whether a traveller's entry into Kanadia should be accepted

    :param input_file: The name of a JSON formatted file that contains cases to decide
    :param watchlist_file: The name of a JSON formatted file that contains names and passport numbers on a watchlist
    :param countries_file: The name of a JSON formatted file that contains country data, such as whether
        an entry or transit visa is required, and whether there is currently a medical advisory
    :return: List of strings. Possible values of strings are: "Accept", "Reject", "Secondary", and "Quarantine"
    """

    global RECORDS, WATCHLIST, COUNTRIES

    # read in all files into data structures
    files = [input_file, watchlist_file, countries_file]
    RECORDS, WATCHLIST, COUNTRIES = [json.load(open(f)) for f in files]

    results = []

    decisions = {
        "Quarantine": is_quarantine,
        "Reject": is_rejection,
        "Secondary": is_secondary,
    }

    for r in RECORDS:
        '''
        Decide whether we need to "Accept", "Reject", "Secondary",
        or "Quarantine" person with record r

        Append string to results
        '''
    return results


def is_quarantine(record):
    """
    Return True iff a traveller that has the given record should be
    quarantined.

    :param record: A dict that corresponds to a traveller record.
    :return: Boolean; True if traveller should be quarantined,
        False otherwise.
    """

    home, via = record["home"]["country"], record["from"]["country"]
    
    # quarantine if traveller was born in a country, or is travelling
    # from a country, having a medical advisory
    if any(COUNTRIES[c]["medical_advisory"] for c in [home, via]):
        return True

    return False


def is_rejection(record):
    return False


def is_secondary(record):
    return False


def valid_passport_format(passport_number):
    """
    Checks whether a pasport number is five sets of five alpha-number characters separated by dashes
    :param passport_number: alpha-numeric string
    :return: Boolean; True if the format is valid, False otherwise
    """
    passport_format = re.compile('.{5}-.{5}-.{5}-.{5}-.{5}')

    if passport_format.match(passport_number):
        return True
    else:
        return False


def valid_date_format(date_string):
    """
    Checks whether a date has the format YYYY-mm-dd in numbers
    :param date_string: date to be checked
    :return: Boolean True if the format is valid, False otherwise
    """
    try:
        datetime.datetime.strptime(date_string, '%Y-%m-%d')
        return True
    except ValueError:
        return False
