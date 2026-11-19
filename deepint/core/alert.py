#!usr/bin/python

# Copyright 2023 Deep Intelligence
# See LICENSE for details.

"""Alerts of AIR-Core: removed from the API.

.. deprecated:: 2.0.0
    The alerts were removed from the AIR-Core API: API v2 replaced them with automations (simple notices and
    flows), and every route of the alerts in API v1 answers HTTP 410 Gone with the code ``ALERTS_REMOVED``.
    Every method of this module that called the API raises :obj:`deepint.error.DeepintAlertsRemovedError`,
    naming the method that replaces it. Use :obj:`deepint.core.automation.Automation` and
    ``workspace.automations`` (:obj:`deepint.core.workspace.WorkspaceAutomations`) instead. A former alert keeps
    its id as a simple notice: ``Automation.build(organization_id, workspace_id, automation_id=alert_id)``.

    The classes are kept so that code importing them keeps loading; :obj:`AlertWebhook.verify_signature` still works,
    as it does not call the API.
"""

import enum
import hashlib
import hmac
from datetime import datetime
from typing import Any, Dict, List, Union

from ..auth import Credentials
from ..error import DeepintAlertsRemovedError
from ..util import parse_date


def _removed(operation: str, replacement: str):
    raise DeepintAlertsRemovedError(replacement=replacement, operation=operation)


class AlertType(enum.Enum):
    """Types of the former alerts.

    .. deprecated:: 2.0.0
        Alerts are now automations; the type of a simple notice is :obj:`deepint.core.automation.AutomationInfo.automation_type`.
    """

    update = 0
    stall = 1

    @classmethod
    def from_string(cls, _str: str) -> 'AlertType':
        """Builds the :obj:`deepint.core.alert.AlertType` from a :obj:`str`.

        Args:
            _str: name of the alert type.

        Returns:
            the alert type converted to :obj:`deepint.core.alert.AlertType`.
        """

        return cls.unknown if _str not in [e.name for e in cls] else cls[_str]

    @classmethod
    def all(cls) -> List[str]:
        """ Returns all available alert types serialized to :obj:`str`.

        Returns:
            all available alert types
        """

        return [e.name for e in cls]


class AlertInfo:
    """Stores the information of an AIR-Core alert.

    .. deprecated:: 2.0.0
        Alerts are now automations: use :obj:`deepint.core.automation.AutomationInfo`.

    Attributes:
        alert_id: alert's id in format uuid4.
        name: alert's name.
        description: alert's description.
        alert_type: type of alert (update, stall). Set to 'update' if you want to trigger when a source updated
            on certain conditions. Set to 'stall' if you want to trigger when a source do not update for a long time.
        last_modified: Last modified date.
        created: Creation date.
        source_id: Identifier of associated source.
        color: Color for the alert
        condition: condition to trigger the alert.
        time_stall: Time in seconds when the alert should trigger (for stall). Must be at least 60.
        subscriptions: List of emails subscribed to the alert.
    """

    def __init__(self, alert_id: str, name: str, description: str, created: datetime, last_modified: datetime,
                 subscriptions: List[str], color: str, alert_type: AlertType, source_id: str, condition: Dict[str, Any],
                 time_stall: int) -> None:

        if alert_id is not None and not isinstance(alert_id, str):
            raise ValueError('alert_id must be str')

        if name is not None and not isinstance(name, str):
            raise ValueError('name must be str')

        if description is not None and not isinstance(description, str):
            raise ValueError('description must be str')

        if created is not None and not isinstance(created, datetime):
            raise ValueError('created must be datetime.datetime')

        if last_modified is not None and not isinstance(last_modified, datetime):
            raise ValueError('last_modified must be datetime.datetime')

        if subscriptions is not None and not isinstance(subscriptions, list):
            raise ValueError('subscriptions must be a list of str')

        if subscriptions is not None:
            for s in subscriptions:
                if s is not None and not isinstance(s, list):
                    raise ValueError('subscriptions must be a list of str')

        if color is not None and not isinstance(color, str):
            raise ValueError('sources_count must be str')

        if alert_type is not None and (not isinstance(alert_type, AlertType) and not isinstance(alert_type, int)):
            raise ValueError('alert_type must be AlertType')

        if source_id is not None and not isinstance(source_id, str):
            raise ValueError('source_id must be str')

        if condition is not None and not isinstance(condition, dict):
            raise ValueError('condition must be dict')

        if time_stall is not None and not isinstance(time_stall, int):
            raise ValueError('time_stall must be int')

        self.alert_id = alert_id
        self.name = name
        self.description = description
        self.created = created
        self.last_modified = last_modified
        self.subscriptions = subscriptions
        self.color = color
        self.alert_type = alert_type
        self.source_id = source_id
        self.condition = condition
        self.time_stall = time_stall

    def __eq__(self, other) -> None:
        if other is not None and not isinstance(other, AlertInfo):
            return False
        else:
            return self.alert_id == other.alert_id

    def __str__(self):
        return ' '.join([f'{k}={v}' for k, v in self.to_dict().items()])

    @staticmethod
    def from_dict(obj: Any) -> 'AlertInfo':
        """Builds a AlertInfo with a dictionary.

        Args:
            obj: :obj:`object` or :obj:`dict` containing the a serialized AlertInfo.

        Returns:
            AlertInfo containing the information stored in the given dictionary.
        """

        alert_id = obj.get("id")
        name = obj.get("name")
        description = obj.get("description")
        created = parse_date(obj.get("created"))
        last_modified = parse_date(obj.get("last_modified"))
        subscriptions = obj.get("subscriptions")
        color = obj.get("color")
        alert_type = AlertType.from_string(obj.get("type"))
        source_id = obj.get("source")
        condition = obj.get("condition")
        time_stall = int(obj.get("time_stall")) if obj.get(
            "time_stall") is not None else None
        return AlertInfo(alert_id, name, description, created, last_modified, subscriptions, color, alert_type,
                         source_id, condition, time_stall)

    def to_dict(self) -> Dict[str, Any]:
        """Builds a dictionary containing the information stored in current object.

        Returns:
            dictionary containing the information stored in the current object.
        """

        return {"id": self.alert_id,
                "name": self.name,
                "description": self.description,
                "created": self.created.isoformat(),
                "last_modified": self.last_modified.isoformat(),
                "subscriptions": self.subscriptions,
                "color": self.color,
                "type": self.alert_type.name,
                "source": self.source_id,
                "condition": self.condition,
                "time_stall": int(self.time_stall)
                }


