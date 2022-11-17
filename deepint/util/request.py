#!usr/bin/python

# Copyright 2023 Deep Intelligence
# See LICENSE for details.


from time import sleep
from typing import Any, Dict

import requests

from ..auth import Credentials
from ..error import DeepintBaseError, DeepintHTTPError


def retry_on(codes=('LIMIT', 'TIMEOUT_ERROR', 'BAD_GATEWAY'), times=3, time_between_tries=10):
    def decorator(func):
        def newfn(*args, **kwargs):
            attempt = 0
            while attempt < times:
                try:
                    return func(*args, **kwargs)
                except DeepintHTTPError as e:
                    sleep(time_between_tries)
                    attempt += 1
                    if e.code not in codes:
                        raise e
            return func(*args, **kwargs)

        return newfn

    return decorator


@retry_on(codes=('LIMIT', 'TIMEOUT_ERROR', 'BAD_GATEWAY'), times=3)
def handle_request(credentials: Credentials = None, method: str = None, path: str = None, parameters: dict = None,
                   headers: dict = None, files: tuple = None):
    # build request parameters
    auth_header = {'x-auth-token': credentials.token}
    if headers is None:
        header = headers
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
        raise DeepintHTTPError(
            code=response_json['code'], message=response_json['message'], method=method, url=url)

    return response_json


def handle_paginated_request(credentials: Credentials = None, method: str = None, path: str = None,
                             headers: dict = None, parameters: dict = None, files: tuple = None):
    # first response
    response = handle_request(credentials=credentials, method=method,
                              path=path, parameters=parameters, headers=headers, files=files)

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
                                  path=path, headers=headers, parameters=parameters, files=files)

        # update state and return items
        yield from response['items']
        next_page = response['page'] + 1
        total_pages = response['pages_count']


class CustomEndpointCall:
    """Allows to create custom endpoints to communciate with Deep Intelligence.

    Attributes:
        organization_id: Deep Intelligence organization.
        credentials: credentials to auth with.
    """

    def __init__(self, organization_id: str, credentials: Credentials) -> None:

        self.credentials = credentials
        self.organization_id = organization_id

    def call(self, http_operation: str, path: str, headers: Dict[str, Any], parameters: Dict[str, Any], is_paginated: bool = False) -> Dict[str, Any]:
        """Performs a call on a custon Deep Ingelligence endpoint. It performs the authentication and organziation set previously.

        Args:
            http_operation: the HTTP method to run, such as GET, POST, PUT and DELETE.
            path: the URL path to run
            headers: the headers except the organization and authentication information.
            parameters: the parameters to send in the URL or body of the request. It will be formated to suite the Deep Intelligence restrictions.
            is_paginated: set to True if you want to handle a paginated request. In that case a generator will be returned to iterate through all results.

        Returns:
            The response of Deep Intelligence API
        """

        # check
        if http_operation.upper() not in ['GET', 'POST', 'PUT', 'DELETE']:
            raise DeepintBaseError(code='OPERATION_NOT_ALLOWED', message='The allowed operations on Deep Intelligence custon endpoint, currenlty are GET, POST, PUT and DELETE')

        # preprocess parameters
        http_operation = http_operation.upper()

        headers = {} if headers is None else headers
        headers['x-deepint-organization'] = self.organization_id

        request_method = handle_request if not is_paginated else handle_paginated_request

        # request
        response = request_method(method=http_operation, path=path, headers=headers, parameters=parameters, credentials=self.credentials)

        return response
