import sas_pipe.utils.data.abstract_data as abstract_data


class AssetData(abstract_data.AbstractData):

    def __init__(self):
        """
        constructor for the curve data class
        """
        super(AssetData, self).__init__()


if __name__ == '__main__':
    a = EntityData()
    a.add_variant('damage', 'data')
    print a.getData()
