import re
from datetime import datetime
from pygeodesy import ellipsoidalVincenty as ev

# choose a file to input(Atlantic/Nencpac)
# while True:
#     selection = input('Enter the area name you want check, a for Atlantic, n for Nencpac: ')
#
#     if selection is 'a':
#         filename = 'hurdat2-1851-2016-041117.txt
filename = 'hurdat2-1851-2016-041117.txt'
        # the pattern to locate the headers in Atlantic file
        # pattern = '(AL)+\d+'
pattern = '(AL)+\d+'
        # break

    # if selection is 'n':
    #     filename = 'hurdat2-nepac-1949-2016-041317.txt'
    #     the pattern to locate the headers in Nencpac file
    #     pattern = '([CE]P)+\d+'
    #     break
    #
    # else:
    #     print("Cannot find the area.")
    #     continue

# create a dictionary to store the data
cyclone = {}

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


def myLatLon(lat: str, lon: str):
    """Given a latitude and longitude, normalize them if necessary,
    to return a valid ellipsoidalVincenty.LatLon object.
    :param lat: the latitude as a string
    :param lon: the longitude as a string
    """

    # get number portion:
    if lon[-1] in ['E', 'W']:
        lon_num = float(lon[:-1])
        lon_dir = lon[-1]
    else:
        lon_num = float(lon)
    if lon_num > 180.0:  # Does longitude exceed range?
        lon_num = 360.0 - lon_num
        lon_dir = flip_direction(lon_dir)
        lon = str(lon_num) + lon_dir

    return ev.LatLon(lat, lon)





def tidying(filename, pattern):
    """
    Group the data by system names and extract corresponding detail
    :param filename:
    :param pattern:
    :return cyclone:
    """
    with open(filename) as file:

        # storm_number = 0
        for lines in file:
            linedata = lines.split(',')

            pat = re.compile(pattern)
            # process the header lines
            if pat.search(linedata[0]) is not None:
                cyc_number = linedata[0]
                cyclone[cyc_number] = {}
                cyclone[cyc_number]['Dates'] = []
                cyclone[cyc_number]['Time'] = []
                cyclone[cyc_number]['Max'] = []
                cyclone[cyc_number]['LatLon'] = []
                cyclone[cyc_number]['Extent'] = []
                landfall = 0

                cyclone[cyc_number]['Name'] = linedata[1].strip()
                cyclone[cyc_number]['Track_Number'] = linedata[2].strip()

                # storm_number += 1

            # process the content after header lines
            else:
                try:
                    cyclone[cyc_number]['Year'] = linedata[0][:4]
                    cyclone[cyc_number]['Dates'].append(linedata[0])
                    datetime = linedata[0] + linedata[1].strip()

                    cyclone[cyc_number]['Time'].append(linedata[1].strip())
                    cyclone[cyc_number]['Max'].append(linedata[6].strip())
                    extent_group = []
                    for i in range(8,20):
                        extent_group.append(int(linedata[i].strip()))
                    cyclone[cyc_number]['Extent'].append(extent_group)
                    # print(cyclone[cyc_number]['Extent'])

                    lat = linedata[4].strip()
                    lon = linedata[5].strip()
                    latlon = myLatLon(lat, lon)

                    # if float(lat[:-1]) > 180:
                    #     if lat[-1] == 'N':
                    #         lat = str(360 - float(lat[:-1])) + 'S'
                    #     else:
                    #         lat = str(360 - float(lat[:-1])) + 'N'
                    #
                    # if float(lon[:-1]) > 180:
                    #     if lon[-1] == 'W':
                    #         lon = str(360 - float(lon[:-1])) + 'E'
                    #     else:
                    #         lon = str(360 - float(lon[:-1])) + 'W'


                    cyclone[cyc_number]['LatLon'].append(latlon)

                    if linedata[2].strip() == 'L':
                        landfall += 1
                    cyclone[cyc_number]['Landfall_Number'] = landfall

                except IndexError:
                    print(cyc_number)
    # print(storm_number)
    return cyclone

