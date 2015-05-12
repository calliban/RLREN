# coding: utf-8
"""
Test for the Handler class and related methods.
"""
__docformat__ = 'restructuredtext en'

import pytest

import handler


@pytest.fixture
def data():
    output = handler.Handler('/home/likewise-open/LOCAL/joao.garcia/Workplace/'
                             '1.INPE/Data/Radar/BR_PP/2014/06/')
    return output


def test_init(data):
    data.list_files()
    assert len(data.files) > 0


def test_dates(data):
    data.list_files()
    data.list_dates()
    assert data.dates[0].strftime("%Y%m%d%H%M%S") in data.files[0]


def test_generate_date_tuples(data):
    data.list_files()
    data.list_dates()
    data.generate_date_tuples("30m", "450s")
    assert data.iterable is not None