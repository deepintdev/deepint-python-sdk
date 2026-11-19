#!usr/bin/python

# Copyright 2026 AIR-Core
# See LICENSE for details.

"""Automations of AIR-Core (API v2): the simple notices and the flows of a workspace.

An automation watches a source and acts. AIR-Core saves a new automation as a **simple notice**
(``kind == 'notice'``) when it is exactly one, and as a **flow** (``kind == 'flow'``) otherwise:

- a trigger ``{'type': 'stall', 'source': ..., 'hours': n}`` (no new data for ``n`` hours) is always a notice;
- a trigger ``{'type': 'source_updated', 'source': ...}`` is a notice when it has no model, its condition is
  ``{'kind': 'all'}`` or rules on columns of the source with the operators eq, gt, gte, lt, lte, null, cn, sw or
  ew, ``min_rows`` is 1, it emails the whole notice list (``{'type': 'email', 'to': 'list'}``), it writes no rows,
  it calls at most one webhook and it is enabled;
- anything else (a schedule, a model, the ``cni`` operator, another recipient, rows written, created disabled)
  is a flow.

Every create and update answers how it was saved and why (:obj:`deepint.core.automation.Automation.saved_as`).
Editing never changes the kind: a flow stays a flow, and a change that would turn a notice into a flow is
refused with HTTP 409 ``NOT_A_NOTICE`` (create a new automation instead). The notices of a metric, of the
quality of a source or of the monitoring of a model only change their name and description (409 ``NOTICE_FIXED``).
These answers are raised as :obj:`deepint.error.DeepintHTTPError` with that ``code``.
"""

import enum
import hashlib
import hmac
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from ..auth import Credentials
from ..util import handle_request, parse_date, parse_url

AUTOMATION_FIELDS = ('name', 'description', 'enabled', 'trigger', 'model', 'retrain', 'condition', 'actions',
                     'rotate_secret')
"""Fields accepted by the API when an automation is created or updated."""


def _automations_path(workspace_id: str, automation_id: str = None, suffix: str = '') -> str:
    # the automations only exist in API v2, whatever version the rest of the SDK calls
    path = f'/api/v2/workspace/{workspace_id}/automations'
    if automation_id is not None:
        path += f'/{automation_id}'
    return path + suffix


def _automation_body(**fields) -> Dict[str, Any]:
    unknown = [k for k in fields if k not in AUTOMATION_FIELDS]
    if unknown:
        raise ValueError(f'Unknown fields of an automation: {", ".join(unknown)}. '
                         f'Allowed: {", ".join(AUTOMATION_FIELDS)}')
    return {k: v for k, v in fields.items() if v is not None}


class AutomationKind(enum.Enum):
    """Kinds of automation: a simple notice or a flow."""

    notice = 0
    flow = 1
    unknown = 2

    @classmethod
    def from_string(cls, _str: str) -> 'AutomationKind':
        """Builds the :obj:`deepint.core.automation.AutomationKind` from a :obj:`str`.

        Args:
            _str: name of the kind (``'notice'`` or ``'flow'``).

        Returns:
            the kind, or ``AutomationKind.unknown``.
        """

        return cls[_str] if _str in ('notice', 'flow') else cls.unknown

    @classmethod
    def all(cls) -> List[str]:
        """Returns the kinds an automation can have, as :obj:`str`."""

        return ['notice', 'flow']


