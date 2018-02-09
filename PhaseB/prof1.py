"""
590PR Examples from Week 4
J. Weible
Demonstrates some custom function designs and unit testing
with DocTests.
"""

import datetime
from pygeodesy import ellipsoidalVincenty as ev
import re

# x = [45, 3]
#
# def increment_something(some_list):
#     for i in range(len(some_list)):
#         some_list[i] += 1
#
#
# increment_something(x)
# print(x)


def hours_elapsed(ts1: str, ts2: str) -> float:
    """Given 2 strings containing dates & clock times,
    return the number of elapsed hours between them
    (as a float).
    :param ts1: date & 24-hr time as a string like '20160228 1830'
    :param ts2: date & 24-hr time as a string like '20160228 2200'
    :return: elapsed hours between ts1 & ts2, as a float.
    >>> hours_elapsed('20160228 1830', '20160228 2200')
    3.5
    >>> hours_elapsed('20160229 1815', '20160301 0000')
    5.75
    >>> # this confirms timestamp order doesn't matter:
    >>> hours_elapsed('20160301 0000', '20160229 1800')
    6.0
    """

    # Parse into datetime objects:
    dt1 = datetime.datetime.strptime(ts1, '%Y%m%d %H%M')
    dt2 = datetime.datetime.strptime(ts2, '%Y%m%d %H%M')

    diff = abs(dt2 - dt1)  # get the difference of time between
    # convert result into hours as a float:
    return diff.total_seconds() / 3600.0


def flip_direction(direction: str) -> str:
    """Given a compass direction 'E', 'W', 'N', or 'S', return the opposite.
    Raises exception with none of those.
    :param direction: a string containing 'E', 'W', 'N', or 'S'
    :return: a string containing 'E', 'W', 'N', or 'S'
    >>> flip_direction('E')
    'W'
    >>> flip_direction('S')
    'N'
    >>> flip_direction('SE')  # test an unsupported value
    Traceback (most recent call last):
    ...
    ValueError: Invalid or unsupported direction SE given.
    """
    if direction == 'E':
        return 'W'
    elif direction == 'W':
        return 'E'
    elif direction == 'N':
        return 'S'
    elif direction == 'S':
        return 'N'
    else:
        raise ValueError('Invalid or unsupported direction {} given.'.format(direction))


def myLatLon(lat: str, lon: str) -> ev.LatLon:
    """Given a latitude and longitude, normalize the longitude if necessary,
    to return a valid ellipsoidalVincenty.LatLon object.
    :param lat: the latitude as a string
    :param lon: the longitude as a string
    >>> a = ev.LatLon('45.1N', '2.0E')
    >>> my_a = myLatLon('45.1N', '2.0E')
    >>> a == my_a
    True
    >>> my_b = myLatLon('45.1N', '358.0W')
    >>> a == my_b  # make sure it normalizes properly
    True
    >>> myLatLon('15.1', '68.0')
    LatLon(15°06′00.0″N, 068°00′00.0″E)
    """

    if lon[-1] in ['E', 'W']:
        # parse string to separate direction from number portion:
        lon_num = float(lon[:-1])
        lon_dir = lon[-1]
    else:
        lon_num = float(lon)
    if lon_num > 180.0:  # Does longitude exceed range?
        lon_num = 360.0 - lon_num
        lon_dir = flip_direction(lon_dir)
        lon = str(lon_num) + lon_dir

    return ev.LatLon(lat, lon)


