# coding: utf-8
"""
This file deals with Earth Networks lightning data format
"""

__docformat__ = 'restructuredtext en'

import numpy as np
import pandas as pd

from wrlr import cities


class EarthNetworks(object):
    """
    This class creates objects representing lightning data from Earth Networks
    """

    side = 200
    data = None
    slices = None

    def __init__(self, city: str):
        self.city = cities.cities[city]

        lat_line = np.linspace(start=self.city.lat_min,
                               stop=self.city.lat_max,
                               num=self.side)
        lon_line = np.linspace(start=self.city.lon_min,
                               stop=self.city.lon_max,
                               num=self.side)

        self.longitude, self.latitude = np.meshgrid(lon_line, lat_line,
                                                    indexing='xy')

        self.y_size, self.x_size = self.city.shape
        self.y_upper_left, self.x_upper_left = self.city.box_ul
        self.y_lower_right, self.x_lower_right = self.city.box_lr
        self.data_size = self.x_size * self.y_size * 4  # Binary size for float

    def remap(self, latitude: float, longitude: float) -> list:
        """
        Remap a tuple (latitude, longitude) to a mapping matrix
        Return (i, j) coordinates

        :param latitude: The latitude of the point
        :param longitude: The Longitude of the point
        :return: (i, j)
        """

        if self.city.lat_min <= latitude < self.city.lat_max:
            lat_window = (self.city.lat_max - self.city.lat_min)
            normal_lat = (latitude - self.city.lat_min) / lat_window
            new_latitude = round(normal_lat * self.city.shape[0])
        else:
            new_latitude = -1

        if self.city.lon_min <= longitude < self.city.lon_max:
            lon_window = (self.city.lon_max - self.city.lon_min)
            normal_lon = (longitude - self.city.lon_min) / lon_window
            new_longitude = round(normal_lon * self.city.shape[1])
        else:
            new_longitude = -1

        return new_latitude, new_longitude

    def open(self, file_name: str):
        """
        Read a single lightning file given it's full file path and file_name.
        Saves it as a pandas.DataFrame where:
        * tipo: either 'CG' for Cloud-to-Ground or 'IC' for intracloud;
        * datahora: a date-time timestamp;
        * latitude: the latitude of the occurrence as a float;
        * longitude: the longitude of the occurrence as a float;
        * pico_corrente: either '+' for positive or '-' for negative polarity,
            with no-polarity converted to '+';
        * multiplicidade: number of strokes for each occurrence;

        :param file_name: the full path for a lightning file
        """
        data = pd.read_csv(file_name,
                           sep=';',
                           index_col='id',
                           converters={'pico_corrente':
                                       lambda z: '-' if '-' in z else '+'},
                           usecols=('id',
                                    'tipo',
                                    'datahora',
                                    'latitude',
                                    'longitude',
                                    'pico_corrente',
                                    'multiplicidade'))

        data['datahora'] = pd.to_datetime(data['datahora'])

        # Reduce to valid intervals only

        data = data[(data['latitude'] >= self.city.lat_min) &
                    (data['latitude'] <= self.city.lat_max) &
                    (data['longitude'] >= self.city.lon_min) &
                    (data['longitude'] <= self.city.lon_max)]

        self.data = data

    @staticmethod
    def _split(data: np.ndarray, lines: int, columns: int):
        """
        Splits the data ndarray into lines x columns smaller arrays

        :param data:
        :param lines:
        :param columns:
        :return:
        """
        tmp = np.concatenate(np.array([np.vsplit(window, lines) for window
                                       in np.hsplit(data, columns)]))
        return [(i[0, 0], i[-1, -1]) for i in tmp]

    def _slice(self, windows):
        """
        Creates Lat-Lon constrain boxes

        :return:
        """

        window_size = 100 // windows
        odd_adjust = 1 if window_size % 5 else 0

        # Split without displacement

        tmp_lat = self._split(self.latitude, lines=windows, columns=windows)
        tmp_lon = self._split(self.longitude, lines=windows, columns=windows)

        full_split = [[[lat_min, lon_min], [lat_max, lon_max]] for
                      (lat_min, lat_max), (lon_min, lon_max)
                      in zip(tmp_lat, tmp_lon)]

        # Split with line displacement

        tmp_lat = self._split(
            self.latitude[window_size + odd_adjust:-window_size, :],
            lines=windows - 1, columns=windows)
        tmp_lon = self._split(
            self.longitude[window_size + odd_adjust:-window_size, :],
            lines=windows - 1, columns=windows)

        l_split = [[[lat_min, lon_min], [lat_max, lon_max]] for
                   (lat_min, lat_max), (lon_min, lon_max)
                   in zip(tmp_lat, tmp_lon)]

        # Split with column displacement

        tmp_lat = self._split(
            self.latitude[:, window_size + odd_adjust:-window_size],
            lines=windows, columns=windows - 1)
        tmp_lon = self._split(
            self.longitude[:, window_size + odd_adjust:-window_size],
            lines=windows, columns=windows - 1)

        c_split = [[[lat_min, lon_min], [lat_max, lon_max]] for
                   (lat_min, lat_max), (lon_min, lon_max)
                   in zip(tmp_lat, tmp_lon)]

        # Split with line and column displacement

        tmp_lat = self._split(
            self.latitude[window_size + odd_adjust:-window_size,
                          window_size + odd_adjust:-window_size],
            lines=windows - 1, columns=windows - 1)
        tmp_lon = self._split(
            self.longitude[window_size + odd_adjust:-window_size,
                           window_size + odd_adjust:-window_size],
            lines=windows - 1, columns=windows - 1)

        lc_split = [[[lat_min, lon_min], [lat_max, lon_max]] for
                    (lat_min, lat_max), (lon_min, lon_max)
                    in zip(tmp_lat, tmp_lon)]

        # Merge all splits into one

        self.slices = full_split + l_split + c_split + lc_split