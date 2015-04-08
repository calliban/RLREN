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

    :param city: A string for the radar location, such as 'BRU', 'PI', 'PPR', or 'SR'
    """

    _file_name = ''
    altitude = "3 km"  # TODO set this to either a float or tuple according to use cases
    side = 200  # Side of the square matrix
    data = None

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
        Remap a tuple (latitude, longitude) to a mapping matrix
        Return (i, j) coordinates

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

    def open(self, file_name: str='', remove_borders: bool=True, use_zr: bool=True) -> np.ndarray:
        """
        Open a single radar file given it's file_name".
        The remove_borders image may be obtained using the "remove_borders" parameter.

        :param file_name: The filename for a radar file
        :param remove_borders: Define whether to use the inner-radar matrix or not
        :param use_zr: Use Z-R (mmh-1)  data if true, or dBZ ir false
        :return cappi_map: The matrix map
        """

        if file_name == '':
            file_name = self._file_name

        with gzip.open(file_name) as data_file:
            data_stream = data_file.read(self.data_size)
            local_map = np.fromstring(data_stream, dtype=np.float32)
            cappi_map = local_map.reshape(self.y_size, self.x_size)

            # TODO Explicit delete - must profile do select the best option
            del data_stream
            del local_map

        # Bin data files contain a "transparency" value for most data, which must not be used for processing
        # data. A simple way to avoid using it is to set it to an invalid dBZ value.
        # A simpler approach is to convert the data to MMH and then change this mask to 0, which is valid.
        # TODO can I use scikit-image to improve this filtering? This is a project-wide decision!

        mask = cappi_map == cappi_map[2, 2]  # This is a masked numpy array!

        # While there may be uses for radar images with the use_zr flag set as false, it is important
        # to notice this data format is actually dBZ, thus making it difficult some common operations
        # over the image. This flag is required to be False for the Steiner filtering.

        if use_zr:
            cappi_map[-mask] = self.city.zr(cappi_map[-mask])
            cappi_map[mask] = 0
        else:
            cappi_map[mask] = -999

        # This will reduce the matrix to the square matrix inside the 150 km range of the weather radar.
        # Without the remove_borders flag active, most of this class won work as planned, so it is
        # advised not to use it for processing other than the Steiner filtering.

        if remove_borders:
            cappi_map = cappi_map[self.y_upper_left:self.y_lower_right, self.x_upper_left:self.x_lower_right]
            cappi_map = cappi_map[::self.city.y_direction, ::self.city.x_direction]
            cappi_map[cappi_map < 0] = 0

        self.data = cappi_map


def main():
    """This is a completely trivial test that will only run in my machine and should be removed"""
    # TODO create some real tests

    x = CAPPI("BRU")
    print(x.file_name)
    x.file_name = "/home/likewise-open/LOCAL/joao.garcia/Workplace/1.INPE/Data/Radar/BR_PP/2014/01/RD_203022195_20140101000700.raw.gz"
    x.open()
    print(x.data[0])
    print(x.file_name)


if __name__ == "__main__":
    main()