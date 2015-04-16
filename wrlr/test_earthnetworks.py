# coding: utf-8
__docformat__ = 'restructuredtext en'

import pytest

from wrlr import earthnetworks

@pytest.fixture
def data():
    output = earthnetworks.EarthNetworks('BRU')
    return output


def test_read(data):
    assert earthnetworks.cities.cities['BRU'].file_name == 'BRU'


def test_open(data):
    data.open(
        "/home/likewise-open/LOCAL/joao.garcia/Workplace/1.INPE/Data"
        "/Lightning/test.csv")
    assert data.data.keys().tolist() == (['tipo', 'datahora', 'latitude',
                                          'longitude', 'pico_corrente',
                                          'multiplicidade'])

def test_slices(data):
    data._slice(4)
    assert len(data.slices) == 49