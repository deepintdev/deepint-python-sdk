#!usr/bin/python

# Copyright 2023 Deep Intelligence
# See LICENSE for details.

import configparser
import os

from ..error import DeepintCredentialsError

DEFAULT_INSTANCE = 'app.air-core.io'
"""Hostname of the AIR-Core SaaS instance, used when no instance is configured."""

TOKEN_ENV_VARS = ('AIRCORE_TOKEN', 'DEEPINT_TOKEN')
"""Environment variables read for the token, in order of precedence."""

INSTANCE_ENV_VARS = ('AIRCORE_INSTANCE', 'DEEPINT_INSTANCE')
"""Environment variables read for the instance, in order of precedence."""


def _first_env(names):
    for name in names:
        value = os.environ.get(name)
        if value is not None:
            return value
    return None


class Credentials:
    """Loads credentials (token), and manages it during runtime.

    This class must not be instantiated directly, but the :obj:`deepint_sdk.auth.Credentials.build`
    method must be used. Due to this fact, for details on how to provide the access token, see the
    :obj:`deepint_sdk.auth.Credentials.build` method.

    Attributes:
        token: Token to access the AIR-Core API that must be used to authenticate each transaction.
        instance : Host to connect with. By default is the hostname of the SaaS instance, however if you are working with an on-premise instance, this must be specified.
    """

    def __init__(self, token: str, instance: str = DEFAULT_INSTANCE) -> None:

        if not isinstance(token, str):
            raise ValueError('token must be str')

        if not isinstance(instance, str):
            raise ValueError('instance must be str')

        self.token = token
        self.instance = instance

    @classmethod
    def build(cls, token: str = None, instance: str = DEFAULT_INSTANCE) -> 'Credentials':
        """Instances a :obj:`deepint_sdk.auth.Credentials` with one of the provided methods.

        The priority of credentials loading is the following:
            - if the credentials are provided as a parameter, this one is used.
            - then the credentials are tried to be extracted from the environment variables ```AIRCORE_TOKEN``` and ```AIRCORE_INSTANCE```
              (the legacy ```DEEPINT_TOKEN``` and ```DEEPINT_INSTANCE``` variables are still supported and used when the ```AIRCORE_*``` ones are not set).
            - then the credentials are tried to be extracted from the file ```~/.deepint.ini``` located in the user's directory.

        If the token is not provided in any of these ways, an :obj:`deepint_sdk.error.DeepintCredentialsError` will be thrown.

        Example:
            [DEFAULT]
            token=a token
            instance=host to connect with (if not providen app.air-core.io will be taken by default)

        Args:
            token : Token to access the AIR-Core API that must be used to authenticate each transaction.
            instance : Host to connect with. By default is the hostname of the SaaS instance, however if you are working with an on-premise instance, this must be specified.

        Returns:
            An instanced credentials object.
        """

        if token is None or instance is None:
            for f in [cls._load_env, cls._load_home_file]:
                token, instance = f()
                if token is not None and instance is not None:
                    break

        if token is None:
            raise DeepintCredentialsError()

        cred = Credentials(token=token, instance=instance)

        return cred

    @classmethod
    def _load_env(cls) -> tuple:
        """Loads the credentials values from the environment variables.

        The token is read from ```AIRCORE_TOKEN``` and, if it is not set, from the legacy ```DEEPINT_TOKEN```.
        The instance is read from ```AIRCORE_INSTANCE``` and, if it is not set, from the legacy ```DEEPINT_INSTANCE```.

        Returns:
            A tuple with the token and the instance. The token is None if none of the token variables is declared.
            The instance defaults to the SaaS instance hostname, app.air-core.io, if none of the instance variables is declared.
        """

        return _first_env(TOKEN_ENV_VARS), _first_env(INSTANCE_ENV_VARS) or DEFAULT_INSTANCE

    @classmethod
    def _load_home_file(cls) -> tuple:
        """Loads the credentials values from the file located in the user's home directory.

        The file loaded is the one located in ```~/.deepint.ini```, and must be a .ini file with the following format:

        Example:
            [DEFAULT]
            token=a token
            instance=host to connect with (if not providen app.air-core.io will be taken by default)

        Returns:
            The value of the token stored in the file.
        """

        home_folder = os.path.expanduser("~")
        credentials_file = f'{home_folder}/.deepint.ini'

        if not os.path.isfile(credentials_file):
            return None, None
        else:
            config = configparser.ConfigParser()
            config.read(credentials_file)

            try:
                token = config['DEFAULT'].get('token', None)
            except:
                token = None

            try:
                instance = config['DEFAULT'].get('instance', DEFAULT_INSTANCE)
            except:
                instance = None

            return token, instance

    def update_credentials(self, token: str, instance: str) -> None:
        """Updates the token value.

        Alternative of updating directly the token value accessing the attribute :obj:`deepint_sdk.auth.Credentials.token`.

        Args:
            token: token to replace current token stored in :obj:`deepint_sdk.auth.Credentials.token`.
            instance : Host to connect with. By default is the hostname of the SaaS instance, however if you are working with an on-premise instance, this must be specified.
        """

        self.token = token
        self.instance = instance
