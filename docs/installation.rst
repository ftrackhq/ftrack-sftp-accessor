.. _installation:

************
Installation
************

.. highlight:: bash

This accessor is designed to be used as a single install studio wide. This negates the need to have it installed in every instance of ftrack-connect used in your studio. You'll first need a sftp server configured where you can successfully log in and make transfers.

The easiest way to install is within a virtual environment using your package manager of choice::
    
    pip install ftrack-sftp-accessor

Alternatively, download this repo and install it's dependencies. 

*************
Configuration
*************

Configure a new location within ftrack with the name 'studio.sftp'. This will be used as the location for sftp transfers.

Set all other ftrack environment variables for your ftrack instance.

Running the example scripts from within your environment requires you to additionally set your sources root to the accessor directory::

    PYTHONPATH=./ftrack_sftp_accessor

**********
Usage
**********

.. highlight:: python

Setting up the accessor for the sftp location is done like so::

    session = ftrack_api.Session()
    location = session.query('Location where name is "studio.sftp"').one()

    hostname = os.getenv("FTRACK_SFTP_ACCESSOR_HOSTNAME", None)
    port = os.getenv("FTRACK_SFTP_ACCESSOR_PORT", 22)

    location.accessor = SFTPAccessor(
        hostname,
        port=port
    )
    location.structure = ftrack_api.structure.standard.StandardStructure()
    location.priority = 30

.. highlight:: bash

Several environment variables are used to configure the plugin::

    FTRACK_SFTP_ACCESSOR_HOSTNAME=<your_sftp_host>
    FTRACK_SFTP_ACCESSOR_PORT=22

For an install managed entirely by local ssh keys, where you're able to authenticate successfully without specifying a username/password combination each time, this will be enough for the plugin to make transfers.

Alternatively, you can specify a username and password like so::

    FTRACK_SFTP_ACCESSOR_USERNAME=user
    FTRACK_SFTP_ACCESSOR_PASSWORD=**********

.. highlight:: python

And then in your plugin::

    location = session.query('Location where name is "studio.sftp"').one()
    hostname = os.getenv("FTRACK_SFTP_ACCESSOR_HOSTNAME", None)
    port = os.getenv("FTRACK_SFTP_ACCESSOR_PORT", 22)
    username = os.getenv("FTRACK_SFTP_ACCESSOR_USERNAME", None)
    password = os.getenv("FTRACK_SFTP_ACCESSOR_PASSWORD", None)

    location.accessor = SFTPAccessor(hostname, username, port=port, password=password)

Uploading Components
====================

When running the accessor outside of ftrack-connect, you will need to ensure your local storage is also correctly configured within a script, as the connect location configured by the desktop client will not be available as an option::
    
    ftrack_location = session.query('Location where name is "ftrack.connect"').one()
    ftrack_location.structure = ftrack_api.structure.standard.StandardStructure()
    ftrack_location.accessor = ftrack_api.accessor.disk.DiskAccessor(
        prefix="/path/to/ftrack_storage"
    )

To upload a component to an AssetVersion, lookup the version and create a component at the new location::

    version = session.get("AssetVersion", "87d07110-962b-11ea-8647-927195c3dfa3")
    version.create_component(
        path="/path/to/file/upload.mp4", location=location
    )

Downloading Components
======================

To download a component, lookup the component required and transfer it from ftrack to your sftp location::

    version = session.get("AssetVersion", "b1ddbf94-6807-4f9f-a404-02298df80bba")

    for component in version["components"]:
        if component["name"] == "main":
            ftrack_location.add_component(component, sftp_location)

Transfer Component Action
=========================

.. highlight:: bash

Optionally, to ease transfer of components between locations via the ftrack interface, it is possible to use the transfer components action found `here <https://bitbucket.org/!api/2.0/snippets/ftrack/B6dX/f9e89e8bf95065a6fc0541dd058863ff1ddaceb6/files/transfer_components_action.py>`_. 

Install the transfer component action in your plugin folder and you'll need to additionally install the action handler it depends upon::
 
    pip install ftrack-action-handler

Once installed, ensure both plugins are on the FTRACK_EVENT_PLUGIN_PATH (or add them to your plugins folder) and the transfer components plugin should become available under ftracks action menu. 
