# coding: utf-8
__docformat__ = 'restructuredtext en'

import pytest

from wrlr import handler


@pytest.fixture
def data():
    output = handler.Handler('/home/likewise-open/LOCAL/joao.garcia/Workplace/1.INPE/Data/Radar/BR_PP/2014/06/')
    return output


def test_init(data):
    assert len(data.files) > 0


def test_dates(data):
    data.generate_dates()
    assert data.dates[0].strftime("%Y%m%d%H%M%S") in data.files[0]