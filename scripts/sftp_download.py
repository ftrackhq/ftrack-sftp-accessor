import ftrack_api.structure.id
import ftrack_api.accessor.disk
import os

from sftp import SFTPAccessor

"""
Copies a component from a sftp location to a local location
"""
session = ftrack_api.Session()
sftp_location = session.query('Location where name is "studio.sftp"').one()

hostname = os.getenv("FTRACK_SFTP_ACCESSOR_HOSTNAME", None)
port = os.getenv("FTRACK_SFTP_ACCESSOR_PORT", 22)

sftp_location.accessor = SFTPAccessor(
    hostname,
    port=port
)
sftp_location.structure = ftrack_api.structure.standard.StandardStructure()
sftp_location.priority = 30

ftrack_location = session.query('Location where name is "ftrack.connect"').one()
ftrack_location.structure = ftrack_api.structure.standard.StandardStructure()
ftrack_location.accessor = ftrack_api.accessor.disk.DiskAccessor(
    prefix="/Users/ian/ftrack_storage"
)

version = session.get("AssetVersion", "b1ddbf94-6807-4f9f-a404-02298df80bba")

for component in version["components"]:
    if component["name"] == "main":
        ftrack_location.add_component(component, sftp_location)
