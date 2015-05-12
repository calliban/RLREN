# coding: utf-8
"""
Test for the EarthNetworks class and related methods.
"""
__docformat__ = 'restructuredtext en'

import pytest
import cities

import earthnetworks


@pytest.fixture
def data():
    """
    Fixture
    """
    output = earthnetworks.EarthNetworks('BRU')
    return output


def test_city_validity(data):
    """
    Tests if city is being read correctly
    :param data: fixture
    """
    assert cities.cities['BRU'].file_name == 'BRU'


def test_open(data):
    """
    Tests if file is being read correctly
    :param data: fixture
    """
    data.open(
        "/home/likewise-open/LOCAL/joao.garcia/Workplace/1.INPE/Data"
        "/Lightning/test.csv")
    assert data.data.keys().tolist() == (['tipo', 'datahora', 'latitude',
                                          'longitude', 'pico_corrente',
                                          'multiplicidade'])


def test_slices(data):
    """
    Tests if slices are being produced as expected
    :param data: fixture
    """
    data._slice(4)
    assert len(data.slices) == 49