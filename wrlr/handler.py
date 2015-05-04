# coding: utf-8
"""
Handle iterating over file lists
"""
__docformat__ = 'restructuredtext en'

import os

import cappi
from datetime import datetime as dt


class Handler(object):
    """
    Handles file-lists and can be used as an iterator in order to get all files
     available in a certain path.
    """

    dates = None
    files = None

    def __init__(self, path: str):
        self.path = path
        self._list_files(self.path)

    def _list_files(self, path: str):
        """
        Lists all visible (i.e. not starting with a dot) files in a directory
         and all its subdirectories, and stores them in alphabetical order,
         which is the same as the date in the name of such files for the scope
         of this work

        :param path: Root path of the files to be handled
        """

        output = []
        for directory, _, files in os.walk(path):
            for f in files:
                if f[0] != '.':
                    file_name = os.path.join(directory, f)
                    output.append(file_name)

        self.files = sorted(output)

    def generate_dates(self):
        """
        This method will try to obtain the date from a file name, which is
         useful specially for radar files.
        """

        dates = []
        for filename in self.files:
            filename = (filename.split('_')[-1]).split('.')[0]  # Date portion
            date = dt.strptime(filename, "%Y%m%d%H%M%S")
            dates.append(date)

        self.dates = dates

    def __next__(self):
        """
        Iterate chronologically given a time interval
        :return:
        """
        pass