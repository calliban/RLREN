# coding: utf-8
"""
This is a clustering class
"""
__docformat__ = 'restructuredtext en'

import pandas as pd


class Cluster():
    data = None

    def __init__(self, path):
        self.open(path)

    def open(self, file_name: str):
        """
        Read a single lightning file given it's full file path and file_name.
        Saves it as a pandas.DataFrame where:
        * tipo: either 'CG' for Cloud-to-Ground or 'IC' for intracloud;
        * datahora: a date-time timestamp;
        * latitude: the latitude of the occurrence as a float;
        * longitude: the longitude of the occurrence as a float;
        * pico_corrente: either '+' for positive or '-' for negative polarity,
            with no-polarity converted to '+';
        * multiplicidade: number of strokes for each occurrence;

        :param file_name: the full path for a lightning file
        """
        data = pd.read_csv(file_name, sep=';', index_col='id',)
        data.drop(('geom'), axis=1, inplace=True)

        data['datahora'] = pd.to_datetime(data['datahora'])

        # ToDo remove this test here
        data = data[("2014-03-01" <= data.datahora) & (data.datahora < "2014-04-01")]

        # Reduce to valid intervals only
        self.data = data

if __name__ == '__main__':
    output = Cluster("/home/likewise-open/LOCAL/joao.garcia/Workplace/1.INPE/Data/Lightning/pulse.csv")
    print(output.data.head())