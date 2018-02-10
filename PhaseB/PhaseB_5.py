"""
IS590PR Assignment 2: Tropical storm tracking analytics
Jianzhang Chen, Yichong Guo, Chaohan Shang
"""

import datetime
from pygeodesy import ellipsoidalVincenty as ev
import re


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
            line = file.readline()  # get one detail data row
            values = line.split(',')  # split into list of strings at commas
            del values[-1]  # chop off the last value which is a newline
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

def get_landfall_num(storm: dict):
    """Given a HURDAT2 storm dictionary, return the times of landfalls of a storm.
    This comes from column number 3 in the data rows.
    :param storm: dictionary with all of one storm's data
    :return: landfall times
    """
    rows = storm['rows']
    landfall_num = 0
    for i in range(len(rows)):
        if rows[i][2] == 'L':
            landfall_num += 1
    return landfall_num


def get_max_wind_speed(storm: dict) -> int:
    """Given a HURDAT2 storm dictionary, return the highest wind recorded.
    This comes from column number 6 in the data rows.
    :param storm: dictionary with all of one storm's data
    :return: maximum wind for the storm
    """
    max_datetime = datetime
    highest = 0  # start at zero
    for r in storm['rows']:  # loop through the rows
        if r[6] > highest:  # update highest value found
            highest = r[6]
            max_datetime = datetime.datetime.strptime(r[0]+r[1], '%Y%m%d%H%M')
    return highest, max_datetime


def hours_elapsed(ts1: str, ts2: str) -> float:
    """Given 2 strings containing dates & clock times,
    return the number of elapsed hours between them
    (as a float).
    :param ts1: date & 24-hr time as a string like '20160228 1830'
    :param ts2: date & 24-hr time as a string like '20160228 2200'
    :return: elapsed hours between ts1 & ts2, as a float.
    """

    # Parse into datetime objects:
    dt1 = datetime.datetime.strptime(ts1, '%Y%m%d%H%M')
    dt2 = datetime.datetime.strptime(ts2, '%Y%m%d%H%M')

    diff = abs(dt2 - dt1)  # get the difference of time between
    # convert result into hours as a float:
    return diff.total_seconds() / 3600.0