def read_one_HURDAT2_storm(file, storm_id=None) -> dict:
    """Read a single storm's data from a NOAA National Hurricane Center
    HURDAT2 file. The file pointer will be left in a spot ready to
    read the next storm.
    The storm's data will be returned in a dictionary that looks like this:
    {'id': 'AL171988', 'name': 'UNNAMED', 'num_rows': 2,
     'rows':
        [ ['19880904', '0000', ' ', 'TD', '28.0N', '93.5W', 30, -999, ..., -999, -999, -999],
          ['19880904', '0600', ' ', 'TD', '28.0N', '92.5W', 25, -999, ..., -999, -999, -999] ] }
    :param file: an open file handle pointing to a HURDAT2 file.
    :param storm_id: Optional. Search file for specific storm and load it.
    :return: a dictionary with the storm data or None if EOF or not found.
    >>> f = open('hurdat2-1851-2016-041117.txt', 'r')
    >>> otto = read_one_HURDAT2_storm(f, 'AL172010')
    >>> otto['name']
    'OTTO'
    >>> len(otto['rows'])
    47
    >>> s = read_one_HURDAT2_storm(f) # find next storm after OTTO
    >>> s['name']
    'PAULA'
    >>> s['rows']  # doctest: +ELLIPSIS
    [...['20101011', '1800', '', 'TS', ... 40, 0, 0, 0, 0], ...]
    >>> s = read_one_HURDAT2_storm(f, 'BAD_STORM_ID')
    >>> s is None
    True
    >>> f.close()
    """
    storm = {}  # start a blank dictionary
    if storm_id is not None:
        # Seek to beginning of file
        file.seek(0)
        # Search until we find the right header line:
        header = ''
        while storm_id not in header:
            header = file.readline()
            if header is None or header == '':
                return None
    else:
        # just read the next storm in file:
        header = file.readline()
        if header is None or header == '':
            return None
    # use a regular expression to split the 3 columns and discard spaces:
    (storm['id'], storm['name'], storm['num_rows'], ignore_this) = re.split(r'\s*,\s*', header)
    try:
        storm['num_rows'] = int(storm['num_rows'])
        storm['rows'] = []  # start with blank list of rows
        for r in range(storm['num_rows']):
            line = file.readline()     # get one detail data row
            values = line.split(',')  # split into list of strings at commas
            del values[-1]             # chop off the last value which is a newline
            # remove spaces from string values:
            for column in range(0, 6):
                values[column] = values[column].strip(' ')
            # convert the later columns from string to real ints:
            for column in range(6, len(values)):
                values[column] = int(values[column])
            storm['rows'].append(values)  # append this row of data
    except ValueError:
        print('Error converting an expected integer value while reading storm', storm['id'])
        return None
    return storm


def get_max_wind_speed(storm: dict) -> int:
    """Given a HURDAT2 storm dictionary, return the highest wind recorded.
    This comes from column number 6 in the data rows.
    :param storm: dictionary with all of one storm's data
    :return: maximum wind for the storm
    >>> f = open('hurdat2-1851-2016-041117.txt', 'r')
    >>> otto = read_one_HURDAT2_storm(f, 'AL172010')
    >>> get_max_wind_speed(otto)
    75
    >>> f.close()
    """
    highest = 0  # start at zero
    for r in storm['rows']:  # loop through the rows
        highest = max(highest, r[6])  # update highest value found
    return highest


def main():
    """Script main, to be executed as a demonstration."""

    # print('Demonstration of selected functions from this script...\n')
    # a = myLatLon('43.2N', '359.1W')
    # b = myLatLon('44.0N', '358.4W')
    #
    # meters = a.distanceTo(b)    # Calculate 'great circle' distance
    # distance = meters / 1852.0  # Divide to convert meters into nautical miles
    # bearing = a.bearingTo(b)
    # knots = distance / 6        # nautical miles / hours = knots
    # print('AL051952 later moved {:.2f} nm at initial heading of {:.2f} deg. \
    #     at a speed of {:.2f} kts'.format(distance, bearing, knots))
    #
    with open('hurdat2-1851-2016-041117.txt', 'r') as f:
        # try searching for a specific storm:
        # s = read_one_HURDAT2_storm(f, 'AL172010')
        # print(s)

        while True:
            s = read_one_HURDAT2_storm(f)
            if s is None:
                break      # hit end of file
            print(s['id'])
            print('highest wind:', get_max_wind_speed(s), '\n')


if __name__ == '__main__':
main()