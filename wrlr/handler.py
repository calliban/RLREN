# coding: utf-8
"""
Handle iterating over file lists
"""
__docformat__ = 'restructuredtext en'

import os

import cappi


class Handler(object):
    """
    Handles file-lists and can be used as an iterator in order to get all files
    available in a certain path.
    """

    files = None

    def __init__(self, path: str):
        self.path = path
        self._list_files(self.path)

    def _list_files(self, path: str):
        """
        Lists all non-invisible (i.e. not starting with a dot) files in a
        directory and all its subdirectories, and stores them in alphabetical
        order, which is the same as the date in the name of such files for the
        scope of this work

        :param path:
        """

        output = []
        for directory, _, files in os.walk(path):
            for f in files:
                if f[0] != '.':
                    file_name = os.path.join(directory, f)
                    output.append(file_name)

        self.files = sorted(output)