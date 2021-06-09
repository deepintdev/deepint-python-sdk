#!usr/bin/python

# Copyright 2021 Deep Intelligence
# See LICENSE for details.

import requests
from time import sleep

from ..auth import Credentials
from ..error import DeepintHTTPError


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
def handle_request(credentials: Credentials = None, method: str = None, url: str = None, parameters: dict = None,
                   files: tuple = None):
    # build request parameters
    header = {'x-auth-token': credentials.token, 'x-deepint-organization': credentials.organization}

    if parameters is not None:
        parameters = {k: parameters[k] for k in parameters if parameters[k] is not None}

    # prepare request parts
    data = parameters if method != 'GET' else None
    params = parameters if method == 'GET' else None

    # perform request
    response = requests.request(method=method, url=url, headers=header, params=params, json=data, files=files)

    if response.status_code == 504:
        raise DeepintHTTPError(code='TIMEOUT_ERROR',
                               message='System reached maximum timeout in the request processing. Please, wait a few seconds and try again.',
                               method=method, url=url)
    elif response.status_code == 502:
        raise DeepintHTTPError(code='BAD_GATEWAY',
                               message='Unable to estabilish connection to system. Please, wait a few seconds and try again.',
                               method=method, url=url)

    # retrieve information
    response_json = response.json()

    if response.status_code != 200:
        raise DeepintHTTPError(code=response_json['code'], message=response_json['message'], method=method, url=url)

    return response_json


def handle_paginated_request(credentials: Credentials = None, method: str = None, url: str = None,
                             parameters: dict = None, files: tuple = None):
    # first response
    response = handle_request(credentials=credentials, method=method, url=url, parameters=parameters, files=files)

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
        response = handle_request(credentials=credentials, method=method, url=url, parameters=parameters, files=files)

        # update state and return items
        yield from response['items']
        next_page = response['page'] + 1
        total_pages = response['pages_count']