class AlertInstances:
    """The instances (firings) of an alert.

    .. deprecated:: 2.0.0
        Removed from the AIR-Core API. Use :obj:`deepint.core.automation.Automation.history`.

    Attributes:
        alert: the alert with which to operate with its instances
    """

    def __init__(self, alert: 'Alert'):

        if alert is not None and not isinstance(alert, Alert):
            raise ValueError('alert must be Alert')

        self.alert = alert

    def fetch(self) -> List[Dict]:
        """Raises :obj:`deepint.error.DeepintAlertsRemovedError`. Use :obj:`deepint.core.automation.Automation.history`.

        .. deprecated:: 2.0.0
        """
        _removed('Alert.instances.fetch()', 'Automation.history()')


class AlertWebhook:
    """The signed outgoing webhook of an alert.

    .. deprecated:: 2.0.0
        Removed from the AIR-Core API. The webhook of an automation is one of its actions
        (``{'type': 'webhook', 'url': ...}``): set it with :obj:`deepint.core.automation.Automation.update` or when it is
        created, and check received events with :obj:`deepint.core.automation.Automation.verify_webhook_signature`.
        :obj:`AlertWebhook.verify_signature` still works.

    Attributes:
        alert: the alert whose webhook is managed
    """

    def __init__(self, alert: 'Alert'):

        self.alert = alert

    def get(self, limit: int = 20) -> Dict[str, Any]:
        """Raises :obj:`deepint.error.DeepintAlertsRemovedError`. The webhook is in the ``actions`` of
        :obj:`deepint.core.automation.Automation.load`.

        .. deprecated:: 2.0.0
        """
        _removed('Alert.webhook.get()', "Automation.load() (the webhook is in info.actions)")

    def set(self, url: str, enabled: bool = True) -> Dict[str, Any]:
        """Raises :obj:`deepint.error.DeepintAlertsRemovedError`. Use
        ``Automation.update(actions=[{'type': 'email', 'to': 'list'}, {'type': 'webhook', 'url': url}])``.

        .. deprecated:: 2.0.0
        """
        _removed('Alert.webhook.set()', "Automation.update(actions=[..., {'type': 'webhook', 'url': url}])")

    def delete(self):
        """Raises :obj:`deepint.error.DeepintAlertsRemovedError`. Use :obj:`deepint.core.automation.Automation.update`
        with ``actions`` without the webhook action.

        .. deprecated:: 2.0.0
        """
        _removed('Alert.webhook.delete()', "Automation.update(actions=[...]) without the webhook action")

    def rotate_secret(self) -> Dict[str, Any]:
        """Raises :obj:`deepint.error.DeepintAlertsRemovedError`. Use ``Automation.update(rotate_secret=True)`` (a flow).

        .. deprecated:: 2.0.0
        """
        _removed('Alert.webhook.rotate_secret()', 'Automation.update(rotate_secret=True)')

    def test(self) -> Dict[str, Any]:
        """Raises :obj:`deepint.error.DeepintAlertsRemovedError`. Use :obj:`deepint.core.automation.Automation.test`.

        .. deprecated:: 2.0.0
        """
        _removed('Alert.webhook.test()', 'Automation.test()')

    @staticmethod
    def verify_signature(secret: str, body: Union[bytes, str], signature_header: str) -> bool:
        """Checks the signature of a received event (receiver side). It does not call the API and keeps working.

        Same as :obj:`deepint.core.automation.Automation.verify_webhook_signature`.

        Args:
            secret: the signing secret of the webhook.
            body: the raw body of the request, as received (bytes, or text decoded as UTF-8).
            signature_header: the value of the ``x-signature-256`` header.

        Returns:
            True if the event was signed with the secret. False for any other header, including a missing or
            malformed one.
        """
        if isinstance(body, str):
            body = body.encode('utf-8')
        expected = 'sha256=' + hmac.new(secret.encode('utf-8'), body, hashlib.sha256).hexdigest()
        received = (signature_header or '').strip().encode('utf-8', 'replace')
        return hmac.compare_digest(expected.encode('ascii'), received)


