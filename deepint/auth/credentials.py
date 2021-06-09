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
        organization: Id of the organization to access the deepint.net API that must be used to authenticate each transaction.
    """

    def __init__(self, token: str, organization: str) -> None:
        self.token = token
        self.organization = organization

    @classmethod
    def build(cls, token: str = None, organization: str = None) -> 'Credentials':
        """Instances a :obj:`deepint_sdk.auth.Credentials` with one of the provided methods.
        
        The priority of credentials loading is the following:
            - if the credentials are provided as a parameter, this one is used.
            - then the credentials are tried to be extracted from the environment variable ```DEEPINT_TOKEN```.
            - then the credentials are tried to be extracted from the file ```~/.deepint.ini``` located in the user's directory.

        If the token is not provided in any of these ways, an :obj:`deepint_sdk.error.DeepintCredentialsError` will be thrown.
        
        Example:
            [DEFAULT]
            token=a token
            organiztion= a organization

        Args:
            token : Token to access the deepint.net API that must be used to authenticate each transaction.
            organization: Id of the organization to access the deepint.net API that must be used to authenticate each transaction.

        Returns:
            An instanced credentials object.
        """

        if token is None or organization is None:
            for f in [cls._load_env, cls._load_home_file]:
                token, organization = f()
                if token is not None and organization is not None:
                    break
        if token is None or organization is None:
            raise DeepintCredentialsError()

        cred = Credentials(token=token, organization=organization)

        return cred

    @classmethod
    def _load_env(cls) -> tuple:
        """Loads the credentials values from the environment variables ```DEEPINT_TOKEN``` and ```DEEPINT_ORGANIZATION```
        
        Returns:
            The value of the ```DEEPINT_TOKEN``` and ```DEEPINT_ORGANIZATION``` environment variables. If the any of the variables is not declared in environment, the retrieved value will be None, otherwise will be the value stored in that variable.
        """

        return os.environ.get('DEEPINT_TOKEN'), os.environ.get('DEEPINT_ORGANIZATION') 

    @classmethod
    def _load_home_file(cls) -> tuple:
        """Loads the credentials values from the file located in the user's home directory.
        
        The file loaded is the one located in ```~/.deepint.ini```, and must be a .ini file with the following format:

        Example:
            [DEFAULT]
            token=a token
            organiztion= a organization

        Returns:
            The value of the token and organization stored in the file.
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
                organization = config['DEFAULT']['organization']
            except:
                token = None
                organization = None

            return token, organization

    def update_credentials(self, token: str, organization: str) -> None:
        """Updates the token value.
        
        Alternative of updating directly the token value accessing the attribute :obj:`deepint_sdk.auth.Credentials.token`.

        Args:
            token: token to replace current token stored in :obj:`deepint_sdk.auth.Credentials.token`.
            organization: Id of the organization to access the deepint.net API that must be used to authenticate each transaction.
        """

        self.token = token
        self.organization = organization
