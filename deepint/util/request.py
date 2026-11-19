#!usr/bin/python

# Copyright 2023 Deep Intelligence
# See LICENSE for details.


import os
import re
from time import sleep
from typing import Any, Dict

import requests

from ..auth import Credentials
from ..error import DeepintAlertsRemovedError, DeepintBaseError, DeepintHTTPError

API_VERSIONS = ('v1', 'v2')
"""Versions of the AIR-Core API that the SDK can target."""

DEFAULT_API_VERSION = 'v2'
"""Version of the AIR-Core API used when none is configured."""

_API_PREFIX = re.compile(r'^/api/v[12](?=/|\?|$)')


def _normalize_api_version(version) -> str:
    v = str(version).strip().lower()
    v = v if v.startswith('v') else f'v{v}'
    if v not in API_VERSIONS:
        raise DeepintBaseError(code='BAD_API_VERSION',
                               message=f'The API version must be one of {", ".join(API_VERSIONS)}, not {version!r}.')
    return v


_api_version = _normalize_api_version(os.environ.get('AIRCORE_API_VERSION') or DEFAULT_API_VERSION)


def set_api_version(version: str) -> None:
    """Sets the version of the AIR-Core API that the SDK calls (``'v2'`` by default).

    API v2 serves every operation of API v1 under ``/api/v2/`` except the alerts, which became automations.
    API v1 is deprecated and keeps working; set ``'v1'`` only to keep calling it. The automations always use
    API v2, whatever this setting. It can also be set with the ``AIRCORE_API_VERSION`` environment variable.

    Args:
        version: ``'v2'`` or ``'v1'`` (``2`` and ``1`` are accepted too).
    """
    global _api_version
    _api_version = _normalize_api_version(version)


def get_api_version() -> str:
    """Returns the version of the AIR-Core API that the SDK calls (``'v2'`` or ``'v1'``)."""
    return _api_version


def api_path(path: str) -> str:
    """Returns the path of an operation of the API in the configured version.

    The SDK writes its paths as ``/api/v1/...``; they are sent to ``/api/v2/...`` unless
    :obj:`deepint.util.request.set_api_version` selected ``'v1'``. Other paths are returned as they are.
    """
    if path is None:
        return path
    return _API_PREFIX.sub(f'/api/{_api_version}', path, count=1) if path.startswith('/api/v1') else path


def retry_on(codes=('LIMIT', 'TIMEOUT_ERROR', 'BAD_GATEWAY'), times=3, time_between_tries=10):
    def decorator(func):
        def newfn(*args, **kwargs):
            attempt = 0
            while attempt < times:
                try:
                    return func(*args, **kwargs)
                except DeepintHTTPError as e:
                    if e.code not in codes:
                        raise e
                    sleep(time_between_tries)
                    attempt += 1
            return func(*args, **kwargs)

        return newfn

    return decorator