def storm_distance(cyclone):
    """
    :param cyclone:
    :return:
    """
    storm_distance = {}

    for storm in cyclone:
        distance = 0
        for i in range(len(cyclone[storm]['LatLon'])-1):
                # piecewise_start = ev.LatLon(cyclone[storm]['LatLon'][i])[0], cyclone[storm]['LatLon'][i][1])
                # piecewise_end = ev.LatLon(cyclone[storm]['LatLon'][i+1])[0], cyclone[storm]['LatLon'][i+1][1])
                piecewise_start = cyclone[storm]['LatLon'][i]
                piecewise_end = cyclone[storm]['LatLon'][i+1]
                if piecewise_start == piecewise_end:
                    piecewise_distance = 0
                else:
                    piecewise_distance = piecewise_start.distanceTo(piecewise_end)
                distance += piecewise_distance
        storm_distance[storm] = distance

    return storm_distance


def storm_speed(cyclone):
    """
    :param cyclone:
    :return:
    """
    storm_speed = {}
    max_speed = {}
    mean_speed = {}

    for storm in cyclone:
        storm_speed[storm] = []
        max_speed[storm] = []
        mean_speed[storm] = []
        for i in range(len(cyclone[storm]['Time']) - 1):

            # piecewise_start = ev.LatLon(cyclone[storm]['LatLon'][i][0], cyclone[storm]['LatLon'][i][1])
            # piecewise_end = ev.LatLon(cyclone[storm]['LatLon'][i + 1][0], cyclone[storm]['LatLon'][i + 1][1])
            piecewise_start = cyclone[storm]['LatLon'][i]
            piecewise_end = cyclone[storm]['LatLon'][i + 1]
            if piecewise_start == piecewise_end:
                piecewise_distance = 0
            else:
                piecewise_distance = piecewise_start.distanceTo(piecewise_end)

            start_time = datetime.strptime(cyclone[storm]['Dates'][i] + cyclone[storm]['Time'][i], '%Y%m%d%H%M')
            end_time = datetime.strptime(cyclone[storm]['Dates'][i+1] + cyclone[storm]['Time'][i+1], '%Y%m%d%H%M')
            time = (end_time - start_time).total_seconds()
            #print("time:", time)
            if time == 0:
                avg_speed = 0
            else:
                avg_speed = piecewise_distance/time

            storm_speed[storm].append(avg_speed)
        if len(cyclone[storm]['Dates']) == 1:
            storm_speed[storm] = [0]
        try:
            # if storm_speed[storm].isnull:
            #     max_speed.append(0)
            #else:
                max_speed[storm].append(max(storm_speed[storm]))
                mean_speed[storm].append(sum([speed for speed in storm_speed[storm]])/len(storm_speed[storm]))
        except ValueError:
            print(storm)
    return max_speed, mean_speed


def initial_bearing(cyclone):
    for storm in cyclone:
        cyclone[storm]['Bearing'] = []
        for i in range(len(cyclone[storm]['Dates']) - 1):
            # piecewise_start = ev.LatLon(cyclone[storm]['LatLon'][i][0], cyclone[storm]['LatLon'][i][1])
            # piecewise_end = ev.LatLon(cyclone[storm]['LatLon'][i + 1][0], cyclone[storm]['LatLon'][i + 1][1])
            piecewise_start = cyclone[storm]['LatLon'][i]
            piecewise_end = cyclone[storm]['LatLon'][i + 1]
            if piecewise_start == piecewise_end:
                cyclone[storm]['Bearing'].append(0)
            else:
                cyclone[storm]['Bearing'].append(piecewise_start.bearingTo(piecewise_end))


def max_extent(cyclone):
    case = {}
    for storm in cyclone:
        case[storm] = []
        for extents in cyclone[storm]['Extent']:
            # print(extents)
            try:
                if len(set(extents[-4:])) != 1:
                    extent = max(extents[-4:])
                    case[storm].append(extents[-4:].index(extent))
                elif len(set(extents[-8:-4])) != 1:
                    extent = max(extents[-8:-4])
                    case[storm].append(extents[-8:-4].index(extent))
                elif len(set(extents[-12:-8])) != 1:
                    extent = max(extents[-12:-8])
                    case[storm].append(extents[-12:-8].index(extent))
                else:
                    case[storm].append(99)
            except TypeError as te:
                print(te, cyclone[storm]['Extent'])
    return case

