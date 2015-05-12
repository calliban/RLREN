# coding: utf-8
"""
This module contains the SteinerHandler class, a subclass of Handler and CAPPI
"""
__docformat__ = 'restructuredtext en'

import os
import sys

import numpy as np

from handler import Handler
from cappi import CAPPI


class SteinerHandler(Handler):
    """
    The SteinerHandler class is a subclass of Handler that deals with the
     Steiner method. While it is almost the same, it implements the iterator
     differently, and also saves the output as a file.
    """
    def __init__(self, city: str, path: str):
        """
        Initialized the SteinerHandler class with a city code and a file path.

        :param path: file path for the radar files
        :param city: city code for a radar
        """
        super().__init__(path)
        self.radar = CAPPI(city)

    def save_steiner(self):
        """
        Save a file as a Steiner file
        """
        old_name = self.radar.file_name + ""
        new_name = old_name.replace("raw.gz", "npy.gz")
        new_name = new_name.replace("Radar", "Steiner")
        np.savetxt(new_name, self.radar.steiner_mask)

    def populate_dirs(self):
        """
        Create a list of directories matching the existing one inside path,
         including subdirectories and stuff. For this, it will replace the
         directory ``Radar``, which must be in filename, with the directory
         ``Steiner``, which will be created if non existing.
        """

        for path, _, _ in os.walk(self.path):
            os.makedirs(path.replace('Radar', 'Steiner'), exist_ok=True)

    def process(self):
        """
        Will iterate over the files and create the respective Steiner filter.
        It will then save the file in the proper directory previously created
         by the ``populate_dirs`` method.
        """

        # Some house-keeping to make sure all conditions for the ``__iter__`` to
        # run are satisfied. The first iteration may take very long, so probably
        # the house-keeping should be explicit.

        self.populate_dirs()
        self.list_files()

        present = 0
        final = len(self.files)

        for file in self.files:
            self.radar.file_name = file
            self.radar.open()
            self.radar.steiner_filter()
            self.save_steiner()

            present += 1
            percentage = (present * 100) // final
            sys.stdout.write("\r%d%% - %s" % (percentage, file))
            sys.stdout.flush()

if __name__ == '__main__':
    x = SteinerHandler('BRU', '/home/likewise-open/LOCAL/joao.garcia/Workplace/'
                              '1.INPE/Data/Radar/')
    x.list_files()
    x.process()