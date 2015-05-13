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

    data.open_steiner()
    assert (667, 1000) == data.steiner_mask.shape

    data.remove_borders()
    assert (200, 200) == data.data.shape
    assert (200, 200) == data.steiner_mask.shape


def test_slice(data):
    """
    Test if slices are being generated correctly
    :param data: fixture
    """
    data.open()
    data.remove_borders()
    data._slice(4)
    assert len(data.slices) == 49


@pytest.fixture
def roque():
    """
    Fixture object for CAPPI radar data
    """
    rad = cappi.CAPPI('PI')
    rad.file_name = "/home/likewise-open/LOCAL/joao.garcia/Workplace/1.INPE/Data/Radar/PC/2014/01/RD_202082071_20140101000100.raw.gz"
    return rad


def test_read(roque):
    """
    Test if files can be read as normal
    :param data: fixture
    """
    roque.open()
    assert (500, 500) == roque.data.shape

    roque.open_steiner()
    assert (500, 500) == roque.steiner_mask.shape

    roque.remove_borders()
    assert (200, 200) == roque.data.shape
    assert (200, 200) == roque.steiner_mask.shape

