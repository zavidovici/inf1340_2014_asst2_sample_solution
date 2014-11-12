#!/usr/bin/env python3

""" Module to test papers.py  """

__author__ = 'Susan Sim'
__email__ = "ses@drsusansim.org"

__copyright__ = "2014 Susan Sim"
__license__ = "MIT License"

__status__ = "Prototype"

# imports one per line
import pytest
import os
from papers import decide

DIR = "test_jsons/"
os.chdir(DIR)


def test_returning():
    """
    Travellers are returning to KAN.
    """
    assert decide("test_returning_citizen.json", "watchlist.json", "countries.json") ==\
        ["Accept", "Accept", "Quarantine"]


def test_watchlist1():
    """
    Travellers should have a secondary screening.
    """
    # If the traveller has a name or passport on the watch list,
    # she or he must be sent to secondary processing.
    assert decide("test_watchlist1.json", "watchlist.json", "countries.json") ==\
        ["Secondary", "Secondary"]


def test_watchlist2():
    """
    Only one of first or last name is on watchlist.
    """
    assert decide("test_watchlist2.json", "watchlist.json", "countries.json") ==\
        ["Accept", "Accept"]


def test_quarantine():
    assert decide("test_quarantine.json", "watchlist.json", "countries.json") ==\
        ["Quarantine", "Accept"]


def test_quarantine_via():
    """
    Test cases where traveller is coming via country with a medical advisory.
    """
    assert decide("test_quarantine_via.json", "watchlist.json", "countries.json") ==\
        ["Quarantine"]


def test_incomplete():
    """
    If the required information for an entry record is incomplete, the traveler must be rejected.
    """
    assert decide("test_incomplete.json", "watchlist.json", "countries.json") == \
        ["Reject", "Reject", "Reject"]


def test_invalid_visa():
    """
    Travellers with invalid visas.
    """
    assert decide("test_invalid_visa.json", "watchlist.json", "countries.json") == \
        ["Reject", "Reject", "Reject", "Reject", "Reject"]


def test_valid_visa():
    """
    Travellers with invalid visas.
    """
    assert decide("test_valid_visa.json", "watchlist.json", "countries.json") == \
        ["Accept"]


def test_valid_passport1():
    """
    Travellers with invalid passport formats.
    """
    assert decide("test_valid_passport1.json", "watchlist.json", "countries.json") == \
        ["Reject"]


def test_valid_passport2():
    """
    Traveller with passport older than 120 years.
    """
    assert decide("test_valid_passport2.json", "watchlist.json", "countries.json") == \
        ["Reject"]


def test_visa_not_needed():
    """
    Non-returning travellers not needing visas.
    """
    assert decide("test_visa_not_needed.json", "watchlist.json", "countries.json") == \
        ["Accept", "Accept"]


def test_case_insensitivity():
    """
    Country codes and passports with mixed cases.
    """
    assert decide("test_case_insensitivity.json", "watchlist.json", "countries.json") == \
        ["Accept", "Secondary"]


def test_conflicts1():
    """
    """
    assert decide("test_conflicts1.json", "watchlist.json", "countries.json") == \
        ["Quarantine", "Reject", "Secondary"]


def test_conflicts2():
    """
    """

    # Conflicts should be resolved according the order of priority:
    # quarantine, reject, secondary, and accept.

    assert decide("test_conflicts2.json", "watchlist.json", "countries.json") == \
        ["Reject"]


def test_error_file_not_found():
    with pytest.raises(FileNotFoundError):
        decide("test_returning_citizen.json", "", "countries.json")


def test_files_not_modified():
    """
    Test that input files are not modified.
    """
    files = ["example_entries.json", "watchlist.json", "countries.json"]

    before = [os.path.getmtime(f) for f in files]
    decide("example_entries.json", "watchlist.json", "countries.json")
    after = [os.path.getmtime(f) for f in files]

    assert before == after
