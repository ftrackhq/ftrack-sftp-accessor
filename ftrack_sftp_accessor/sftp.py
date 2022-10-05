# :coding: utf-8
# :copyright: Copyright (c) 2014-2022 ftrack

import os
import logging
import paramiko

from ftrack_api.accessor.base import Accessor
from ftrack_api.data import FileWrapper
from ftrack_api.exception import (
    AccessorOperationFailedError,
    AccessorUnsupportedOperationError,
    AccessorResourceInvalidError,
    AccessorResourceNotFoundError,
    AccessorContainerNotEmptyError,
    AccessorParentResourceNotFoundError,
)


class SFTPAccessor(Accessor):
    """Provide SFTP location access."""

    def __init__(self, host, username, port=22, password=None, folder=None):
        """Initialise location accessor.

        Uses the server credentials specified by *host*, *password*, *port* and *password*
        to create a sftp connection.

        If specified, *folder* indicates the subfolder where assets are stored
        """
        self._host = host
        self._username = username
        self._password = password
        self._port = port
        self._folder = folder
        self._sftp = None
        self._ssh = None
        self._logger = logging.getLogger(__name__ + "." + self.__class__.__name__)
        super(SFTPAccessor, self).__init__()

    def __deepcopy__(self, memo):
        """Return a new SFTPAccessor instance"""
        return SFTPAccessor(
            self._host, self._username, self._port, self._password, self._folder
        )

    @property
    def ssh(self):
        """Return SSH resource."""
        if self._ssh is None:
            self._logger.debug("Initialising SSH Session")
            self._ssh = paramiko.SSHClient()
            self._ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            if not self._password:
                # attempt to connect using keyfile if no password specified
                self._ssh.connect(
                    self._host,
                    port=self._port,
                )
            else:
                self._ssh.connect(
                    hostname=self._host,
                    port=self._port,
                    username=self._username,
                    password=self._password,
                )
        return self._ssh

    @property
    def sftp(self):
        """Return SFTP resource."""
        self._logger.debug("Initialising SFTP Session")
        if self._sftp is None:
            self._sftp = self.ssh.open_sftp()

            if self._folder is not None:
                self._sftp.chdir(self._folder)

        return self._sftp

    def list(self, resource_identifier):
        """Return list of entries in *resource_identifier* container.

        Each entry in the returned list should be a valid resource identifier.

        Raise :py:class:`~ftrack.ftrackerror.AccessorResourceNotFoundError` if
        *resource_identifier* does not exist or
        :py:class:`~ftrack.ftrackerror.AccessorResourceInvalidError` if
        *resource_identifier* is not a container.

        """
        if not resource_identifier.endswith("/"):
            resource_identifier += "/"

        if resource_identifier == "/":
            resource_identifier = ""

        try:
            self.sftp.stat(resource_identifier)
            return self.sftp.listdir(resource_identifier)
        except IOError:
            self._logger.debug(
                f"Returning an empty list as resource identifier {resource_identifier} doesn't exist"
            )
            return []

    def exists(self, resource_identifier):
        """Return if *resource_identifier* is valid and exists in location."""
        # Root directory always exists
        if not resource_identifier:
            return True

        return self.is_container(resource_identifier) or self.is_file(
            resource_identifier
        )

    def is_file(self, resource_identifier):
        """Return whether *resource_identifier* refers to a file."""
        # Root is a directory
        if not resource_identifier:
            return False

        resource_identifier = resource_identifier.rstrip("/")

        try:
            file_object = self.sftp.stat(resource_identifier)
        except IOError:
            self._logger.debug(
                f"Returning is not file as resource identifier {resource_identifier} doesn't exist"
            )
            file_object = None
        except Exception as error:
            raise AccessorOperationFailedError(
                operation="is_file",
                resource_identifier=resource_identifier,
                error=error,
            )

        return file_object is not None

    def is_container(self, resource_identifier):
        """Return whether *resource_identifier* refers to a container."""
        # Root is a directory
        if not resource_identifier:
            return True

        file_objects = self.list(resource_identifier)

        try:
            next(iter(file_objects))
        except StopIteration:
            return False
        else:
            return True

    def is_sequence(self, resource_identifier):
        """Return whether *resource_identifier* refers to a file sequence."""
        raise AccessorUnsupportedOperationError("is_sequence")

    def open(self, resource_identifier, mode="rb"):
        """Return :py:class:`~ftrack.Data` for *resource_identifier*."""
        if self.is_container(resource_identifier):
            raise AccessorResourceInvalidError(
                resource_identifier=resource_identifier,
                message="Cannot open a directory: {resource_identifier}",
            )

        try:
            file_obj = self.sftp.open(resource_identifier, mode)
        except IOError:
            self._logger.debug(f"Creating SFTP Resource {resource_identifier}")
            if "w" not in mode and "a" not in mode:
                raise AccessorResourceNotFoundError(
                    resource_identifier=resource_identifier
                )

            self.ssh.exec_command(f"touch {resource_identifier}")
            file_obj = self.sftp.open(resource_identifier, mode)

        if "w" in mode:
            file_obj = self.sftp.open(resource_identifier, mode)

        return FileWrapper(file_obj)

    def remove(self, resource_identifier):
        """Remove *resource_identifier*.

        Raise :py:class:`~ftrack.ftrackerror.AccessorResourceNotFoundError` if
        *resource_identifier* does not exist.

        """
        self._logger.debug(f"Removing SFTP Resource {resource_identifier}")
        if self.is_file(resource_identifier):
            self.sftp.remove(resource_identifier)

        elif self.is_container(resource_identifier):
            contents = self.list(resource_identifier)
            if contents:
                raise AccessorContainerNotEmptyError(
                    resource_identifier=resource_identifier
                )

            self.sftp.remove(resource_identifier + "/")

        else:
            raise AccessorResourceNotFoundError(resource_identifier=resource_identifier)

    def get_container(self, resource_identifier):
        """Return resource_identifier of container for *resource_identifier*.

        Raise
        :py:class:`~ftrack.ftrackerror.AccessorParentResourceNotFoundError` if
        container of *resource_identifier* could not be determined.

        """
        if os.path.normpath(resource_identifier) in ("/", ""):
            raise AccessorParentResourceNotFoundError(
                resource_identifier=resource_identifier,
                message="Could not determine container for "
                "{resource_identifier} as it is the root.",
            )

        return os.path.dirname(resource_identifier.rstrip("/"))

    def make_container(self, resource_identifier, recursive=True):
        """Make a container at *resource_identifier*.

        If *recursive* is True, also make any intermediate containers.

        """
        if not resource_identifier:
            # Root directory
            return

        if not resource_identifier.endswith("/"):
            resource_identifier += "/"

        if self.exists(resource_identifier):
            if self.is_file(resource_identifier):
                raise AccessorResourceInvalidError(
                    resource_identifier=resource_identifier,
                    message=("Resource {resource_identifier} already exists as a file"),
                )

            else:
                return

        parent = self.get_container(resource_identifier)

        if not self.is_container(parent):
            if recursive:
                self.make_container(parent, recursive=recursive)
            else:
                raise AccessorParentResourceNotFoundError(resource_identifier=parent)

        self.sftp.mkdir(resource_identifier)

    def get_url(self, resource_identifier=None):
        """Return url for *resource_identifier*."""

        if self._folder:
            return (
                f"sftp://{self._host}:{self._port}/{self._folder}/{resource_identifier}"
            )
        return f"sftp://{self._host}:{self._port}/{resource_identifier}"
