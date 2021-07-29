#!usr/bin/python

# Copyright 2021 Deep Intelligence
# See LICENSE for details.


from datetime import datetime
from typing import Any, List, Dict

from ..auth import Credentials
from ..error import DeepintBaseError
from ..util import handle_request, parse_date, parse_url


class DashboardInfo:
    pass


class Dashboard:
    """Stores the information of a Deep Intelligence dashboard.
    
    Attributes:
        dashboard_id: dashboard's id in format uuid4.
        name: dashboard's name.
        description: dashboard's description.
        created: creation date.
        last_modified: last modified date.
        last_access: last access date.
    """

    def __init__(self, dashboard_id: str, created: datetime, last_modified: datetime, last_access: datetime, name: str,
                 description: str) -> None:
        self.dashboard_id = dashboard_id
        self.created = created
        self.last_modified = last_modified
        self.last_access = last_access
        self.name = name
        self.description = description

    def __eq__(self, other):
        if not isinstance(other, Dashboard):
            return False
        else:
            return self.dashboard_id == other.dashboard_id

    def __str__(self):
        return '<Dashboard ' + ' '.join([f'{k}={v}' for k, v in self.to_dict().items()]) + '>'

    @staticmethod
    def from_dict(obj: Any) -> 'Dashboard':
        """Builds a Dashboard with a dictionary.

        Args:
            obj: :obj:`object` or :obj:`dict` containing the a serialized Dashboard.

        Returns:
            Dashboard containing the information stored in the given dictionary.
        """

        dashboard_id = obj.get("id")
        created = parse_date(obj.get("created"))
        last_modified = parse_date(obj.get("last_modified"))
        last_access = parse_date(obj.get("last_access"))
        name = obj.get("name")
        description = obj.get("description")
        return Dashboard(dashboard_id, created, last_modified, last_access, name, description)

    def to_dict(self) -> Dict[str, Any]:
        """Builds a dictionary containing the information stored in current object.

        Returns:
            dictionary containing the information stored in the current object.
        """

        return {"id": self.dashboard_id, "created": self.created.isoformat(),
                "last_modified": self.last_modified.isoformat(), "last_access": self.last_access.isoformat(),
                "name": self.name, "description": self.description}