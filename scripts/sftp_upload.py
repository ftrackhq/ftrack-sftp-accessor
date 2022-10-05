# :coding: utf-8
# :copyright: Copyright (c) 2014-2022 ftrack

import ftrack_api.structure.id
from ftrack_sftp_accessor.sftp import SFTPAccessor
import os


session = ftrack_api.Session()
location = session.query('Location where name is "studio.sftp"').one()

hostname = os.getenv("FTRACK_SFTP_ACCESSOR_HOSTNAME", None)
username = os.getenv("FTRACK_SFTP_ACCESSOR_USERNAME", None)
port = os.getenv("FTRACK_SFTP_ACCESSOR_PORT", 22)

# Setup accessor
location.accessor = SFTPAccessor(hostname, username, port=port)
location.structure = ftrack_api.structure.standard.StandardStructure()
location.priority = 30

version = session.get("AssetVersion", "83b88aa2-b739-4ed1-b840-2ccdac7da271")
version.create_component(
    path="/Users/ian/Downloads/film0001_512kb.mp4", location=location
)
