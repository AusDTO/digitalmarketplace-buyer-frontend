from __future__ import absolute_import
import json
import os
from app.api_client.error import HTTPError

try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse

import requests
from flask import has_request_context, request, current_app

from functools import partial


def pretty_print_request(prep):
    """
    Useful to print out the request call. Example-
    response = requests.Request(method, url, headers=headers, json=data, params=params)
    prepared = response.prepare()
    pretty_print_request(prepared)

    At this point it is completely built and ready
    to be fired; it is "prepared".

    However pay attention at the formatting used in
    this function because it is programmed to be pretty
    printed and may differ from the actual request.
    """
    print('{}\n{}\n{}\n\n{}'.format(
        '-----------START-----------',
        prep.method + ' ' + prep.url,
        '\n'.join('{}: {}'.format(k, v) for k, v in prep.headers.items()),
        prep.body,
        ))


class GenericRequester(object):
    def __init__(self, client):
        self.client = client

    def __getattr__(self, name):
        method_name, route = name.split('_', 1)
        method_call_name = '_{}'.format(method_name)
        method = getattr(self.client, method_call_name)

        route_name = '/{}'.format(route)
        return partial(method, route_name)


class BaseAPIClient(object):
    def __init__(self, base_url=None, auth_token=None, enabled=True):
        self.base_url = base_url or current_app.config.get('DM_DATA_API_URL', '')
        self.auth_token = auth_token or current_app.config.get('DM_DATA_API_AUTH_TOKEN', '')
        self.enabled = enabled
        self.req = GenericRequester(self)

    def _put(self, url, data):
        return self._request("PUT", url, data=data)

    def _get(self, url, data=None, params=None):
        return self._request("GET", url, data=data, params=params)

    def _post(self, url, data):
        return self._request("POST", url, data=data)

    def _patch(self, url, data):
        return self._request("PATCH", url, data=data)

    def _delete(self, url, data=None):
        return self._request("DELETE", url, data=data)

    def _delete_with_updated_by(self, url, data, user):
        data = dict(data, updated_by=user)
        return self._delete(url, data)

    def _request(self, method, url, data=None, params=None):
        if not self.enabled:
            return None

        url = url.lstrip('/')
        url = urlparse.urljoin(self.base_url, url)

        headers = {
            "Content-type": "application/json",
            "Authorization": "Bearer {}".format(self.auth_token),
            "User-agent": "DM-API-Client",
            }

        headers = self._add_request_id_header(headers)

        try:
            response = requests.request(method, url, headers=headers, json=data, params=params)
            response.raise_for_status()
            return response.json()

        except requests.RequestException as e:
            api_error = HTTPError.create(e)
            print "API %s request on %s failed with %s '%s'" % (method, url, api_error.status_code, api_error.message)
            raise api_error

    def _add_request_id_header(self, headers):
        if not has_request_context():
            return headers
        if 'DM_REQUEST_ID_HEADER' not in current_app.config:
            return headers
        header = current_app.config['DM_REQUEST_ID_HEADER']
        headers[header] = request.request_id
        return headers

    def get_status(self):
        return self._get("{}/_status".format(self.base_url))