class Alert:
    """An AIR-Core alert.

    .. deprecated:: 2.0.0
        The alerts were removed from the AIR-Core API (API v1 answers HTTP 410 Gone, code ``ALERTS_REMOVED``).
        Every method that called the API raises :obj:`deepint.error.DeepintAlertsRemovedError`. Use
        :obj:`deepint.core.automation.Automation`; a former alert is a simple notice with the same id.

    Attributes:
        organization_id: organization where alert is located.
        workspace_id: workspace where alert is located.
        info: :obj:`deepint.core.alert.AlertInfo` with the alert's information.
        instances: :obj:`deepint.core.alert.AlertInstances` (deprecated).
        webhook: :obj:`deepint.core.alert.AlertWebhook` (deprecated).
        credentials: credentials to authenticate with AIR-Core API.
    """

    def __init__(self, organization_id: str, workspace_id: str, credentials: Credentials, info: AlertInfo) -> None:

        if organization_id is not None and not isinstance(organization_id, str):
            raise ValueError('organization_id must be str')

        if workspace_id is not None and not isinstance(workspace_id, str):
            raise ValueError('workspace_id must be str')

        if credentials is not None and not isinstance(credentials, Credentials):
            raise ValueError(f'credentials must be {Credentials.__class__}')

        if info is not None and not isinstance(info, AlertInfo):
            raise ValueError(f'info must be {AlertInfo.__class__}')

        self.info = info
        self.credentials = credentials
        self.workspace_id = workspace_id
        self.organization_id = organization_id
        self.instances = AlertInstances(self)
        self.webhook = AlertWebhook(self)

    def __str__(self):
        return f'<Alert organization_id={self.organization_id} workspace={self.workspace_id} {self.info}>'

    def __eq__(self, other):
        if other is not None and not isinstance(other, Alert):
            return False
        else:
            return self.info == other.info

    @classmethod
    def build(cls, organization_id: str, workspace_id: str, alert_id: str, credentials: Credentials = None) -> 'Alert':
        """Raises :obj:`deepint.error.DeepintAlertsRemovedError`. Use
        ``Automation.build(organization_id, workspace_id, automation_id=alert_id)``.

        .. deprecated:: 2.0.0
        """
        _removed('Alert.build()', 'Automation.build(organization_id, workspace_id, automation_id=alert_id)')

    @classmethod
    def from_url(cls, url: str, organization_id: str = None, credentials: Credentials = None) -> 'Alert':
        """Raises :obj:`deepint.error.DeepintAlertsRemovedError`. Use :obj:`deepint.core.automation.Automation.from_url`
        with the API v2 URL (``/api/v2/workspace/{workspace_id}/automations/{alert_id}``).

        .. deprecated:: 2.0.0
        """
        _removed('Alert.from_url()', 'Automation.from_url(url) with /api/v2/workspace/{ws}/automations/{id}')

    def load(self):
        """Raises :obj:`deepint.error.DeepintAlertsRemovedError`. Use :obj:`deepint.core.automation.Automation.load`.

        .. deprecated:: 2.0.0
        """
        _removed('Alert.load()', 'Automation.load()')

    def update(self, name: str = None, description: str = None, subscriptions: List[str] = None, color: str = None,
               alert_type: AlertType = None, source_id: str = None, condition: Dict[str, Any] = None, time_stall: int = None):
        """Raises :obj:`deepint.error.DeepintAlertsRemovedError`. Use :obj:`deepint.core.automation.Automation.update`.

        .. deprecated:: 2.0.0
        """
        _removed('Alert.update()', 'Automation.update(name=..., trigger=..., condition=..., actions=...)')

    def delete(self):
        """Raises :obj:`deepint.error.DeepintAlertsRemovedError`. Use :obj:`deepint.core.automation.Automation.delete`.

        .. deprecated:: 2.0.0
        """
        _removed('Alert.delete()', 'Automation.delete()')

    def to_dict(self) -> Dict[str, Any]:
        """Builds a dictionary containing the information stored in current object.

        Returns:
            dictionary contining the information stored in the current object.
        """

        return {"info": self.info.to_dict()}
