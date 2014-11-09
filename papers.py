#!/usr/bin/env python3

""" Computer-based immigration office for Kanadia """

__author__ = 'Susan Sim, Sasa Milic'
__email__ = "ses@drsusansim.org, milic@cs.toronto.edu"

__copyright__ = "2014 Susan Sim"
__license__ = "MIT License"

__status__ = "Prototype"

# imports one per line
import re
import datetime
import json

######################
## global constants ##
######################
REQUIRED_FIELDS = ["passport", "first_name", "last_name",
                   "birth_date", "home", "entry_reason", "from"]

######################
## global variables ##
######################
'''
countries:
dictionary mapping country codes (lowercase strings) to dictionaries
containing the following keys:
"code","name","visitor_visa_required",
"transit_visa_required","medical_advisory"
'''
COUNTRIES = None
'''
WATCH_PASSPORTS, WATCH_NAMES:
sets containing, respectively, passports (lowercase strings) and
names (lowercase strings in the format "{first_name} {last_name}")
of people on the "watchlist"
'''
WATCH_PASSPORTS = None
WATCH_NAMES = None


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

    with open(input_file) as f:
        records = json.load(f)

    records = [convert_to_lower(r) for r in records]

    set_global_vars(watchlist_file, countries_file)

    decisions = {
        "Quarantine": is_quarantine,
        "Reject": is_reject,
        "Secondary": is_secondary,
    }

    results = []
    for r in records:

        # An exciting opportunity to use Python's for...else construct!
        for d in ["Quarantine", "Reject", "Secondary"]:

            if decisions[d](r):
                results.append(d)
                break
        else:
            # A traveller is accepted if they are not quarantined,
            # rejected, or require secondary processing
            results.append("Accept")

    return results


def convert_to_lower(d):
    """
    Convert all strings in dict d to upper case.

    :param d: a dictionary with string keys, where
     values are either strings or dicts
    :return:
    """

    new_d = {}
    for k, v in d.items():

        if type(v) is str:
            new_d[k.lower()] = v.lower()
        elif type(v) is dict:
            new_d[k.lower()] = convert_to_lower(v)

    return new_d


def set_global_vars(watchlist_file, countries_file):
    """
    Populate global variables COUNTRIES, WATCH_PASSPORTS, and WATCH_NAMES

    :param watchlist_file: JSON file
    :param countries_file: JSON file
    :return: None
    """

    global COUNTRIES, WATCH_PASSPORTS, WATCH_NAMES

    # read in all files into data structures
    with open(watchlist_file) as f:
        watchlist = json.load(f)
    with open(countries_file) as f:
        COUNTRIES = json.load(f)

    # convert country codes to lowercase
    COUNTRIES = convert_to_lower(COUNTRIES)
    watchlist = [convert_to_lower(w) for w in watchlist]

    # populate sets
    WATCH_PASSPORTS = set([x["passport"] for x in watchlist])
    WATCH_NAMES = set([" ".join([x["first_name"], x["last_name"]]) for x in watchlist])


def is_quarantine(record):
    """
    Return True iff a traveller that has the given record should be
    quarantined.

    :param record: A dict that corresponds to a traveller record.
    :return: Boolean; True if traveller should be quarantined,
        False otherwise.
    """

    # fields may not exist in record, thus
    # default values of from_ and via are empty strings 
    from_ = record.get("from", {}).get("country", "")
    via = record.get("via", {}).get("country", "")

    # If the traveler is coming from or via a country that has a
    # medical advisory, he or she must be sent to quarantine
    if any([COUNTRIES.get(c, {}).get("medical_advisory", "") for c in [from_, via]]):
        return True

    return False


def is_reject(record):
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

    # Reject traveller if they need a visa and it is not valid.
    return requires_visa(record) and not is_valid_visa(record)


def is_secondary(record):
    """
    Return True iff a traveller that has the given record should be
    sent to secondary processing.

    :param record: A dict that corresponds to a traveller record.
    :return: Boolean; True if traveller should be sent to secondary,
        False otherwise.
    """

    # Check if name or passport on the watchlist
    passport = record["passport"].lower()
    name = " ".join([record["first_name"], record["last_name"]]).lower()

    return (passport in WATCH_PASSPORTS) or (name in WATCH_NAMES)


def requires_visa(record):
    """
    Return whether a traveller requires a visa (transit or traveller)
    :param record: A dict that corresponds to a traveller record.
    :return: Boolean; True if the traveller requires a visa, False otherwise
    """

    home = record["home"]["country"]
    reason = record["entry_reason"]
    if home == "kan":
        return False

    visitor_visa_required = int(COUNTRIES[home]["visitor_visa_required"])
    transit_visa_required = int(COUNTRIES[home]["transit_visa_required"])

    if reason == "visit" and visitor_visa_required:
        return True
    if reason == "transit" and transit_visa_required:
        return True

    # traveller is returning
    return False


def is_valid_visa(record):
    """
    Checks whether a visa is valid (a valid visa is one that is less than two years)
    :param record: A dict that corresponds to a traveller record.
    :return: Boolean; True if the visa is valid, False otherwise
    """

    # Check whether the visa information is available,
    # and in the proper format
    visa = record.get("visa", {})
    visa_code = visa.get("code", "")
    visa_date = visa.get("date", "")

    if not (valid_visa_format(visa_code) and valid_date_format(visa_date)):
        return False

    # Check if visa is less than 2 years old
    now = datetime.datetime.now()
    two_years_ago = now.replace(year=now.year-2)
    visa_datetime = datetime.datetime.strptime(visa_date, '%Y-%m-%d')

    return (visa_datetime - two_years_ago).total_seconds() >= 0


def valid_visa_format(visa_code):
    """
    Checks whether a visa code is two groups of ﬁve alphanumeric characters separated by a dash
    :param visa_code: alpha-numeric string
    :return: Boolean; True if the format is valid, False otherwise
    """
    passport_format = re.compile('^\w{5}-\w{5}$')

    return passport_format.match(visa_code)


def valid_passport_format(passport_number):
    """
    Checks whether a pasport number is five sets of five alpha-number characters separated by dashes
    :param passport_number: alpha-numeric string
    :return: Boolean; True if the format is valid, False otherwise
    """
    passport_format = re.compile('^\w{5}-\w{5}-\w{5}-\w{5}-\w{5}$')

    return passport_format.match(passport_number)


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
