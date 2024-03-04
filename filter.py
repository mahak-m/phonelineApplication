"""
CSC148, Winter 2024
Assignment 1

This code is provided solely for the personal and private use of
students taking the CSC148 course at the University of Toronto.
Copying for purposes other than this use is expressly prohibited.
All forms of distribution of this code, whether as given or with
any changes, are expressly prohibited.

All of the files in this directory and all subdirectories are:
Copyright (c) 2022 Bogdan Simion, Diane Horton, Jacqueline Smith
"""
import time
import datetime
from typing import Any, Optional
from call import Call
from customer import Customer


class Filter:
    """ A class for filtering customer data on some criterion. A filter is
    applied to a set of calls.

    This is an abstract class. Only subclasses should be instantiated.
    """

    def __init__(self) -> None:
        pass

    def apply(self, customers: list[Customer],
              data: list[Call],
              filter_string: str) \
            -> list[Call]:
        """ Return a list of all calls from <data>, which match the filter
        specified in <filter_string>.

        The <filter_string> is provided by the user through the visual prompt,
        after selecting this filter.
        The <customers> is a list of all customers from the input dataset.

         If the filter has
        no effect or the <filter_string> is invalid then return the same calls
        from the <data> input.

        Note that the order of the output matters, and the output of a filter
        should have calls ordered in the same manner as they were given, except
        for calls which have been removed.

        Precondition:
        - <customers> contains the list of all customers from the input dataset
        - all calls included in <data> are valid calls from the input dataset
        """
        raise NotImplementedError

    def __str__(self) -> str:
        """ Return a description of this filter to be displayed in the UI menu
        """
        raise NotImplementedError


class ResetFilter(Filter):
    """
    A class for resetting all previously applied filters, if any.
    """

    def apply(self, customers: list[Customer],
              data: list[Call],
              filter_string: str) \
            -> list[Call]:
        """ Reset all of the applied filters. Return a List containing all the
        calls corresponding to <customers>.
        The <data> and <filter_string> arguments for this type of filter are
        ignored.

        Precondition:
        - <customers> contains the list of all customers from the input dataset
        """
        filtered_calls = []
        for c in customers:
            customer_history = c.get_history()
            # only take outgoing calls, we don't want to include calls twice
            filtered_calls.extend(customer_history[0])
        return filtered_calls

    def __str__(self) -> str:
        """ Return a description of this filter to be displayed in the UI menu
        """
        return "Reset all of the filters applied so far, if any"


def helper_one(new_call: Any, phone_number_: Any, result_calls: list) -> None:
    """
    This is a helper function that helps apply the Customer Filter
    ("c") by adding customer calls to an existing list.
    """
    if new_call.src_number == phone_number_:
        result_calls.append(new_call)


def _add_call_if_matched(call: Call, phone_number: str,
                         return_list: list[Call]) -> None:
    """helper function to add a call to the return list if it matches the
    phone number. """
    # if call.src_number == phone_number or call.dst_number == phone_number:
    if phone_number in {call.src_number, call.dst_number}:
        if call not in return_list:
            return_list.append(call)


def _filter_calls_by_customer(customers: list[Customer],
                              data: list[Call],
                              filter_string: str) -> list[Call]:
    """helper function to filter calls based on customer ID."""
    return_list = []
    for customer in customers:
        if str(customer.get_id()) == filter_string:
            phone_numbers = customer.get_phone_numbers()
            for phone_number in phone_numbers:
                for call in data:
                    _add_call_if_matched(call, phone_number, return_list)
    return return_list


class CustomerFilter(Filter):
    """
    A class for selecting only the calls from a given customer.
    """

    def apply(self, customers: list[Customer],
              data: list[Call],
              filter_string: str) \
            -> list[Call]:
        """ Return a list of all unique calls from <data> made or
        received by the customer with the id specified in <filter_string>.

        The <customers> list contains all customers from the input dataset.

        The filter string is valid if and only if it contains a valid
        customer ID.
        - If the filter string is invalid, return the original list <data>
        - If the filter string is invalid, your code must not crash, as
        specified in the handout.

        Do not mutate any of the function arguments!
        """
        try:
            return_list = _filter_calls_by_customer(customers, data,
                                                    filter_string)
            if return_list:
                return return_list
            else:
                return data
        except (IndexError, TypeError, ValueError):
            return data

    def __str__(self) -> str:
        """ Return a description of this filter to be displayed in the UI menu
        """
        return "Filter events based on customer ID"


