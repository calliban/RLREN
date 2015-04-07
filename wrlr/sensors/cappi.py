# coding: utf-8
"""CAPPI - Constant Altitude Plan Position Indicator
This Package deals with CAPPI files containing Radar data.
"""

__docformat__ = 'restructuredtext en'

import gzip

import numpy as np

from sensors.cities import get_city


class CAPPI(object):
    """
    This is the class for working with CAPPI radar files
    """

    _file_name = ''
    altitude = "3 km"  # TODO set this to either a float or tuple according to use cases
    side = 200  # Side of the square matrix

    def __init__(self, city: str):

        # Validate the city name
        self.city = get_city(city)

        lat_line = np.linspace(start=self.city.lat_min, stop=self.city.lat_max, num=self.side)

        lon_line = np.linspace(start=self.city.lon_min, stop=self.city.lon_max, num=self.side)

        self.latitude, self.longitude = np.meshgrid(lon_line, lat_line, indexing='ij')

        self.y_size, self.x_size = self.city.shape
        self.y_upper_left, self.x_upper_left = self.city.box_ul
        self.y_lower_right, self.x_lower_right = self.city.box_lr
        self.data_size = self.x_size * self.y_size * 4  # Binary size for float data radar matrix

    def remap(self, latitude: float, longitude: float) -> list:
        """
        Remap a tuple (latitude, longitude) to (i, j) coordinates

        :param latitude: The latitude of the point
        :param longitude: The Longitude of the point
        :return: (i, j)
        """
        new_latitude = round((latitude - self.city.lat_min) * self.city.shape[0] / (
            self.city.lat_max - self.city.lat_min)) if self.city.lat_min <= latitude < self.city.lat_max else -1

        new_longitude = round((longitude - self.city.lon_min) * self.city.shape[1] / (
            self.city.lon_max - self.city.lon_min)) if self.city.lon_min <= longitude < self.city.lon_max else -1

        return new_latitude, new_longitude

    @property
    def file_name(self) -> str:
        """Returns the value of file_name
        :return: str
        """
        return self._file_name

    @file_name.setter
    def file_name(self, file_name: str) -> None:
        """Sets the value of file_name
        :param file_name:
        """
        self._file_name = file_name

    def open(self, file_name: str, use_full_map: bool=False, use_zr: bool=True) -> np.ndarray:
        """
        Open a single radar file given it's file_name".
        The use_full_map image may be obtained using the "use_full_map" parameter.

        :param file_name: The filename for a radar file
        :param use_full_map: Define whether to use the use_full_map data matrix or just the important part
        :param use_zr: Use Z-R (mmh-1)  data if true, or dBZ ir false
        :return local_map: The matrix map
        """

        with gzip.open(file_name) as data_file:
            local_map = np.fromstring(data_file.read(self.data_size),
                                      dtype=np.float32).reshape(self.y_size, self.x_size)

        # Cleanup process and conversion to MMH. This is important
        mask = local_map == local_map[2, 2]
        local_map[mask] = -999
        if not use_zr:
            return local_map
        local_map[-mask] = self.city.zr(local_map[-mask])

        if use_full_map:
            return local_map
        local_map = local_map[self.y_upper_left:self.y_lower_right, self.x_upper_left:self.x_lower_right]
        local_map = local_map[::self.city.y_direction, ::self.city.x_direction]
        local_map[local_map < 0] = 0
        return local_map


if __name__ == "__main__":
    x = CAPPI("BRU")
    print(x.file_name)
    x.file_name = "Jose"
    print(x.file_name)
