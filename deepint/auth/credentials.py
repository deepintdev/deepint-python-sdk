#!usr/bin/python

# Copyright 2021 Deep Intelligence
# See LICENSE for details.

import os
import configparser
from ..error import DeepintCredentialsError


class Credentials:
    """Loads credentials (token), and manages it during runtime.
    
    This class must not be instantiated directly, but the :obj:`deepint_sdk.auth.Credentials.build` 
    method must be used. Due to this fact, for details on how to provide the access token, see the 
    :obj:`deepint_sdk.auth.Credentials.build` method.

    Attributes:
        token: Token to access the deepint.net API that must be used to authenticate each transaction.
    """

    def __init__(self, token: str) -> None:
        self.token = token

    @classmethod
    def build(cls, token: str = None) -> 'Credentials':
        """Instances a :obj:`deepint_sdk.auth.Credentials` with one of the provided methods.
        
        The priority of credentials loading is the following:
            - if the token is provided as a parameter, this one is used.
            - then the token is tried to be extracted from the environment variable ```DEEPINT_TOKEN```.
            - then the token is tried to be extracted from the file ```~/.deepint.ini``` located in the user's directory.

        If the token is not provided in any of these ways, an :obj:`deepint_sdk.error.DeepintCredentialsError` will be thrown.
        
        Example:
            [DEFAULT]
            token=a token

        Args:
            token : Token to access the deepint.net API that must be used to authenticate each transaction.

        Returns:
            An instanced credentials object.
        """

        if token is None:
            for f in [cls._load_env, cls._load_home_file]:
                token = f()
                if token is not None:
                    break
        if token is None:
            raise DeepintCredentialsError()

        cred = Credentials(token=token)

        return cred

    @classmethod
    def _load_env(cls) -> str:
        """Loads the token value from the environment variable ```DEEPINT_TOKEN```
        
        Returns:
            The value of the ```DEEPINT_TOKEN``` environment variable. If the variable is not declared in environment, the retrieved value will be None, otherwise will be the token stored in that variable.
        """

        return os.environ.get('DEEPINT_TOKEN')

    @classmethod
    def _load_home_file(cls) -> str:
        """Loads the token value from the file located in the user's home directory.
        
        The file loaded is the one located in ```~/.deepint.ini```, and must be a .ini file with the following format:

        Example:
            [DEFAULT]
            token=a token

        Returns:
            The value of the ```DEEPINT_TOKEN``` environment variable. If the variable is not declared in environment, the retrieved value will be None, otherwise will be the token stored in that variable.
        """

        home_folder = os.path.expanduser("~")
        credentials_file = f'{home_folder}/.deepint.ini'

        if not os.path.isfile(credentials_file):
            return None
        else:
            config = configparser.ConfigParser()
            config.read(credentials_file)

            try:
                token = config['DEFAULT']['token']
            except:
                token = None

            return token

    def update_credentials(self, token: str) -> None:
        """Updates the token value.
        
        Alternative of updating directly the token value accessing the attribute :obj:`deepint_sdk.auth.Credentials.token`.

        Args:
            token: token to replace current token stored in :obj:`deepint_sdk.auth.Credentials.token`.
        """

        self.token = token
