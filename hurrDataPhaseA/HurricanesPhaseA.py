import re
from datetime import datetime

# choose a file to input(Atlantic/Nencpac)
while True:
    selection = input('Enter the area name you want check, a for Atlantic, n for Nencpac: ')

    if selection is 'a':
        filename = 'hurdat2-1851-2016-041117.txt'
        # the pattern to locate the headers in Atlantic file
        pattern = '(AL)+\d+'
        break

    if selection is 'n':
        filename = 'hurdat2-nepac-1949-2016-041317.txt'
        # the pattern to locate the headers in Nencpac file
        pattern = '([CE]P)+\d+'
        break

    else:
        print("Cannot find the area.")
        continue

# create a dictionary to store the data
cyclone = {}

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
                landfall = 0

                cyclone[cyc_number]['Name'] = linedata[1].strip()
                cyclone[cyc_number]['Track_Number'] = linedata[2].strip()

                # storm_number += 1
            
            # process the content after header lines 
            else:
                try:
                    cyclone[cyc_number]['Year'] = linedata[0][:4]
                    cyclone[cyc_number]['Dates'].append(linedata[0])
                    cyclone[cyc_number]['Time'].append(linedata[1].strip())
                    cyclone[cyc_number]['Max'].append(linedata[6].strip())

                    if linedata[2].strip() == 'L':
                        landfall += 1
                    cyclone[cyc_number]['Landfall_Number'] = landfall

                except IndexError:
                    print(cyc_number)
    # print(storm_number)
    return cyclone

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
        max_storm[storm]= []
        max = 0
        for wind in cyclone[storm]['Max']:
            wind = int(wind)
            if wind > max:
                max = wind
                date = cyclone[storm]['Dates'][cyclone[storm]['Max'].index(str(wind))]
                time = cyclone[storm]['Time'][cyclone[storm]['Max'].index(str(wind))]
        max_storm[storm].append(max)
        max_storm[storm].append(datetime.strptime(date + time,'%Y%m%d%H%M'))

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
storm_max = max_of_storm(cyclone)
date = date_range(cyclone)
storm_num = year_storm_count(cyclone)
hurr_num = year_hurr_count(storm_max)

for storm in cyclone:
    print("======================================")
    print("Storm system name: " + cyclone[storm]['Name'])
    print("Date range from " + date[storm][0] + " to " + date[storm][1])
    print("The highest Maximum sustained wind (in knot): " , storm_max[storm][0] , " at ", storm_max[storm][1])
    print("It had " , cyclone[storm]['Landfall_Number'] , " time(s) 'landfalls'.")

for year in storm_num:
    print("Total number of storms in ", year, ' is ', storm_num[year])

for year in hurr_num:
    print("Total number of hurricanes in ", year, ' is ', hurr_num[year])
