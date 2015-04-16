# coding: utf-8
"""
Test for the CAPPI class and related methods
"""
__docformat__ = 'restructuredtext en'

import pytest

from wrlr import cappi


@pytest.fixture
def data():
    rad = cappi.CAPPI('BRU')
    rad.file_name = "/home/likewise-open/LOCAL/joao.garcia/Workplace/1.INPE/Data/Radar/BR_PP/2014/01/RD_203022195_20140112213700.raw.gz"
    return rad


def test_read(data):
    data.open()
    assert (200, 200) == data.data.shape

    data.open(remove_borders=False)
    assert (667, 1000) == data.data.shape

def test_slice(data):
    data.open()
    data._slice(4)
    assert len(data.slices) == 49
