# coding: utf-8
"""CAPPI - Constant Altitude Plan Position Indicator
This Package deals with CAPPI files containing Radar data.
"""

__docformat__ = 'restructuredtext en'

import gzip

import numpy as np
from scipy.ndimage.filters import generic_filter

import cities
import circles


class CAPPI(object):
    """
    This is the class for working with CAPPI radar files

    :param city: A string for the radar location
    """

    _file_name = ''
    altitude = "3 km"
    side = 200  # Side of the square matrix
    data = None
    mask = 0
    mask_value = 0
    steiner_mask = None

    def __init__(self, city: str):
        self.city = cities.cities[city]

        lat_line = np.linspace(start=self.city.lat_min,
                               stop=self.city.lat_max,
                               num=self.side)
        lon_line = np.linspace(start=self.city.lon_min,
                               stop=self.city.lon_max,
                               num=self.side)

        self.latitude, self.longitude = np.meshgrid(lon_line, lat_line,
                                                    indexing='ij')

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

    def open(self, file_name: str='', remove_borders: bool=True,
             use_zr: bool=True) -> np.ndarray:
        """
        Open a single radar file given it's file_name".
        The remove_borders image may be obtained using the "remove_borders"
        parameter.

        :param file_name: The filename for a radar file
        :param remove_borders: Define whether to use the inner-radar matrix
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

        # Bin data files contain a marked value, which must not be used for
        # processing data. A simple way to avoid using it is to set it to an
        # invalid dBZ value.

        self.mask_value = cappi_map[2, 2]
        self.mask = cappi_map == self.mask_value  # This is a masked numpy array

        # While there may be uses for radar images with the use_zr flag set as
        # false, it is important to notice this data format is actually dBZ,
        # thus making it difficult some common operations over the image. This
        # flag is required to be False for the Steiner filtering.

        if use_zr:
            cappi_map[-self.mask] = self.city.zr(cappi_map[-self.mask])
            cappi_map[self.mask] = 0

        # This will reduce the matrix to the square matrix inside the 150 km
        # range of the weather radar.
        # Without the remove_borders flag active, most of this class won work as
        # planned, so it is advised not to use it for processing other than the
        # Steiner filtering.

        if remove_borders:
            cappi_map = cappi_map[self.y_upper_left:self.y_lower_right,
                                  self.x_upper_left:self.x_lower_right]
            cappi_map = cappi_map[::self.city.y_direction,
                                  ::self.city.x_direction]
            cappi_map[cappi_map < 0] = 0

        self.data = cappi_map

    def steiner_filter(self, data: np.ndarray):
        """
        Steiner Filter is based on the Steiner Method Steiner et al. (1995) for
        filtering convective rainfall from a radar image.
        This method follow 3 rules, which should be applied to every point the
        grid:

        1. Intensity: Any point above 40dBZ is a Convective Point
        2. Peak: Any point above a threshold (a) over the mean local rain
            (11 km radius circle) is a Convective Point
        3. Neighbor: Every point around a certain radius (b) around a Convective
            point is also a Convective Point

        (a) is the threshold
        (b) is given by the static method convective_radius, in this class

        :param data:
        """

        # 1. Intensity
        # This rule may be removed eventually after fixing 2. Peak

        rule_intensity = data <= 40.0

        # 2. Peak
        data = data.copy()

        # TODO improve performance here
        rule_peak = np.ones(rule_intensity.shape, dtype=rule_intensity.dtype)
        generic_filter(data, self._above_background, output=rule_peak, size=23)

        self.steiner_mask = np.logical_and(rule_peak, rule_intensity)
        data[self.steiner_mask] = self.mask_value

        # 3. Neighbor

        rule_neighbor = self._surrounding_area(data)
        self.steiner_mask = np.logical_and(self.steiner_mask, -rule_neighbor)
        self.steiner_mask = np.logical_or(self.steiner_mask, self.mask)

        return np.ma.array(self.data, mask=self.steiner_mask)

    def _above_background(self, data: np.ndarray) -> bool:
        """
        A filter function to be used with scipy.ndimage.filters.generic_filter
        in order to find the mean background
        intensity for the entire matrix.
        Returns a boolean np.ndarray with True being the values to filter out.

        :param data:
        :return:
        """

        # This function will be called about half a million times per image, and
        # should be optimized as much as possible

        point = data[len(data) // 2]
        if point == self.mask_value:
            return True

        data[len(data) // 2] = self.mask_value
        data = data[circles.background_line]
        data = data[data != self.mask_value]

        data = data.mean() if data.size else 0
        return False if point - self._threshold(point) > data else True

    def _surrounding_area(self, data: np.ndarray) -> np.ndarray:
        """
        This is a semi-optimized class for finding the surrounding area for a
        given intensity pixel.
        :param data:
        """

        output = np.zeros(data.shape, dtype=np.bool)

        line_max, column_max = data.shape
        line_min = 5
        column_min = 5
        line_max -= 5
        column_max -= 5
        for (line, column), value in np.ndenumerate(data):

            if value == self.mask_value:
                continue
            if line_min >= line or line >= line_max:
                continue
            if column_min >= column or column >= column_max:
                continue

            radius = self._convective_radius(value)
            output[line - radius:line + radius+1, column - radius:column + radius+1] +=\
                circles.convective_radius[radius]

        return output

    @staticmethod
    def _convective_radius(reflectivity):
        """
        Calculates the Convective Radius of a given convective, i.e. the
        radius in which all points should be considered convective.

        As per Steiner et al. (1995), Figure 6 (b)
        :param reflectivity: mean reflectivity over a 11 km radius in dBZ
        """

        # Tested against a simpler equation ( x//5 - 3) this resulting  formula
        # had almost twice the performance. This is a function that  will be
        # called several times, so performance enhancements are welcome.

        if reflectivity < 25:
            return 1
        elif reflectivity < 30:
            return 2
        elif reflectivity < 35:
            return 3
        elif reflectivity < 40:
            return 4
        else:
            return 5

    @staticmethod
    def _threshold(background_reflectivity: np.float) -> np.float:
        """
        Calculates the threshold a certain Z must to be above the background
        reflectivity in order to
        be considered a Convective Point.

        As per Steiner et al. (1995), Equation 2
        :param background_reflectivity:
        """

        # This function will be called several times (as many as there are
        # points in a map), so it should be as optimal as possible in order to
        # avoid performance issues.
        # If memory is no issue, maybe a full matrix should be generated here to
        # make use of numpy optimizations.

        if background_reflectivity < 0:
            return 10
        elif background_reflectivity < 42.43:
            return 10 - (background_reflectivity ** 2) / 180.0
        else:
            return 0

    def grid(self, data: np.ndarray, grid_size: int=50, shift: float=25):
        pass

    @staticmethod
    def split(data: np.ndarray, vertical: int, horizontal: int):
        """
        Splits the data ndarray into vertical x horizontal smaller arrays

        :param data:
        :param vertical:
        :param horizontal:
        :return:
        """
        return np.concatenate(np.array([np.vsplit(window, vertical) for window
                                        in np.hsplit(data, horizontal)]))

    @staticmethod
    def slice(data, windows):
        """
        Creates several sub-matrices

        :param data:
        :param windows:
        :return:
        """
        # TODO enhance documentation

        window_size = 100 // windows

        odd_adjust = 1 if window_size % 5 else 0

        v_split = CAPPI.split(data[window_size+odd_adjust:-window_size, :],
                              vertical=windows-1, horizontal=windows)
        h_split = CAPPI.split(data[:, window_size+odd_adjust:-window_size],
                              vertical=windows, horizontal=windows-1)
        vh_split = CAPPI.split(data[window_size+odd_adjust:-window_size,
                               window_size+odd_adjust:-window_size],
                               vertical=windows-1, horizontal=windows-1)
        full_split = CAPPI.split(data, vertical=windows, horizontal=windows)

        output = np.append(v_split, h_split, 0)
        output = np.append(output, vh_split, 0)
        output = np.append(output, full_split, 0)
        return output