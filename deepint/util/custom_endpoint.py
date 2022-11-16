#!usr/bin/python

# Copyright 2023 Deep Intelligence
# See LICENSE for details.


from typing import Any, Dict

from ..auth import Credentials
from ..error import DeepintBaseError
from . import handle_request, handle_paginated_request


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
