# coding: utf-8
"""
This file is intended to be used as a main script. It's intended to read and
 process all set files.
"""
__docformat__ = 'restructuredtext en'

from earthnetworks import EarthNetworks
from cappi import CAPPI
from handler import Handler
from sys import argv


def main():
    #city = argv[1]
    city = 'BRU'
    if city == 'BRU' or city == 'PPR':
        city_name = "BR_PP"
    radar_path = "/home/likewise-open/LOCAL/joao.garcia/Workplace/1.INPE/Data/Radar/%s/" % city_name
    flash_path = "/home/likewise-open/LOCAL/joao.garcia/Workplace/1.INPE/Data/Lightning/flash.csv"
    pulse_path = "/home/likewise-open/LOCAL/joao.garcia/Workplace/1.INPE/Data/Lightning/pulse.csv"

    rad = CAPPI(city)
    flash = EarthNetworks(city)
    flash.open(flash_path)
    pulse = EarthNetworks(city)
    pulse.open(pulse_path)

    handler = Handler(radar_path)
    handler.list_files()
    handler.list_dates()
    handler.generate_date_tuples("30m", "450s")


if __name__ == '__main__':
    main()