class DurationFilter(Filter):
    """
    A class for selecting only the calls lasting either over or under a
    specified duration.
    """

    def apply(self, customers: list[Customer],
              data: list[Call],
              filter_string: str) \
            -> list[Call]:
        """ Return a list of all unique calls from <data> with a duration
        of under or over the time indicated in the <filter_string>.

        The <customers> list contains all customers from the input dataset.

        The filter string is valid if and only if it contains the following
        input format: either "Lxxx" or "Gxxx", indicating to filter calls less
        than xxx or greater than xxx seconds, respectively.
        - If the filter string is invalid, return the original list <data>
        - If the filter string is invalid, your code must not crash, as
        specified in the handout.

        Do not mutate any of the function arguments!
        """
        if len(filter_string.strip()) == 0:
            return data

        return_list = []
        try:
            for i in data:
                if filter_string[0] == 'L':
                    curr_text = int(filter_string[1:4])
                    if i.duration < curr_text:
                        return_list.append(i)
                elif filter_string[0] == 'G':
                    curr_text = int(filter_string[1:4])
                    if i.duration > curr_text:
                        return_list.append(i)
                else:
                    return data
            # do error checking
        except IndexError:
            return data
        except TypeError:
            return data
        except ValueError:
            return data
        else:  # if there are no errors as of this point
            return return_list

    def __str__(self) -> str:
        """ Return a description of this filter to be displayed in the UI menu
        """
        return "Filter calls based on duration; " \
               "L### returns calls less than specified length, G### for greater"


def _parse_coordinates(filter_string: str) -> tuple:
    """Helper function to parse filter_string into coordinates."""
    cut = filter_string.split(', ')
    return float(cut[0]), float(cut[1]), float(cut[2]), float(cut[3])


def _is_valid_boundary(north: float, south: float, west: float,
                       east: float) -> bool:
    """
    This helper function checks to see if the corrdinates
    actually do form a valid boundary
    """
    return (-79.697878 <= north < south <= -79.196382) and \
           (43.576959 <= west < east <= 43.799568)


def _is_call_within_boundary(call: Call, north: float, south: float,
                             west: float, east: float) -> bool:
    """
    This helper function checks to see if a call is within the
    boundary.
    """
    src_long, src_lat = call.src_loc
    dst_long, dst_lat = call.dst_loc
    return (north <= src_long <= south and west <= src_lat <= east) or \
           (north <= dst_long <= south and west <= dst_lat <= east)


def _filter_calls_by_location(data: list[Call], north: float, south: float,
                              west: float, east: float) -> list[Call]:
    """
    This helper function filters calls based on the coordinates
    and arguments provided
    """
    return_list = []
    for call in data:
        if _is_call_within_boundary(call, north, south, west, east):
            return_list.append(call)
    return return_list


class LocationFilter(Filter):
    """
    A class for selecting only the calls that took place within a specific area
    """

    def apply(self, customers: list[Customer],
              data: list[Call],
              filter_string: str) \
            -> list[Call]:
        """ Return a list of all unique calls from <data>, which took
        place within a location specified by the <filter_string>
        (at least the source or the destination of the event was
        in the range of coordinates from the <filter_string>).

        The <customers> list contains all customers from the input dataset.

        The filter string is valid if and only if it contains four valid
        coordinates within the map boundaries.
        These coordinates represent the location of the lower left corner
        and the upper right corner of the search location rectangle,
        as 2 pairs of longitude/latitude coordinates, each separated by
        a comma and a space:
          lowerLong, lowerLat, upperLong, upperLat
        Calls that fall exactly on the boundary of this rectangle are
        considered a match as well.
        - If the filter string is invalid, return the original list <data>
        - If the filter string is invalid, your code must not crash, as
        specified in the handout.

        Do not mutate any of the function arguments!
        """
        try:
            north, west, south, east = _parse_coordinates(filter_string)
        except (IndexError, TypeError, ValueError):
            return data

        if _is_valid_boundary(north, south, west, east):
            return _filter_calls_by_location(data, north, south, west, east)
        else:
            return data

    def __str__(self) -> str:
        """ Return a description of this filter to be displayed in the UI menu
        """
        return "Filter calls made or received in a given rectangular area. " \
               "Format: \"lowerLong, lowerLat, " \
               "upperLong, upperLat\" (e.g., -79.6, 43.6, -79.3, 43.7)"


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(config={
        'allowed-import-modules': [
            'python_ta', 'typing', 'time', 'datetime', 'call', 'customer'
        ],
        'max-nested-blocks': 4,
        'allowed-io': ['apply', '__str__'],
        'disable': ['W0611', 'W0703'],
        'generated-members': 'pygame.*'
    })
