"""

"""


def add_show(root, show_name):
    """
    Add a new show
    :param root: of the project
    :param show_name: name of the show to add
    """
    return os_util.create_directory(os.path.join(os.path.join(self.shows_path, show_name.upper())))


def add_asset(self, asset, type):
    """
    Create new asset
    :param asset: name of the asset
    :type asset: str

    :param type: asset type
    :type type: str

    :returns: path to asset
    :rtype: str
    """
    for mode in [True, False]:
        path = self.__build_asset_path(type=type, rel=mode, asset=asset)
        if not os.path.exists(path):
            os_util.create_directory(path)
            Logger.info('New asset: {} created with type {}'.format(asset, type))
            for task in show_settings.ShowSettings.get_data('asset_tasks'):
                os_util.create_directory(os.path.join(path, task))
        else:
            Logger.warning("Asset '{}' already exists in show {}".format(asset, self.current_show))


def add_sequence(self, sequence, type):
    """
    Create new sequence
    :param sequence: sequence to create
    :type sequence: str

    :param type: sequence type
    :type type: str

    :returns: path to sequence
    :rtype: str
    """
    for mode in [True, False]:
        path = self.__build_seq_path(sequence=sequence, type=type, rel=mode)
        if not os.path.exists(path):
            Logger.info('New sequence: {} created with type {}'.format(sequence, type))
            os_util.create_directory(os.path.join(path))
        else:
            Logger.warning("Sequence '{}' already exists in show {}".format(sequence, self.current_show))


def add_shot(self, shot, sequence, type=None):
    """
    Create new shot
    :param shot: name of the asset
    :type shot: str

    :param sequence: sequence to put the shot in
    :type sequence: str

    :param type: type of sequence
    :type type: str
    """
    for mode in [True, False]:
        path = self.__build_shot_path(sequence=sequence, type=type, shot=shot, rel=mode)
        if not os.path.exists(path):
            Logger.info('New shot: {} created under sequence {}/{}'.format(shot, type, sequence))
            for task in show_settings.ShowSettings.get_data('shot_tasks'):
                os_util.create_directory(os.path.join(path, task))
        else:
            Logger.warning("Shot '{}/{}' already exists in show {}".format(sequence, shot, self.current_show))


def get_shows(self, base_only=False):
    """
    :param base_only: get the full path of an object
    :type base_only: bool

    :return: Return a items of all shows
    :rtype: list
    """
    return os_util.get_many(self.shows_path, base_only=base_only)


def get_show(self, show, base_only=False):
    """
    Get the path of a specific show
    :param show:
    :param base_only:
    :return:
    """
    return os_util.get_one(show, self.get_shows(base_only=True), base_only=base_only)


def get_depts(self, base_only=False):
    """
    :param base_only: get the full path of an object
    :type base_only: bool

    :return: Return a items of all departments
    :rtype: list
    """
    return os_util.get_many(self.depts_path, base_only=base_only)


def get_assets(self, type=None, rel=False, base_only=False):
    """
    List all assets. If a type is provided get only assets of that type
    :param type: Optional - Asset type to return.
    :type type: str

    :param rel: If True will items assets in release path. False will return assets in the working path
    :type rel: bool

    :param base_only: get the full path of an object
    :type base_only: bool

    :return: List of assets
    :rtype: list
    """
    result = list()
    if type:
        result.extend(os_util.get_many(self.__build_asset_path(type=type, rel=rel), base_only=base_only))
    else:
        for type in show_settings.ShowSettings.get_data('asset_types'):
            result.extend(os_util.get_many(self.__build_asset_path(type=type, rel=rel), base_only=base_only))

    return sorted(result)


def get_sequences(self, type=None, rel=False, base_only=False):
    """
    List all Sequences. If a type is provided get only sequences of that type
    :param type: Optional - Sequence type to return.
    :type type: str

    :param rel: If True will items sequences in release path. False will return sequences in the working path
    :type rel: bool

    :param base_only: get the full path of an object
    :type base_only: bool

    :return: List of sequences
    :rtype: list
    """
    result = list()
    if type:
        result.extend(os_util.get_many(self.__build_seq_path(type=type, rel=rel), base_only=base_only))
    else:
        for type in show_settings.ShowSettings.get_data('sequence_types'):
            result.extend(os_util.get_many(self.__build_seq_path(type=type, rel=rel), base_only=base_only))
    return sorted(result)


def get_shots(self, sequence, type=None, rel=False, base_only=False):
    """
    List all Shots in a sequence.
    :param sequence: Sequence to get shots from
    :type sequence: str

     :param type: type of sequence
     :type type: str

    :param rel: If True will items shots in release path. False will return shots in the working path
    :type rel: bool

    :return: List of shots
    :rtype: list

    :param base_only: get the  path of an object
    :type base_only: bool
    """
    result = list()
    path = self.__build_shot_path(sequence=sequence, type=type, rel=rel)
    if path:
        result.extend(
            os_util.get_many(self.__build_shot_path(sequence=sequence, type=type, rel=rel), base_only=base_only))
    return sorted(result)


def find_sequence(self, sequence, type=None, rel=False, base_only=False):
    """
    Get a specicific sequence based on sequence name
    :param sequence: sequence to get
    :type sequence: str

    :param type: Optional - Sequence type to return.
    :type type: str

    :param rel: If True will items sequences in release path. False will return sequences in the working path
    :type rel: bool

    :param base_only: get the full path of an object
    :type base_only: bool

    :return: path to sequence
    :rtype: list
    """
    result = list()
    if type:
        result.extend(os_util.get_one(sequence, self.__build_seq_path(type=type, rel=rel), base_only=base_only))
    else:
        for type in show_settings.ShowSettings.get_data('sequence_types'):
            result.extend(os_util.get_one(sequence, self.__build_seq_path(type=type, rel=rel), base_only=base_only))

    if len(result) > 0:
        return sequence_.Sequence(common.getFirstIndex(result))
    else:
        return None


def find_shot(self, shot, sequence, type=None, rel=False, base_only=False):
    """
    :param shot: name of the shot to get
    :type shot: str

    :param sequence: Sequence to get shots from
    :type sequence: str

    :param type: type of sequence
    :type type: str

    :param rel: If True will items sequences in release path. False will return sequences in the working path
    :type rel: bool

    :param base_only: get the full path of an object
    :type base_only: bool

    :return: path to sequence
    :rtype: list
    """
    result = list()
    path = self.__build_shot_path(sequence=sequence, type=type, rel=rel)
    if path:
        result.extend(
            os_util.get_one(shot, self.__build_shot_path(sequence=sequence, type=type, rel=rel),
                            base_only=base_only))

    if len(result) > 0:
        return shot_.Shot(common.getFirstIndex(result))
    else:
        return None


def find_asset(self, asset=None, type=None, rel=False, base_only=False):
    """
    Get a specific asset based on name
    :param asset: Asset to get
    :type asset: str

    :param type: Optional - type of the asset. May be required if multiple assets have the same name
    :type type: str

    :param rel: If True will items assets in release path. False will return assets in the working path
    :type rel: bool

    :param base_only: get the full path of an object
    :type base_only: bool

    :return:
    """
    result = list()
    if type:
        result.extend(os_util.get_one(asset, self.__build_asset_path(type=type, rel=rel), base_only=base_only))
    else:
        for type in show_settings.ShowSettings.get_data('asset_types'):
            result.extend(os_util.get_one(asset, self.__build_asset_path(type=type, rel=rel), base_only=base_only))
    if len(result) > 0:
        return asset_.Asset(common.getFirstIndex(result))
    else:
        return None
