#!usr/bin/python

# Copyright 2021 Deep Intelligence
# See LICENSE for details.

from typing import Any, List, Dict, Optional, Generator

from .workspace import Workspace
from ..auth import Credentials
from ..util import handle_request, parse_date, parse_url


class OrganizationWorkspaces:
    """Operates over the worksapces of a concrete organization.

    Note: This class should not be instanced, and only be used within an :obj:`deepint.core.organization.Organization`
    
    Attributes:
        organization: the organization with which to operate with its worksapces
    """

    def __init__(self, organization: 'Organization', workspaces: List[Workspace]):
        self.organization = organization
        self._workspaces = workspaces
        self._generator = None

    def load(self):
        """Loads a organization's workspaces.

        If the workspaces were already loaded, this ones are replace by the new ones after retrieval.
        """

        # request
        url = f'https://app.deepint.net/api/v1/workspaces'
        response = handle_request(method='GET', url=url, credentials=self.organization.credentials)

        # map results
        self._generator = (Workspace.build(workspace_id=w['id'], credentials=self.organization.credentials) for w in
                           response)

    def create(self, name: str, description: str) -> Workspace:
        """Creates a workspace in current organization.

        Before creation, the workspace is loaded and stored locally in the internal list of workspaces in the current instance.

        Args:
            name: new workspace's name.
            descrpition: new workspace's description.
        
        Returns:
            the created workspace
        """

        # request
        url = f'https://app.deepint.net/api/v1/workspaces/'
        parameters = {'name': name, 'description': description}
        response = handle_request(method='POST', url=url, credentials=self.organization.credentials,
                                  parameters=parameters)

        # map results
        new_workspace = Workspace.build(workspace_id=response['workspace_id'],
                                        credentials=self.organization.credentials)

        # update local state
        self._workspaces = self._workspaces if self._workspaces is not None else []
        self._workspaces.append(new_workspace)

        return new_workspace

    def create_if_not_exists(self, name: str) -> Workspace:
        """Creates a workspace in current organization if not exists, else retrieves the given worksapce.

        The source is created with the :obj:`deepint.core.organization.OrganizationWorkspaces.create`, so it's reccomended to 
        read the documentation of that method to learn more about the possible artguments of creation.
        Before creation, the workspace is loaded and stored locally in the internal list of workspaces in the current instance.

        Args:
            name: new workspace's name.
        
        Returns:
            the created workspace if not exists, else the retrieved workspace
        """

        # retrieve selected workspace
        selected_workspace = self.fetch(name=name, force_reload=True)

        # if exists return
        if selected_workspace is not None:
            return selected_workspace

        # if not exists, create
        return self.create(name, '')

    def fetch(self, workspace_id: str = None, name: str = None, force_reload: bool = False) -> Optional[Workspace]:
        """Search for a workspace in the organization.

        The first time is invoked, buidls a generator to retrieve workspaces directly from deepint.net API. However, 
        if there is stored workspaces and the force_reload option is not specified, only iterates in local 
        workspaces. In other case, it request the workspaces to deepint.net API and iterates over it.

        Note: if no name or id is provided, the returned value is None.

        Args:
            workspace_id: workspace's id to search by.
            name: workspace's name to search by.
            force_reload: if set to True, workspaces are reloaded before the search with the
                :obj:`deepint.core.organization.OrganizationWorkspaces.load` method.
        
        Returns:
            retrieved workspace if found, and in other case None.
        """

        # if set to true reload
        if force_reload or self._generator is None:
            self.load()

        # check parameters
        if workspace_id is None and name is None:
            return None

        # search by given attributes
        if self._workspaces is not None and not force_reload:
            for ws in self._workspaces:
                if ws.info.workspace_id == workspace_id or ws.info.name == name:
                    return ws

        if self._generator is not None:
            try:
                for ws in self._generator:
                    if ws.info.workspace_id == workspace_id or ws.info.name == name:
                        return ws
            except:
                # if there is an exception, a workspace does not exist anymore and needs to be reloaded
                self.load()
                for ws in self._generator:
                    if ws.info.workspace_id == workspace_id or ws.info.name == name:
                        return ws

        return None

    def fetch_all(self, force_reload: bool = False) -> Generator[Workspace, None, None]:
        """Retrieves all organization's workspaces.
        
        The first time is invoked, buidls a generator to retrieve workspaces directly from deepint.net API. However, 
        if there is stored workspaces and the force_reload option is not specified, only iterates in local 
        workspaces. In other case, it request the workspaces to deepint.net API and iterates over it.

        Args:
            force_reload: if set to True, workspaces are reloaded before the search with the
                :obj:`deepint.core.organization.OrganizationWorkspaces.load` method.
        
        Yields:
            :obj:`deepint.core.workspace.Workspace`: The next workspace returned by deeepint.net API.

        Returns:
            the organization's workspaces.
        """

        # if set to true reload
        if force_reload or self._generator is None:
            self.load()

        if force_reload or self._workspaces is None:
            yield from self._generator
        else:
            yield from self._workspaces



class Organization:
    """A Deep Intelligence Organization.
    
    Note: This class should not be instanced directly, and it's recommended to use the :obj:`deepint.core.organization.Organization.build`
        method.
    
    Attributes:
        workspaces: :obj:`deepint.core.organization.OrganizationWorkspaces` to operate with organization's workspaces.
        account: :obj:`dict` containing information about the providen token, like permissions and associated account details like id or name.
        credentials: credentials to authenticate with Deep Intelligence API and be allowed to perform operations over the task. If
                 not provided, the credentials are generated with the :obj:`deepint.auth.credentials.Credentials.build`.
    """

    def __init__(self, credentials: Credentials, workspaces: List[Workspace], account: Dict[Any, Any]) -> None:
        self.account = account
        self.credentials = credentials
        self.workspaces = OrganizationWorkspaces(self, workspaces)

    def __str__(self):
        return f'<Organization account={self.account}>'

    @classmethod
    def build(cls, credentials: Credentials = None) -> 'Organization':
        """Builds an organization.
        
        Note: when organization is created, the organization's information and account are retrieved from API.

        Args:
            credentials: credentials to authenticate with Deep Intelligence API and be allowed to perform operations over the organization. If
                 not provided, the credentials are generated with the :obj:`deepint.auth.credentials.Credentials.build`.

        Returns:
            the organization build with the given parameters and credentials.
        """

        credentials = credentials if credentials is not None else Credentials.build()
        org = cls(credentials=credentials, workspaces=None, account=None)
        org.load()
        org.workspaces.load()
        return org

    def load(self):
        """Loads the organization's information and account.

        If the organization's or account's information is already loaded, is replace by the new one after retrieval.
        """

        # request
        url = f'https://app.deepint.net/api/v1/who'
        response_who = handle_request(method='GET', url=url, credentials=self.credentials)

        url = f'https://app.deepint.net/api/v1/profile'
        response_profile = handle_request(method='GET', url=url, credentials=self.credentials)

        # map results
        response = {**response_who, **response_profile}
        self.account = response

    def clean(self):
        """Deletes all workspaces in organization.
        """
        
        for ws in self.workspaces.fetch_all():
            ws.delete()
        self.workspaces.load()

    def to_dict(self) -> Dict[str, Any]:
        """Builds a dictionary containing the information stored in current object.

        Returns:
            dictionary contining the information stored in the current object.
        """

        return {"workspaces": [w.to_dict() for w in self.workspaces.fetch_all()]}
