# coding: utf-8
"""
Handle iterating over file lists, specially for CAPPI files as they need to be
 set in intervals
"""
__docformat__ = 'restructuredtext en'

import os
from collections import namedtuple

from pandas import to_timedelta, date_range, to_datetime

# A justification for the use of pandas' time instead of datetime is the
# simplicity. If this software was intended to be used within machines
# other than this, a check would be needed, or the use of datetime would
# be required.

DRange = namedtuple('DRange', ['start', 'end', 'files'])


class Handler(object):
    """
    Handles file-lists and can be used as an iterator in order to get all files
     available in a certain path.
    """

    dates = None
    files = None
    iterable = None

    def __init__(self, path: str):
        self.path = path

    def perform(self):
        self.list_files(self.path)
        self.list_dates()

    def list_files(self):
        """
        Lists all visible (i.e. not starting with a dot) files in a directory
         and all its subdirectories, and stores them in alphabetical order,
         which is the same as the date in the name of such files for the scope
         of this work

        :param path: Root path of the files to be handled
        """

        output = []
        for directory, _, files in os.walk(self.path):
            for f in files:
                if f[0] != '.':
                    file_name = os.path.join(directory, f)
                    output.append(file_name)

        self.files = sorted(output)

    def list_dates(self):
        """
        This method will try to obtain the date from a file name, which is
         useful specially for radar files.
        """

        dates = []
        for filename in self.files:
            filename = (filename.split('_')[-1]).split('.')[0]  # Date portion
            date = to_datetime(filename)
            dates.append(date)

        self.dates = dates

    def generate_date_tuples(self, length: str, step: str):
        """
        This method generates a list of named_tuples self.iterable to be used
         when iterating over itself. Each element contains the starting and end
         dates, as well as a list of all files in such length.
        An alternative method would be to save this list as a file, and include
         a flag to explicitly reload it if exists, to reduce loading times.

        :param length: the duration of each time interval
        :param step: the time step between the starting time of two intervals
        """

        # Grant the data starts at minute 00, nas has smooth start and ending

        tmp_start = to_datetime(self.dates[0].strftime("%Y%m%d"))
        tmp_start = tmp_start - to_timedelta("1d")
        tmp_end = to_datetime(self.dates[-1].strftime("%Y%m%d"))
        tmp_end = tmp_end + to_timedelta("1d")

        start = date_range(start=tmp_start, end=tmp_end, freq=step)
        end = start + to_timedelta(length)

        # A namedtuple was used for clarity of reading for the return type

        iterable = []
        i = 0
        for d_start, d_end in zip(start, end):
            files = []
            for date, file_path in zip(self.dates[i:], self.files[i:]):
                i += 1
                if d_start <= date < d_end:
                    files.append(file_path)
                elif date >= d_end:
                    i -= 1
                    break
            if files:
                iterable.append(DRange(start=d_start, end=d_end, files=files))
        self.iterable = iterable

    def __iter__(self):
        """
        Iterate chronologically given a time interval
        :return:
        """
        for element in self.iterable:
            yield element


if __name__ == '__main__':
    x = Handler('/home/likewise-open/LOCAL/joao.garcia/Workplace/1.INPE/Data/'
                'Radar/BR_PP/2014/')
    x.list_files()
    x.list_dates()
    x.generate_date_tuples("30m", "450s")