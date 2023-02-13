# ftrack-sftp-accessor

An ftrack sftp [accessor](https://ftrack-python-api.readthedocs.io/en/backlog-threading-story/locations/overview.html?highlight=accessor#accessors). 


**Note**
> To see paths resolved in Studio, the [resolver listener](https://github.com/ftrackhq/ftrack-connect/blob/main/resource/hook/resolver.py) need to be running, either through [ftrack-connect](https://github.com/ftrackhq/ftrack-connect) or manually.

# Installation

Install using pip:

    $ pip install ftrack-sftp-accessor

Install from sources:

    $ git clone https://github.com/ftrackhq/ftrack-sftp-accessor.git
    $ pip install poetry
    $ poetry build
    $ pip install dist/ftrack_sftp_accessor-<VERSION>-py3-none-any.whl


## Documentation

Full documentation, including installation and setup guides can be found at https://ftrack-sftp-accessor.readthedocs.io/en/latest/

## Usage

The main plugin can be found in the plugins folder. This folder may be registered using the FTRACK_EVENT_PLUGIN_PATH ftrack environment variable so that it is picked up when ftrack is started.

Examples of how to use the plugin can be found in the scripts folder. The simplest way to launch ftrack with the accessor is scripts/start_ftrack_with_sftp.py. 

# Contributing

Please refer to the [CONTRIBUTING.md](./CONTRIBUTING.md) 