# coding: utf-8
__docformat__ = 'restructuredtext en'

import collections
from numpy import piecewise, power

valid_cities = ('BRU', 'PPR', 'SR', 'PI')

City = collections.namedtuple('City',
                              ('file_name',
                               'lat_min',
                               'lat_max',
                               'lon_min',
                               'lon_max',
                               'box_ul',
                               'box_lr',
                               'shape',
                               'lat_step',
                               'lon_step',
                               'x_direction',
                               'y_direction',
                               'date0',
                               'date1',
                               'folder',
                               'zr'))

# Bauru - SP

cities = {'BRU': City(file_name='BRU',
                      lat_min=-23.0975,
                      lat_max=-21.605,
                      lon_min=-49.7775,
                      lon_max=-48.285,
                      box_ul=(281, 563),
                      box_lr=(481, 763),
                      shape=(667, 1000),
                      lat_step=0.0075000,
                      lon_step=0.0075000,
                      x_direction=1,
                      y_direction=-1,
                      date0="2014-01-01 00:07:00",
                      date1="2014-11-30 06:59:00",
                      folder="BR_PP",
                      zr=lambda dBZ: piecewise(dBZ, [dBZ < -900, dBZ >= -900],
                                               [0, lambda z: power((10 ** (z / 10.0)) / 32.0, 1 / 1.65)])),
          'PPR': City(file_name='PPR',
                      lat_min=-22.9175,
                      lat_max=-21.425,
                      lon_min=-52.125,
                      lon_max=-50.6325,
                      box_ul=(257, 250),
                      box_lr=(457, 450),
                      shape=(667, 1000),
                      lat_step=0.0075000,
                      lon_step=0.0075000,
                      x_direction=1,
                      y_direction=-1,
                      date0="2014-01-01 00:07:00",
                      date1="2014-11-30 06:59:00",
                      folder="BR_PP",
                      zr=lambda dBZ: piecewise(dBZ, [dBZ < -900, dBZ >= -900],
                                               [0, lambda z: power((10 ** (z / 10.0)) / 32.0, 1 / 1.65)])),
          'PI': City(file_name='PI',
                     lat_min=-23.3420906,
                     lat_max=-21.55121,
                     lon_min=-44.27867,
                     lon_max=-42.3156942,
                     box_ul=(150, 150),
                     box_lr=(350, 350),
                     shape=(500, 500),
                     lat_step=0.0089994,
                     lon_step=0.0098642,
                     x_direction=1,
                     y_direction=1,
                     date0="2014-01-01 00:01:00",
                     date1="2014-11-30 23:50:00",
                     folder="PC",
                     zr=lambda dBZ: piecewise(dBZ, [dBZ < -900, (dBZ >= -900) & (dBZ <= 35.0), (dBZ > 35.0)],
                                              [0, lambda z: power((10 ** (z / 10.0)) / 300.0, 1 / 1.6),
                                               lambda z: power((10 ** (z / 10.0)) / 200.0, 1 / 1.4)])),
          'SR': City(file_name='SR',
                     lat_min=-24.4883886,
                     lat_max=-22.69711,
                     lon_min=-48.08505,
                     lon_max=-46.103607,
                     box_ul=(150, 150),
                     box_lr=(350, 350),
                     shape=(500, 500),
                     lat_step=0.0099570,
                     lon_step=0.0090014,
                     x_direction=1,
                     y_direction=1,
                     date0="2014-01-01 00:11:00",
                     date1="2014-11-30 23:50:00",
                     folder="SR",
                     zr=lambda dBZ: piecewise(dBZ, [dBZ < -900, (dBZ >= -900) & (dBZ <= 35.0), (dBZ > 35.0)],
                                              [0, lambda z: power((10 ** (z / 10.0)) / 300.0, 1 / 1.6),
                                               lambda z: power((10 ** (z / 10.0)) / 200.0, 1 / 1.4)]))}


def get_city(city_name):
    """
    Select a city from the available radar list
    Valid names are:
        BRU - for Bauru-SP
        PPR - for Presidente Prudente-SP
        PI - for Pico do Couto-RJ
        SR - for Sao Roque-SP
    :param city_name: a string with the code-file_name of the radar/city
    :return: A named tuple containing data about the city
        file_name - Radar Codename String
        lat_min - Minimum value of Latitude of the 400x400 box
        lat_max - Maximum value of Latitude of the 400x400 box
        lon_min - Minimum value of Longitude of the 400x400 box
        lon_max - Maximum value of Longitude of the 400x400 box
        box_ul - Uppermost Leftmost boundary of the 400x400 box
        box_lr - Lowermost Rightmost boundary of the 400x400 box
        shape - Original radar file shape
        lat_step - latitude step
        lon_step - longitude step
        x_direction - x diretion adjust for matrix[::y, ::x]
        y_direction - x diretion adjust for matrix[::y, ::x]
    """
    if city_name in valid_cities:
        return cities[city_name]
    else:
        raise ValueError("Value not in valid_cities")
