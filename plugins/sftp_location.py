# :coding: utf-8
# :copyright: Copyright (c) 2014-2022 ftrack

import ftrack_api
import ftrack_api.entity.location
import ftrack_api.accessor.disk
import ftrack_api.structure.id
import logging
import os
import sys
import functools

NAME = "ftrack-sftp-accessor"
VERSION = "0.1.0"

logger = logging.getLogger("{}".format(NAME.replace("-", "_")))


def configure_location(event):
    from ftrack_sftp_accessor.sftp import SFTPAccessor

    """Configure locations for session."""
    session = event["data"]["session"]

    # Find location(s) and customise instances.
    location = session.query('Location where name is "studio.sftp"').one()

    hostname = os.getenv("FTRACK_SFTP_ACCESSOR_HOSTNAME", None)
    port = os.getenv("FTRACK_SFTP_ACCESSOR_PORT", 22)
    username = os.getenv("FTRACK_SFTP_ACCESSOR_USERNAME", None)
    password = os.getenv("FTRACK_SFTP_ACCESSOR_PASSWORD", None)
    folder = os.getenv("FTRACK_SFTP_ACCESSOR_FOLDER", None)

    # Setup accessor to use bucket
    location.accessor = SFTPAccessor(
        hostname, username, port=port, password=password, folder=folder
    )
    location.structure = ftrack_api.structure.standard.StandardStructure()
    location.priority = 30

    # Setup any other locations you require
    ftrack_location = session.query('Location where name is "ftrack.connect"').one()
    ftrack_location.structure = ftrack_api.structure.standard.StandardStructure()
    ftrack_location.accessor = ftrack_api.accessor.disk.DiskAccessor(
        prefix="/Users/ian/ftrack_storage"
    )


def register(session):
    if not isinstance(session, ftrack_api.session.Session):
        return

    logging.info("Registering sftp accessor")

    session.event_hub.subscribe(
        "topic=ftrack.api.session.configure-location and source.user.username={}".format(
            session.api_user
        ),
        configure_location,
    )