@retry_on(codes=('LIMIT', 'TIMEOUT_ERROR', 'BAD_GATEWAY'), times=3)
def handle_request(credentials: Credentials = None, method: str = None, path: str = None, parameters: dict = None,
                   headers: dict = None, files: tuple = None, versioned: bool = True):
    # paths written for /api/v1 go to the configured version of the API (v2 by default)
    if versioned:
        path = api_path(path)

    # build request parameters
    auth_header = {'x-auth-token': credentials.token}
    if headers is None:
        header = auth_header
    else:
        header = {**auth_header, **headers}

    if parameters is not None:
        parameters = {k: parameters[k]
                      for k in parameters if parameters[k] is not None}

    # prepare request parts
    url = f'https://{credentials.instance}{path}'
    params = parameters if method == 'GET' else None
    data = parameters if method != 'GET' and files is not None else None
    json_data = parameters if method != 'GET' and files is None else None

    # perform request
    response = requests.request(method=method, url=url, headers=header,
                                params=params, json=json_data, data=data, files=files)

    if response.status_code == 500:
        raise DeepintHTTPError(code='UNKOWN_ERROR',
                               message='System errored. Please, wait a few seconds and try again.',
                               method=method, url=url)
    elif response.status_code == 504:
        raise DeepintHTTPError(code='TIMEOUT_ERROR',
                               message='System reached maximum timeout in the request processing. Please, wait a few seconds and try again.',
                               method=method, url=url)
    elif response.status_code == 502:
        raise DeepintHTTPError(code='BAD_GATEWAY',
                               message='Unable to estabilish connection to system. Please, wait a few seconds and try again.',
                               method=method, url=url)

    # retrieve information
    try:
        response_json = response.json()
    except:
        raise DeepintHTTPError(
            code=response.status_code, message='The API returned a no JSON-deserializable response.', method=method, url=url)

    if response.status_code != 200:
        code = response_json.get('code') if isinstance(response_json, dict) else None
        message = response_json.get('message') if isinstance(response_json, dict) else None
        if code == 'ALERTS_REMOVED':
            raise DeepintAlertsRemovedError(replacement=response_json.get('replacement'), message=message,
                                            method=method, url=url, docs=response_json.get('docs'))
        raise DeepintHTTPError(
            code=code if code is not None else response.status_code,
            message=message if message is not None else f'HTTP {response.status_code}', method=method, url=url)

    return response_json


def handle_paginated_request(credentials: Credentials = None, method: str = None, path: str = None,
                             headers: dict = None, parameters: dict = None, files: tuple = None, versioned: bool = True):
    # first response
    response = handle_request(credentials=credentials, method=method,
                              path=path, parameters=parameters, headers=headers, files=files, versioned=versioned)

    # update state and return items
    yield from response['items']
    next_page = response['page'] + 1
    total_pages = response['pages_count']

    # create parameters
    parameters = parameters if parameters is not None else {}

    # request the rest of the data
    while next_page < total_pages:
        # update parameters and perform request
        parameters['page'] = next_page
        response = handle_request(credentials=credentials, method=method,
                                  path=path, headers=headers, parameters=parameters, files=files, versioned=versioned)

        # update state and return items
        yield from response['items']
        next_page = response['page'] + 1
        total_pages = response['pages_count']


class CustomEndpointCall:
    """Allows to create custom endpoints to communciate with AIR-Core.

    Attributes:
        organization_id: AIR-Core organization.
        credentials: credentials to auth with.
    """

    def __init__(self, organization_id: str, credentials: Credentials) -> None:

        self.credentials = credentials
        self.organization_id = organization_id

    def call(self, http_operation: str, path: str, headers: Dict[str, Any], parameters: Dict[str, Any], is_paginated: bool = False) -> Dict[str, Any]:
        """Performs a call on a custon Deep Ingelligence endpoint. It performs the authentication and organziation set previously.

        Args:
            http_operation: the HTTP method to run, such as GET, POST, PUT and DELETE.
            path: the URL path to run, sent as it is (``/api/v1/...`` is not changed to the configured API version).
            headers: the headers except the organization and authentication information.
            parameters: the parameters to send in the URL or body of the request. It will be formated to suite the AIR-Core restrictions.
            is_paginated: set to True if you want to handle a paginated request. In that case a generator will be returned to iterate through all results.

        Returns:
            The response of AIR-Core API
        """

        # check
        if http_operation.upper() not in ['GET', 'POST', 'PUT', 'DELETE']:
            raise DeepintBaseError(code='OPERATION_NOT_ALLOWED', message='The allowed operations on AIR-Core custon endpoint, currenlty are GET, POST, PUT and DELETE')

        # preprocess parameters
        http_operation = http_operation.upper()

        headers = {} if headers is None else headers
        headers['x-deepint-organization'] = self.organization_id

        request_method = handle_request if not is_paginated else handle_paginated_request

        # request
        response = request_method(method=http_operation, path=path, headers=headers, parameters=parameters, credentials=self.credentials,
                                  versioned=False)

        return response
