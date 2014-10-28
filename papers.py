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

# global constants
REQUIRED_FIELDS = ["passport", "first_name", "last_name",
                   "birth_date", "home", "entry_reason", "from"]

# global variables
records = None
countries = None
watch_passports = None
watch_names = None


def decide(input_file, watchlist_file, countries_file):
    """
    Decides whether a traveller's entry into Kanadia should be accepted

    :param input_file: The name of a JSON formatted file that contains
        cases to decide
    :param watchlist_file: The name of a JSON formatted file that
        contains names and passport numbers on a watchlist
    :param countries_file: The name of a JSON formatted file that contains
        country data, such as whether an entry or transit visa is required,
        and whether there is currently a medical advisory
    :return: List of strings. Possible values of strings are:
        "Accept", "Reject", "Secondary", and "Quarantine"
    """

    global records, countries, watch_passports, watch_names

    # read in all files into data structures
    files = [input_file, watchlist_file, countries_file]
    records, watchlist, countries = [json.load(open(f)) for f in files]

    watch_passports = set([x["passport"] for x in watchlist])
    watch_names = set([" ".join(x["first_name"], x["last_name"]) for x in watchlist])

    results = []

    decisions = {
        "Quarantine": is_quarantine,
        "Reject": is_rejection,
        "Secondary": is_secondary,
    }

    for r in records:
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

    # Quarantine if traveller was born in a country, or is travelling
    # from a country, having a medical advisory.
    if any([countries[c]["medical_advisory"] for c in [home, via]]):
        return True

    return False


def is_rejection(record):
    """
    Return True iff a traveller that has the given record should be
    rejected.

    :param record: A dict that corresponds to a traveller record.
    :return: Boolean; True if traveller should be rejected,
        False otherwise.
    """

    # Check if required information is complete.
    if not all([record.get(field, "") for field in REQUIRED_FIELDS]):
        return True

    # Check if they need a visa.
    if record["entry_reason"] not in ["visit", "transit"]:
        return False

    # Check whether the visa is valid.
    visa = record.get("visa")
    if visa:

        visa_code = visa.get("code", "")
        visa_date = visa.get("date", "")

        if valid_visa_format(visa_code) and \
           valid_date_format(visa_date) and \
           is_valid_visa(visa_date):

            return False

    return True


def is_secondary(record):
    """
    Return True iff a traveller that has the given record should be
    sent to secondary processing.

    :param record: A dict that corresponds to a traveller record.
    :return: Boolean; True if traveller should be sent to secondary,
        False otherwise.
    """

    # Check if name or passport on the watchlist
    passport = record["passport"]
    name = " ".join(record["first_name"], record["last_name"])

    return (passport in watch_passports) or (name in watch_names)


def is_valid_visa(visa_date):
    """
    Checks whether a visa is valid (a valid visa is one that is less than two years)
    :param visa_date: A string in the form 'XXXX-XX-XX'; the date the visa was issued
    :return: Boolean; True if the visa is valid, False otherwise
    """

    then = datetime.datetime.strptime(visa_date, '%Y-%m-%d')
    now = datetime.datetime.now()

    return (now - then).days < (365 * 2)


def valid_visa_format(visa_code):
    """
    Checks whether a visa code is two groups of ﬁve alphanumeric characters separated by a dash
    :param visa_code: alpha-numeric string
    :return: Boolean; True if the format is valid, False otherwise
    """
    passport_format = re.compile('.{5}-.{5}')

    if passport_format.match(visa_code):
        return True
    else:
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
