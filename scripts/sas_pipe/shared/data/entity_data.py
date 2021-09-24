import sas_pipe.shared.data.abstract_data as abstract_data


class EntityData(abstract_data.AbstractData):

    def __init__(self):
        """
        constructor for the curve data class
        """
        super(EntityData, self).__init__()

    def add_variant(self, variant, data):
        data["variant"] = True
        self._data[variant] = data


if __name__ == '__main__':
    a = EntityData()
    a.add_variant('damage', 'data')
    print a.getData()
