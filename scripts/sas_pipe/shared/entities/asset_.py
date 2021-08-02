import sas_pipe.shared.entities.entity_ as entity


class Asset(entity.Entity):
    def __init__(self, path):
        super(Asset, self).__init__(path)