def dir_accurate_case(cyclone, case):
    accurate_case = 0
    case_num = 0

    for storm in cyclone:
        for i in range(1, len(case[storm])):
            if case[storm][i] != 99:
                case_num += 1
                try:
                    expect_dir_low = cyclone[storm]['Bearing'][i-1] + 45
                    expect_dir_high = cyclone[storm]['Bearing'][i-1] + 90

                except TypeError:
                    print(cyclone[storm]['Bearing'])

                degree = (case[storm][i-1]*2 + 1) * 45

                if expect_dir_high >= 360:
                    expect_dir_high = expect_dir_high - 360
                    if degree > expect_dir_low or degree < expect_dir_high:
                        accurate_case += 1
                elif expect_dir_low < degree < expect_dir_high:
                    accurate_case += 1


    return accurate_case / case_num



def year_storm_count(cyclone):
    """
    Get the number of storms happened per year
    :param cyclone:
    :return storm_per_year:
    """
    year = None
    storm_per_year = {}
    for storm in cyclone:
        if cyclone[storm]['Year'] != year:
            year = cyclone[storm]['Year']
            storm_per_year[year] = 1
            max_storm = max_of_storm(cyclone)
        else:
            storm_per_year[year] += 1

    # print(storm_per_year)
    return storm_per_year


def date_range(cyclone):
    """
    Get the date range of every storm
    :param cyclone:
    :return drange:
    """
    drange = {}
    for storm in cyclone:
        mininum = min(cyclone[storm]['Dates'])
        maxinum = max(cyclone[storm]['Dates'])
        mininum = mininum[:4] + '-' + mininum[4:6] + '-' + mininum[6:8]
        maxinum = maxinum[:4] + '-' + maxinum[4:6] + '-' + maxinum[6:8]

        drange[storm] = []
        drange[storm].append(mininum)
        drange[storm].append(maxinum)

    return drange


def max_of_storm(cyclone):
    """
    Get the highest Maximum sustained wind and when it first occurred
    :param cyclone:
    :return max_storm:
    """
    max_storm = {}
    for storm in cyclone:
        max_storm[storm] = []
        max = 0
        for wind in cyclone[storm]['Max']:
            wind = int(wind)
            if wind > max:
                max = wind
                date = cyclone[storm]['Dates'][cyclone[storm]['Max'].index(str(wind))]
                time = cyclone[storm]['Time'][cyclone[storm]['Max'].index(str(wind))]
        max_storm[storm].append(max)
        max_storm[storm].append(datetime.strptime(date + time, '%Y%m%d%H%M'))

    return max_storm


def year_hurr_count(storm_max):
    """
    Get the number of hurricanes happened per year
    :param cyclone:
    :return hurr_per_year:
    """
    storm_max = max_of_storm(cyclone)
    hurr_per_year = {}
    year = 0
    for storm in storm_max:
        if storm_max[storm][1].year != year:
            year = storm_max[storm][1].year
            hurr_per_year[year] = 0

        if storm_max[storm][0] >= 64:
            hurr_per_year[year] += 1

    # print(hurr_per_year)
    return hurr_per_year







cyclone = tidying(filename, pattern)
# storm_max = max_of_storm(cyclone)
# date = date_range(cyclone)
# storm_num = year_storm_count(cyclone)
# hurr_num = year_hurr_count(storm_max)
# storm_dis = storm_distance(cyclone)
# storm_speed_max, storm_speed_mean = storm_speed(cyclone)
initial_bearing(cyclone)
case = max_extent(cyclone)
rate = dir_accurate_case(cyclone, case)
print(rate)
#print(case)

# for storm in cyclone:
#     print(cyclone[storm]['Bearing'])

# for storm in cyclone:

        # print("======================================")
        # print("Storm system ID: " + storm)
        # if cyclone[storm]['Name'] != 'UNNAMED':
            # print("Storm system name: " + cyclone[storm]['Name'])
        # print("Date range from " + date[storm][0] + " to " + date[storm][1])
        # print("The highest Maximum sustained wind (in knot): ", storm_max[storm][0], " at ", storm_max[storm][1])
        # print("It had ", cyclone[storm]['Landfall_Number'], " time(s) 'landfalls'.")
        # print("The total distance this storm was tracked is: ", storm_dis[storm])
        # print(storm_speed_max[storm][0])
        # print(storm_speed_mean[storm][0])
        # print(cyclone[storm][datetime])
# print(storm_dis)
# print(cyclone['AL122004']['200409160600'])



# for year in storm_num:
#     print("Total number of storms in ", year, ' is ', storm_num[year])
#
# for year in hurr_num:
#     print("Total number of hurricanes in ", year, ' is ', hurr_num[year])