class AutomationInfo:
    """Stores the information of an AIR-Core automation.

    Attributes:
        automation_id: automation's id.
        kind: :obj:`deepint.core.automation.AutomationKind` (notice or flow).
        automation_type: a simple notice: update, stall, metric, quality or model. None for a flow.
        name: automation's name.
        description: automation's description.
        enabled: whether it is on (a simple notice is always on).
        source_id: the source it watches.
        trigger: what starts it, as a dict (``type``: source_updated, schedule or stall; ``source``; ``every_hours``
            or ``hours``). Only filled when the automation was read in full.
        condition: when it acts, as a dict (``{'kind': 'all'}``, ``{'kind': 'rules', 'match': 'all'|'any',
            'rules': [{'column', 'op', 'value'}]}``, ``{'kind': 'tree', ...}`` or ``{'kind': 'text', ...}``).
        actions: what it does, as a list of dicts (``{'type': 'email', 'to': 'list'}``, ``{'type': 'webhook', ...}``,
            ``{'type': 'append', 'target': ...}``). Of a webhook only its channel and origin are returned.
        created: creation date.
        last_modified: last modification date.
        last_outcome: a flow in a list: the outcome of its last run (status, reason, dry_run, started), or None.
        raw: the dictionary returned by the API, with every field (a flow also has its version, model,
            retraining and history of versions).
    """

    def __init__(self, automation_id: str, kind: AutomationKind, automation_type: str = None, name: str = None,
                 description: str = None, enabled: bool = None, source_id: str = None, trigger: Dict[str, Any] = None,
                 condition: Dict[str, Any] = None, actions: List[Dict[str, Any]] = None, created: datetime = None,
                 last_modified: datetime = None, last_outcome: Dict[str, Any] = None, raw: Dict[str, Any] = None) -> None:

        if automation_id is not None and not isinstance(automation_id, str):
            raise ValueError('automation_id must be str')

        if kind is not None and not isinstance(kind, AutomationKind):
            raise ValueError('kind must be AutomationKind')

        self.automation_id = automation_id
        self.kind = kind
        self.automation_type = automation_type
        self.name = name
        self.description = description
        self.enabled = enabled
        self.source_id = source_id
        self.trigger = trigger
        self.condition = condition
        self.actions = actions
        self.created = created
        self.last_modified = last_modified
        self.last_outcome = last_outcome
        self.raw = raw if raw is not None else {}

    def __eq__(self, other) -> bool:
        if not isinstance(other, AutomationInfo):
            return False
        return self.automation_id == other.automation_id

    def __str__(self):
        return ' '.join([f'{k}={v}' for k, v in self.to_dict().items()])

    @staticmethod
    def from_dict(obj: Any) -> 'AutomationInfo':
        """Builds an AutomationInfo from the dictionary returned by the API (an item of the list or a full automation).

        Args:
            obj: :obj:`dict` containing a serialized automation.

        Returns:
            AutomationInfo containing the information stored in the given dictionary.
        """

        trigger = obj.get('trigger') if isinstance(obj.get('trigger'), dict) else None
        source_id = obj.get('source') or (trigger.get('source') if trigger else None)
        return AutomationInfo(
            automation_id=obj.get('id'),
            kind=AutomationKind.from_string(obj.get('kind')),
            automation_type=obj.get('type'),
            name=obj.get('name'),
            description=obj.get('description'),
            enabled=obj.get('enabled'),
            source_id=source_id or None,
            trigger=trigger,
            condition=obj.get('condition'),
            actions=obj.get('actions'),
            created=parse_date(obj.get('created')),
            last_modified=parse_date(obj.get('updated')),
            last_outcome=obj.get('last_outcome'),
            raw=dict(obj),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Builds a dictionary containing the information stored in current object.

        Returns:
            dictionary containing the information stored in the current object.
        """

        return {'id': self.automation_id,
                'kind': self.kind.name if self.kind is not None else None,
                'type': self.automation_type,
                'name': self.name,
                'description': self.description,
                'enabled': self.enabled,
                'source': self.source_id,
                'trigger': self.trigger,
                'condition': self.condition,
                'actions': self.actions,
                'created': self.created.isoformat() if self.created is not None else None,
                'updated': self.last_modified.isoformat() if self.last_modified is not None else None,
                'last_outcome': self.last_outcome}


class Automation:
    """An AIR-Core automation: a simple notice or a flow of a workspace (API v2).

    Note: This class should not be instanced directly, and it's recommended to use the
    :obj:`deepint.core.automation.Automation.build` or :obj:`deepint.core.automation.Automation.from_url` methods,
    or the :obj:`deepint.core.workspace.WorkspaceAutomations` of a workspace (``workspace.automations``).

    Attributes:
        organization_id: organization where the automation is located.
        workspace_id: workspace where the automation is located.
        info: :obj:`deepint.core.automation.AutomationInfo` with the automation's information.
        saved_as: after a create or an update, how AIR-Core saved it and why: ``{'kind': 'notice'|'flow', 'reason': ...}``
            (STALL or SIMPLE for a notice; SCHEDULE, MODEL, ALERT_CONDITION, OPERATOR, COLUMN, MIN_ROWS, APPEND,
            NO_EMAIL, EMAIL_NOT_LIST or OFF for a flow). None until then.
        webhook_secret: the signing secret of a new webhook, returned only once by the create or update that
            made it (or by ``rotate_secret=True`` on a flow). None otherwise.
        warnings: warnings of the last create or update (``LIST_EMPTY``: the notice list has no address yet).
        credentials: credentials to authenticate with AIR-Core API and be allowed to perform operations over the
            automation. If not provided, the credentials are generated with the :obj:`deepint.auth.credentials.Credentials.build`.
    """

    def __init__(self, organization_id: str, workspace_id: str, credentials: Credentials, info: AutomationInfo) -> None:

        if organization_id is not None and not isinstance(organization_id, str):
            raise ValueError('organization_id must be str')

        if workspace_id is not None and not isinstance(workspace_id, str):
            raise ValueError('workspace_id must be str')

        if credentials is not None and not isinstance(credentials, Credentials):
            raise ValueError(f'credentials must be {Credentials.__class__}')

        if info is not None and not isinstance(info, AutomationInfo):
            raise ValueError(f'info must be {AutomationInfo.__class__}')

        self.organization_id = organization_id
        self.workspace_id = workspace_id
        self.credentials = credentials
        self.info = info
        self.saved_as = None
        self.webhook_secret = None
        self.warnings = []

    def __str__(self):
        return f'<Automation organization_id={self.organization_id} workspace={self.workspace_id} {self.info}>'

    def __eq__(self, other):
        if not isinstance(other, Automation):
            return False
        return self.info == other.info

    @property
    def is_notice(self) -> bool:
        """True when the automation is a simple notice."""
        return self.info is not None and self.info.kind == AutomationKind.notice

    @property
    def is_flow(self) -> bool:
        """True when the automation is a flow."""
        return self.info is not None and self.info.kind == AutomationKind.flow

    def _headers(self) -> Dict[str, str]:
        return {'x-deepint-organization': self.organization_id}

    def _path(self, suffix: str = '') -> str:
        return _automations_path(self.workspace_id, self.info.automation_id, suffix)

    def _apply_saved(self, response: Dict[str, Any]) -> Dict[str, Any]:
        if isinstance(response.get('automation'), dict):
            self.info = AutomationInfo.from_dict(response['automation'])
        self.saved_as = response.get('saved_as')
        self.webhook_secret = response.get('webhook_secret')
        self.warnings = response.get('warnings') or []
        return response

    @classmethod
    def build(cls, organization_id: str, workspace_id: str, automation_id: str,
              credentials: Credentials = None) -> 'Automation':
        """Builds an automation, reading it in full from the API.

        Args:
            organization_id: organization where the automation is located.
            workspace_id: workspace where the automation is located.
            automation_id: automation's id (of a simple notice or of a flow; the id of a former alert is the
                id of its simple notice).
            credentials: credentials to authenticate with AIR-Core API. If not provided, the credentials are
                generated with the :obj:`deepint.auth.credentials.Credentials.build`.

        Returns:
            the automation.
        """

        credentials = credentials if credentials is not None else Credentials.build()
        info = AutomationInfo(automation_id=automation_id, kind=None)
        automation = cls(organization_id=organization_id, workspace_id=workspace_id, credentials=credentials, info=info)
        automation.load()
        return automation

    @classmethod
    def from_url(cls, url: str, organization_id: str = None, credentials: Credentials = None) -> 'Automation':
        """Builds an automation from its API URL.

        Example:
            - https://app.air-core.io/api/v2/workspace/f0e2095f-fe2b-479e-be4b-bbc77207f42/automations/db98f976-f4bb-43d5-830e-bc18a3a89641

        Args:
            url: the automation's API URL.
            organization_id: the id of the organization (the API URL does not contain it).
            credentials: credentials to authenticate with AIR-Core API. If not provided, the credentials are
                generated with the :obj:`deepint.auth.credentials.Credentials.build`.

        Returns:
            the automation.
        """

        url_info, hostname = parse_url(url)

        if 'organization_id' not in url_info and organization_id is None:
            raise ValueError(
                'Fields organization_id must be in url to build the object. Or providen as optional parameter.')

        if 'workspace_id' not in url_info or 'automation_id' not in url_info:
            raise ValueError('Fields workspace_id and automation_id must be in url to build the object.')

        organization_id = url_info.get('organization_id', organization_id)
        credentials = credentials if credentials is not None else Credentials.build()
        new_credentials = Credentials(token=credentials.token, instance=hostname)

        return cls.build(organization_id=organization_id, workspace_id=url_info['workspace_id'],
                         automation_id=url_info['automation_id'], credentials=new_credentials)

    def load(self) -> None:
        """Reads the automation in full (trigger, condition and actions), replacing the information stored."""

        response = handle_request(method='GET', path=self._path(), headers=self._headers(),
                                  credentials=self.credentials)
        self.info = AutomationInfo.from_dict(response)

    def update(self, name: str = None, description: str = None, enabled: bool = None, trigger: Dict[str, Any] = None,
               model: str = None, retrain: str = None, condition: Dict[str, Any] = None,
               actions: List[Dict[str, Any]] = None, rotate_secret: bool = None) -> Dict[str, Any]:
        """Changes the automation. Only the arguments given are sent; the rest keeps its value.

        Editing never changes the kind. A flow stays a flow (a new version of it). A simple notice of type update
        or stall stays a simple notice: a change that would need a flow raises :obj:`deepint.error.DeepintHTTPError`
        with code ``NOT_A_NOTICE`` (create a new automation instead). For a notice, ``actions`` replaces its webhook:
        ``{'type': 'webhook'}`` without ``url`` keeps the saved address, and leaving out the webhook action removes it.
        The notices of a metric, of the quality of a source or of the monitoring of a model only change ``name`` and
        ``description`` (code ``NOTICE_FIXED``).

        Args:
            name: name (up to 120 characters).
            description: description (up to 300 characters).
            enabled: whether it is on (a simple notice is always on).
            trigger: what starts it, see :obj:`deepint.core.workspace.WorkspaceAutomations.create`.
            model: id of a model that predicts the new rows (a flow).
            retrain: retraining of the model (``'never'``, ``'if_due'`` or ``'always'``; a flow).
            condition: when it acts.
            actions: what it does (up to 3).
            rotate_secret: a flow: True for a new signing secret of its webhook (returned once in ``webhook_secret``).

        Returns:
            the answer of the API: ``kind``, ``saved_as``, ``automation``, and ``webhook_secret`` and ``warnings``
            when there are. The object's ``info``, ``saved_as``, ``webhook_secret`` and ``warnings`` are updated.
        """

        body = _automation_body(name=name, description=description, enabled=enabled, trigger=trigger, model=model,
                                retrain=retrain, condition=condition, actions=actions, rotate_secret=rotate_secret)
        response = handle_request(method='PUT', path=self._path(), headers=self._headers(), parameters=body,
                                  credentials=self.credentials)
        return self._apply_saved(response)

    def delete(self) -> Dict[str, Any]:
        """Deletes the automation (a simple notice with its webhook, or a flow with its runs).

        Returns:
            the answer of the API: ``{'result': 'success', 'kind': ..., 'id': ...}``.
        """

        return handle_request(method='DELETE', path=self._path(), headers=self._headers(),
                              credentials=self.credentials)

    def history(self, page: int = None, limit: int = None) -> Dict[str, Any]:
        """Reads the history of the automation, newest first.

        Of a simple notice, when it fired, with the rows that met its condition (only for those who can read the
        sources), paginated with ``page`` and ``limit``: ``{'kind': 'notice', 'page', 'limit', 'pages_count',
        'items_count', 'items': [{'id', 'timestamp', 'data'}]}``. Of a flow, its runs with what each step did
        (counts, never rows), up to ``limit`` (50 at most): ``{'kind': 'flow', 'items': [...]}``.

        Args:
            page: page to read, starting at 0 (simple notices).
            limit: items per page (simple notices) or number of runs (flows).

        Returns:
            the history, as returned by the API.
        """

        return handle_request(method='GET', path=self._path('/history'), headers=self._headers(),
                              parameters={'page': page, 'limit': limit}, credentials=self.credentials)

    def test(self) -> Dict[str, Any]:
        """Tests the automation: what would happen now, with nothing sent, retrained or written.

        A flow answers its test run (at most 10 an hour). A simple notice of type update answers its condition on
        the newest 20 rows of its source (``rows_checked``, ``matched``, ``would_fire`` and up to 5 rows in
        ``preview`` for those who can read the sources); one of type stall, the hours without new data
        (``silent_hours``) against its limit (``after_hours``). The notices of a metric, of the quality of a source
        or of the monitoring of a model raise :obj:`deepint.error.DeepintHTTPError` with code ``TEST_NOT_AVAILABLE``.

        Returns:
            the result of the test, as returned by the API.
        """

        return handle_request(method='POST', path=self._path('/test'), headers=self._headers(), parameters={},
                              credentials=self.credentials)

    @staticmethod
    def verify_webhook_signature(secret: str, body: Union[bytes, str], signature_header: str) -> bool:
        """Checks the signature of an event received from the webhook of an automation (receiver side).

        AIR-Core signs each event with HMAC-SHA256 over the raw body, in the header ``x-signature-256: sha256=<hex>``.
        The ``x-aircore-delivery`` header identifies each event and is the same in its retries: process an identifier
        only once.

        Args:
            secret: the signing secret of the webhook (``webhook_secret``, returned once).
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

    def to_dict(self) -> Dict[str, Any]:
        """Builds a dictionary containing the information stored in current object.

        Returns:
            dictionary containing the information stored in the current object.
        """

        return {'info': self.info.to_dict()}


