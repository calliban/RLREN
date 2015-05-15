# coding: utf-8
"""
Includes a named tuple containing information for all available cities
"""
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

cities = dict(BRU=City(file_name='BRU',
                       lat_min=-23.72,
                       lat_max=-21.605,
                       lon_min=-50.3925,
                       lon_max=-48.2775,
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
                       zr=lambda dbz: piecewise(dbz, [dbz < -15, dbz >= -15],
                                                [0, lambda z: power(
                                                    (10 ** (z / 10.0)) / 32.0,
                                                    1 / 1.65)])),
              PPR=City(file_name='PPR',
                       lat_min=-22.925,
                       lat_max=-21.425,
                       lon_min=-52.125,
                       lon_max=-50.625,
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
                       zr=lambda dbz: piecewise(dbz, [dbz < -15, dbz >= -15],
                                                [0, lambda z: power(
                                                    (10 ** (z / 10.0)) / 32.0,
                                                    1 / 1.65)])),
              PI=City(file_name='PI',
                      lat_min=-23.3510900,
                      lat_max=-20.2013000,
                      lon_min=-44.2786700,
                      lon_max=-42.3058300,
                      box_ul=(150, 150),
                      box_lr=(350, 350),
                      shape=(500, 500),
                      lat_step=0.00899940,
                      lon_step=0.00986420,
                      x_direction=1,
                      y_direction=1,
                      date0="2014-01-01 00:01:00",
                      date1="2014-11-30 23:50:00",
                      folder="PC",
                      zr=lambda dbz: piecewise(dbz, [dbz < -15,
                                                     (dbz >= -15) &
                                                     (dbz <= 35.0),
                                                     (dbz > 35.0)],
                                               [0, lambda z: power(
                                                   (10 ** (z / 10.0)) / 300.0,
                                                   1 / 1.6),
                                                lambda z: power(
                                                    (10 ** (z / 10.0)) / 200.0,
                                                    1 / 1.4)])),
              SR=City(file_name='SR',
                      lat_min=-24.4973900,
                      lat_max=-22.6971100,
                      lon_min=-48.0850500,
                      lon_max=-46.0936500,
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
                      zr=lambda dbz: piecewise(dbz, [dbz < -15,
                                                     (dbz >= -15) &
                                                     (dbz <= 35.0),
                                                     (dbz > 35.0)],
                                               [0, lambda z: power(
                                                   (10 ** (z / 10.0)) / 300.0,
                                                   1 / 1.6),
                                                lambda z: power(
                                                    (10 ** (z / 10.0)) / 200.0,
                                                    1 / 1.4)])))