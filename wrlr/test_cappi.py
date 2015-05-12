# coding: utf-8
"""
Test for the CAPPI class and related methods.
"""
__docformat__ = 'restructuredtext en'

import pytest

import cappi

@pytest.fixture
def data():
    """
    Fixture object for CAPPI radar data
    """
    rad = cappi.CAPPI('BRU')
    rad.file_name = "/home/likewise-open/LOCAL/joao.garcia/Workplace/1.INPE/Data/Radar/BR_PP/2014/01/RD_203022195_20140112213700.raw.gz"
    return rad


def test_read(data):
    """
    Test if files can be read as normal
    :param data: fixture
    """
    data.open()
    assert (667, 1000) == data.data.shape

    data.remove_borders()
    assert (200, 200) == data.data.shape


def test_slice(data):
    """
    Test if slices are being generated correctly
    :param data: fixture
    """
    data.open()
    data.remove_borders()
    data._slice(4)
    assert len(data.slices) == 49