def flip_direction(direction: str) -> str:
    """Given a compass direction 'E', 'W', 'N', or 'S', return the opposite.
    Raises exception with none of those.
    :param direction: a string containing 'E', 'W', 'N', or 'S'
    :return: a string containing 'E', 'W', 'N', or 'S'
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


def print_date_range(storm: dict):
    """Given a HURDAT2 storm dictionary, return the date range of the storm.
    This is calculated with columns number 1 and 2 in every two data rows.
    :param storm: dictionary with all of one storm's data
    :return: the date range of the storm
    """
    rows = storm['rows']
    begin = datetime.datetime.strptime(rows[0][0] + rows[0][1], '%Y%m%d%H%M')
    end = datetime.datetime.strptime(rows[-1][0] + rows[-1][1], '%Y%m%d%H%M')

    print("Date range from {0} to {1}".format(str(begin), str(end)))


def get_distance(start, end):
    """Given start point and end point, return the distance between.
    :param start: start point
    :param end: end point
    :return: distance between
    """
    distance = 0
    if start == end:
        distance = 0
    else:
        distance = start.distanceTo(end)

    return distance


def storm_speed(storm: dict):
    """Given a HURDAT2 storm dictionary, return the max and the mean speed of the storm.
    :param storm: dictionary with all of one storm's data
    :return: mean speed and mean speed
    """
    rows = storm['rows']

    speeds = []
    distance = 0

    for i in range(len(rows) - 1):
        pre_start = myLatLon(rows[i][4], rows[i][5])
        pre_end = myLatLon(rows[i + 1][4], rows[i + 1][5])
        pre_distance = get_distance(pre_start, pre_end)
        pre_time = hours_elapsed(rows[i][0] + rows[i][1], rows[i + 1][0] + rows[i + 1][1])

        speeds.append((pre_distance/1852)/pre_time)

        distance += (pre_distance/1852)

    time = hours_elapsed(rows[0][0] + rows[0][1], rows[-1][0] + rows[-1][1])


    if time == 0:
        mean_speed = 0
        max_speed = 0
    else:
        mean_speed = distance / time
        max_speed = max(speeds)

    return mean_speed, max_speed

def same_value_index(value_list: list):
    """Given a list of wind extent values, return the indices of the max values.
    :param value_list: wind extent values
    :return: the max values's indices
    """
    max_value = max(value_list)
    index_list = []
    for i in range(len(value_list)):
        if value_list[i] == max_value:
            index_list.append(i)
    return index_list

def dir_accurate_case(storm: dict):
    """Given a HURDAT2 storm dictionary, return the number of valid cases and the number of accurate cases.
    :param storm: dictionary with all of one storm's data
    :return: the number of valid cases and the number of accurate cases
    """
    rows = storm['rows']

    case = []
    accurate_case = 0
    case_num = 0


    for i in range(len(rows)-1):
        if len(set(rows[i][-4:])) != 1 or (len(set(rows[i][-4:])) == 1 and set(rows[i][-4:]) != {0} and set(rows[i][-4:]) != {-999}):
            case.append(same_value_index(rows[i][-4:]))
        elif len(set(rows[i][-8:-4])) != 1 or (len(set(rows[i][-8:-4])) == 1 and set(rows[i][-8:-4]) != {0} and set(rows[i][-8:-4]) != {-999}):
            case.append(same_value_index(rows[i][-8:-4]))
        elif len(set(rows[i][-12:-8])) != 1 or (len(set(rows[i][-12:-8])) == 1 and set(rows[i][-12:-8]) != {0} and set(rows[i][-12:-8]) != {-999}):
            case.append(same_value_index(rows[i][-12:-8]))
        else:
            case.append([99])


        start = myLatLon(rows[i][4], rows[i][5])
        end = myLatLon(rows[i+1][4], rows[i+1][5])


        degree = start.bearingTo(end) if start != end else 0

        degree_low = degree + 45
        degree_high = degree +90

        degree_low = (degree_low-360) if degree_low > 360 else degree_low
        degree_high = (degree_high - 360) if degree_high > 360 else degree_high


        if case[i] != [99]:
            case_num += 1
            for j in case[i]:
                if (j * 90 < degree_low < (j + 1) * 90) or (j * 90 < degree_high < (j + 1) * 90):
                    accurate_case += 1
                    break

    return accurate_case, case_num

def get_year(storm: dict):
    """Given a HURDAT2 storm dictionary, return the year of the storm.
    This comes from the last 4 digits of storm ID
    :param storm: dictionary with all of one storm's data
    :return: the year of the storm
    """
    return storm['id'][-4:]

def count_storm(storm: dict, year: dict):
    """
    A counter for storm number per year
    Given a HURDAT2 storm dictionary and the year of the storm.
    :param storm: dictionary with all of one storm's data
    :param year: the year of the storm
    """
    year[storm['id'][-4:]][0] = year[storm['id'][-4:]][0] + 1

def count_hurricane(storm: dict, year: dict):
    """
    A counter for hurricane number per year
    Given a HURDAT2 storm dictionary and the year of the storm.
    :param storm: dictionary with all of one storm's data
    :param year: the year of the storm
    """
    for i in storm['rows']:
        if i[6] >= 64:
            year[storm['id'][-4:]][1] = year[storm['id'][-4:]][1] + 1
            break


def main():
    """Script main, to be executed as a demonstration."""

    # filename = 'hurdat2-1851-2016-041117.txt'

    while True:
        selection = input('Enter the area name you want check, a for Atlantic, n for Nencpac: ')

        if selection is 'a':
            filename = 'hurdat2-1851-2016-041117.txt'
            break
        if selection is 'n':
            filename = 'hurdat2-nepac-1949-2016-041317.txt'
            break
        else:
            print("Cannot find the area.")
            continue


    overall_accurate_number = 0
    overall_case_number = 0
    year = {}

    while True:
        function = input('Enter the function you want, s for checking by storm, y for checking by year: ')
        if function is 's':
            storm_id = input("Type in the storm ID you want check or 'a' for all records: ")

            if storm_id == 'a':
                storm_id = None
            break

        elif function is 'y':
            storm_id = None
            break

        else:
            print("Cannot find the function.")
            continue

    try:
        with open(filename, 'r') as f:

            s1 = 0

            while True:

                s = read_one_HURDAT2_storm(f, storm_id)

                if s is None or (s == s1):
                    break  # hit end of file

                s1 = s
                accurate_number, case_number = dir_accurate_case(s)
                overall_accurate_number += accurate_number
                overall_case_number += case_number

                if function is 's':
                    print('============================')
                    print(s['id'])
                    if s['name'] != 'UNNAMED':
                        print(s['name'])
                    print_date_range(s)
                    print('number of landfalls:', get_landfall_num(s))
                    max_wind, max_time = get_max_wind_speed(s)
                    print('highest wind:', max_wind, 'first occurs at:', max_time)
                    mean_speed, max_speed = storm_speed(s)
                    print('max speed:', max_speed)
                    print('mean speed:', mean_speed, '\n')

                elif function is 'y':
                    years = get_year(s)
                    if years not in year.keys():
                        year[years] = [0, 0]
                    count_storm(s, year)
                    count_hurricane(s, year)


    except ValueError as ve:
        print("Cannot find the storm.")



    if function is 'y':
        for y in year:
            print('year', y, 'has', year[y][0], 'storms and', year[y][1], 'hurricanes.')

    if storm_id is None:
        print('\n')
        print('Based on physics, we expect that the quadrant with the highest winds \n'
              'should typically be somewhere between 45-90 degrees clockwise of the \n'
              'storm’s recent direction of movement.')
        print('The accuracy of this hypothesis is ', overall_accurate_number / overall_case_number)


if __name__ == '__main__':
    main()