def list_automations(organization_id: str, workspace_id: str, credentials: Credentials,
                     kind: Optional[Union[str, AutomationKind]] = None) -> List[AutomationInfo]:
    """Lists the automations of a workspace, by name (used by :obj:`deepint.core.workspace.WorkspaceAutomations`).

    Args:
        organization_id: organization of the workspace.
        workspace_id: the workspace.
        credentials: credentials to authenticate with AIR-Core API.
        kind: ``'notice'`` or ``'flow'`` (or an :obj:`deepint.core.automation.AutomationKind`) to list only one kind.

    Returns:
        the summary of each automation (``trigger``, ``condition`` and ``actions`` are only read in full).
    """

    if isinstance(kind, AutomationKind):
        kind = kind.name
    if kind is not None and kind not in AutomationKind.all():
        raise ValueError("kind must be 'notice', 'flow' or None")
    response = handle_request(method='GET', path=_automations_path(workspace_id),
                              headers={'x-deepint-organization': organization_id},
                              parameters={'kind': kind}, credentials=credentials)
    return [AutomationInfo.from_dict(item) for item in response.get('items', [])]


def create_automation(organization_id: str, workspace_id: str, credentials: Credentials,
                      **fields) -> Automation:
    """Creates an automation (used by :obj:`deepint.core.workspace.WorkspaceAutomations.create`).

    Returns:
        the automation, with ``saved_as``, ``webhook_secret`` and ``warnings`` of the creation.
    """

    body = _automation_body(**fields)
    response = handle_request(method='POST', path=_automations_path(workspace_id),
                              headers={'x-deepint-organization': organization_id},
                              parameters=body, credentials=credentials)
    automation = Automation(organization_id=organization_id, workspace_id=workspace_id, credentials=credentials,
                            info=AutomationInfo(automation_id=None, kind=None))
    automation._apply_saved(response)
    return automation
