#!usr/bin/python

# Copyright 2023 Deep Intelligence
# See LICENSE for details.

# Requests of the API 1.1 features (explanations, model card, alert webhooks, AI activity), checked against a mocked
# HTTP layer: no instance or credentials needed.

import hashlib
import hmac
import json
import unittest
from datetime import datetime, timezone
from unittest import mock

import pandas as pd

from deepint.auth import Credentials
from deepint.core.alert import Alert, AlertInfo, AlertWebhook
from deepint.core.model import Model, ModelFeature, ModelInfo
from deepint.core.organization import Organization
from deepint.core.source import FeatureType
from deepint.util import handle_request


def response(body):
    r = mock.Mock()
    r.status_code = 200
    r.json.return_value = body
    return r


CREDENTIALS = Credentials(token='tkn', instance='app.air-core.io')


def model():
    info = ModelInfo(model_id='m1', name='m', description='', model_type=None, method=None, created=None,
                     last_modified=None, last_access=None, source_train=None, configuration={}, size_bytes=0)
    inputs = [ModelFeature('a', FeatureType.numeric, 0), ModelFeature('b', FeatureType.numeric, 1)]
    return Model('org1', 'ws1', CREDENTIALS, info, inputs, [ModelFeature('y', FeatureType.nominal, 2)])


class TestApi11(unittest.TestCase):

    @mock.patch('deepint.util.request.requests.request')
    def test_token_sent_without_extra_headers(self, request):
        request.return_value = response({})
        handle_request(credentials=CREDENTIALS, method='GET', path='/api/v1/who')
        self.assertEqual(request.call_args.kwargs['headers'], {'x-auth-token': 'tkn'})

    @mock.patch('deepint.util.request.requests.request')
    def test_explain_prediction_orders_inputs_like_the_model(self, request):
        request.return_value = response({'contributions': []})
        model().explanations.explain_prediction(pd.DataFrame([{'b': 2, 'a': 1}]), lang='en')
        kwargs = request.call_args.kwargs
        self.assertEqual(kwargs['method'], 'POST')
        self.assertTrue(kwargs['url'].endswith('/api/v1/workspace/ws1/models/m1/explanation/prediction'))
        self.assertEqual(kwargs['json'], {'inputs': [1, 2], 'lang': 'en'})

    @mock.patch('deepint.util.request.requests.request')
    def test_global_importances_and_card(self, request):
        request.return_value = response({})
        m = model()
        m.explanations.global_importances()
        self.assertTrue(request.call_args.kwargs['url'].endswith('/models/m1/explanation'))
        self.assertEqual(request.call_args.kwargs['params'], {})
        m.card(lang='es')
        self.assertEqual(request.call_args.kwargs['params'], {'format': 'json', 'lang': 'es'})

    @mock.patch('deepint.util.request.requests.request')
    def test_alert_webhook_requests(self, request):
        request.return_value = response({'result': 'success'})
        info = AlertInfo(alert_id='al1', name='n', description='', created=None, last_modified=None, subscriptions=[],
                         color='#000', alert_type=None, source_id='s', condition={}, time_stall=None)
        alert = Alert('org1', 'ws1', CREDENTIALS, info)
        alert.webhook.set('https://hooks.example.com/x')
        self.assertEqual(request.call_args.kwargs['json'], {'url': 'https://hooks.example.com/x', 'enabled': True})
        alert.webhook.rotate_secret()
        self.assertTrue(request.call_args.kwargs['url'].endswith('/alerts/al1/webhook/rotate'))
        alert.webhook.test()
        self.assertTrue(request.call_args.kwargs['url'].endswith('/alerts/al1/webhook/test'))

    @mock.patch('deepint.util.request.requests.request')
    def test_explain_prediction_sends_missing_values_and_dates_as_json(self, request):
        request.return_value = response({'contributions': []})
        model().explanations.explain_prediction(pd.DataFrame([{'a': float('nan'), 'b': 2.0}]))
        self.assertEqual(request.call_args.kwargs['json']['inputs'], [None, 2.0])
        model().explanations.explain_prediction(pd.DataFrame([{'a': pd.Timestamp('2026-10-30T12:00:00'), 'b': pd.NaT}]))
        sent = request.call_args.kwargs['json']['inputs']
        self.assertEqual(sent, ['2026-10-30T12:00:00', None])
        json.dumps(sent, allow_nan=False)
        model().explanations.explain_prediction([float('nan'), 3])
        self.assertEqual(request.call_args.kwargs['json']['inputs'], [None, 3])

    @mock.patch('deepint.util.request.requests.request')
    def test_webhook_deliveries_limit(self, request):
        request.return_value = response({'webhook': None, 'deliveries': []})
        info = AlertInfo(alert_id='al1', name='n', description='', created=None, last_modified=None, subscriptions=[],
                         color='#000', alert_type=None, source_id='s', condition={}, time_stall=None)
        Alert('org1', 'ws1', CREDENTIALS, info).webhook.get(limit=50)
        self.assertEqual(request.call_args.kwargs['params'], {'limit': 50})

    def test_webhook_signature_of_text_bodies_and_malformed_headers(self):
        body = '{"event":"alert","name":"Ñandú"}'
        header = 'sha256=' + hmac.new(b'secret', body.encode('utf-8'), hashlib.sha256).hexdigest()
        self.assertTrue(AlertWebhook.verify_signature('secret', body, header))
        self.assertFalse(AlertWebhook.verify_signature('secret', body, 'sha256=ñ'))
        self.assertFalse(AlertWebhook.verify_signature('secret', body, ''))

    def test_webhook_signature(self):
        body = b'{"event":"alert"}'
        header = 'sha256=' + hmac.new(b'secret', body, hashlib.sha256).hexdigest()
        self.assertTrue(AlertWebhook.verify_signature('secret', body, header))
        self.assertFalse(AlertWebhook.verify_signature('other', body, header))
        self.assertFalse(AlertWebhook.verify_signature('secret', body, None))

    @mock.patch('deepint.util.request.requests.request')
    def test_ai_activity_filters(self, request):
        request.return_value = response({'items': []})
        org = Organization('org1', CREDENTIALS, [], {})
        org.ai_activity(channel='mcp', from_time=datetime(2026, 10, 1, tzinfo=timezone.utc))
        params = request.call_args.kwargs['params']
        self.assertEqual(params['channel'], 'mcp')
        self.assertEqual(params['from'], 1790812800000)
        self.assertNotIn('to', params)


if __name__ == '__main__':
    unittest.main()
