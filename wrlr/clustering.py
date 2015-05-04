# coding: utf-8
"""
This is a clustering class
"""
__docformat__ = 'restructuredtext en'

import pandas as pd
from geopy.distance import distance


class Cluster():
    data = None
    clusters = None

    def __init__(self, path, delta_x=10, delta_t=5):
        self.delta_x = delta_x
        self.delta_t = delta_t
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
        data = pd.read_csv(file_name, sep=';', index_col='id', )
        data.drop(['geom'], axis=1, inplace=True)

        data['datahora'] = pd.to_datetime(data['datahora'])


        #TODO remove this
        data = data[data.index < data.index.min() + 100]
        # Reduce to valid intervals only
        self.data = data

    @profile
    def get_cluster(self, index):
        """
        Create the cluster based on a single lightning occurrence
        :param index:
        :return:
        """
        lightning = self.data.loc[index]
        time_delta = lightning.datahora + pd.to_timedelta(
            "%imin" % self.delta_t)
        lat_min = lightning.latitude - self.delta_x
        lat_max = lightning.latitude + self.delta_x
        lon_min = lightning.longitude - self.delta_x
        lon_max = lightning.longitude + self.delta_x

        tmp_data = self.data[self.data.datahora >= lightning.datahora]
        tmp_data = tmp_data[tmp_data.datahora <= time_delta]
        tmp_data = tmp_data[tmp_data.latitude >= lat_min]
        tmp_data = tmp_data[tmp_data.latitude <= lat_max]
        tmp_data = tmp_data[tmp_data.longitude >= lon_min]
        tmp_data = tmp_data[tmp_data.longitude <= lon_max]

        truth = []
        for _, row in tmp_data.iterrows():
            coord1 = (row.latitude, row.longitude)
            coord2 = (lightning.latitude, lightning.longitude)
            if distance(coord1, coord2).km <= self.delta_x:
                truth.append(True)
            else:
                truth.append(False)
        tmp_data = tmp_data[truth]

        return [tmp_data.index.tolist()]

    def create_clusters(self):
        """
        Create a list of all lightning clusters
        """

        self.clusters = {index: self.get_cluster(index)
                         for index, _ in self.data.iterrows()}


if __name__ == '__main__':
    output = Cluster(
        "/home/likewise-open/LOCAL/joao.garcia/Workplace/1.INPE/Data/Lightning/flash.csv")
    output.create_clusters()
