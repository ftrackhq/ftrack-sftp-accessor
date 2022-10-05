# :coding: utf-8
# :copyright: Copyright (c) 2014-2022 ftrack

import ftrack_api.structure.id
import ftrack_api.accessor.disk
import os

from ftrack_sftp_accessor.sftp import SFTPAccessor

"""
Copies a component from a sftp location to a local location
"""
session = ftrack_api.Session()
sftp_location = session.ensure("Location", {"name": "studio.sftp"})

hostname = os.getenv("FTRACK_SFTP_ACCESSOR_HOSTNAME", None)
username = os.getenv("FTRACK_SFTP_ACCESSOR_USERNAME", None)
port = os.getenv("FTRACK_SFTP_ACCESSOR_PORT", 22)
folder = os.getenv("FTRACK_SFTP_ACCESSOR_FOLDER", "ftrack")

sftp_location.accessor = SFTPAccessor(hostname, username, port=port, folder=folder)
sftp_location.structure = ftrack_api.structure.standard.StandardStructure()
sftp_location.priority = 30

ftrack_location = session.ensure("Location", {"name": "ftrack.connect"})
ftrack_location.structure = ftrack_api.structure.standard.StandardStructure()
ftrack_location.accessor = ftrack_api.accessor.disk.DiskAccessor(
    prefix="/Users/ian/ftrack_storage"
)

version = session.get("AssetVersion", "9d5d86b7-46b5-49fc-993c-03ce885a6950")

for component in version["components"]:
    if component["name"] == "main":
        ftrack_location.add_component(component, sftp_location)
