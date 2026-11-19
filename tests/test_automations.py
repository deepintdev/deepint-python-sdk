#!usr/bin/python

# Copyright 2026 AIR-Core
# See LICENSE for details.

# Automations (API v2), the version of the API the SDK calls and the removed alerts, checked against a mocked
# HTTP layer: no instance or credentials needed.

import hashlib
import hmac
import unittest
from unittest import mock

from deepint.auth import Credentials
from deepint.core.alert import Alert, AlertInfo, AlertWebhook
from deepint.core.automation import Automation, AutomationInfo, AutomationKind
from deepint.core.workspace import Workspace, WorkspaceInfo
from deepint.error import DeepintAlertsRemovedError, DeepintBaseError, DeepintHTTPError
from deepint.util import (CustomEndpointCall, api_path, get_api_version, handle_request, parse_url,
                          set_api_version)

CREDENTIALS = Credentials(token='tkn', instance='app.air-core.io')


def response(body, status=200):
    r = mock.Mock()
    r.status_code = status
    r.json.return_value = body
    return r


def workspace():
    info = WorkspaceInfo(workspace_id='ws1', name='w', description='', created=None, last_modified=None,
                         last_access=None, sources_count=0, dashboards_count=0, visualizations_count=0,
                         models_count=0, size_bytes=0)
    return Workspace('org1', CREDENTIALS, info, sources=None, models=None, tasks=None, alerts=None,
                     visualizations=None, dashboards=None, emails=None)


NOTICE = {'id': 'a1', 'kind': 'notice', 'type': 'update', 'name': 'Hot', 'description': '', 'enabled': True,
          'trigger': {'type': 'source_updated', 'source': 's1'},
          'condition': {'kind': 'rules', 'match': 'all', 'rules': [{'column': 't', 'op': 'gt', 'value': 30}]},
          'actions': [{'type': 'email', 'to': 'list'}], 'created': 1790812800000, 'updated': 1790812800000}

FLOW_ITEM = {'id': 'f1', 'kind': 'flow', 'name': 'Daily', 'description': '', 'enabled': True, 'source': 's1',
             'created': 1790812800000, 'updated': None, 'last_outcome': {'status': 'ok'}}


class TestApiVersion(unittest.TestCase):

    def tearDown(self):
        set_api_version('v2')

    def test_v2_by_default(self):
        self.assertEqual(get_api_version(), 'v2')
        self.assertEqual(api_path('/api/v1/workspace/ws1/source/s1'), '/api/v2/workspace/ws1/source/s1')
        self.assertEqual(api_path('/api/v1/who'), '/api/v2/who')
        self.assertEqual(api_path('/api/v1'), '/api/v2')
        self.assertEqual(api_path('/api/v2/workspace/ws1/automations'), '/api/v2/workspace/ws1/automations')
        self.assertEqual(api_path('/api/v10/x'), '/api/v10/x')
        self.assertEqual(api_path('/other/api/v1/x'), '/other/api/v1/x')

    def test_v1_can_be_chosen(self):
        set_api_version(1)
        self.assertEqual(get_api_version(), 'v1')
        self.assertEqual(api_path('/api/v1/who'), '/api/v1/who')
        # the automations only exist in v2
        self.assertEqual(api_path('/api/v2/workspace/ws1/automations'), '/api/v2/workspace/ws1/automations')
        with self.assertRaises(DeepintBaseError):
            set_api_version('v3')

    @mock.patch('deepint.util.request.requests.request')
    def test_requests_go_to_the_configured_version(self, request):
        request.return_value = response({})
        handle_request(credentials=CREDENTIALS, method='GET', path='/api/v1/who')
        self.assertEqual(request.call_args.kwargs['url'], 'https://app.air-core.io/api/v2/who')
        set_api_version('v1')
        handle_request(credentials=CREDENTIALS, method='GET', path='/api/v1/who')
        self.assertEqual(request.call_args.kwargs['url'], 'https://app.air-core.io/api/v1/who')

    @mock.patch('deepint.util.request.requests.request')
    def test_custom_endpoints_keep_their_path(self, request):
        request.return_value = response({})
        CustomEndpointCall('org1', CREDENTIALS).call('GET', '/api/v1/who', headers=None, parameters=None)
        self.assertEqual(request.call_args.kwargs['url'], 'https://app.air-core.io/api/v1/who')


class TestAutomations(unittest.TestCase):

    @mock.patch('deepint.util.request.requests.request')
    def test_list_with_kind(self, request):
        request.return_value = response({'items': [FLOW_ITEM]})
        items = workspace().automations.list(kind='flow')
        kwargs = request.call_args.kwargs
        self.assertEqual(kwargs['method'], 'GET')
        self.assertEqual(kwargs['url'], 'https://app.air-core.io/api/v2/workspace/ws1/automations')
        self.assertEqual(kwargs['params'], {'kind': 'flow'})
        self.assertEqual(kwargs['headers']['x-deepint-organization'], 'org1')
        self.assertEqual(items[0].kind, AutomationKind.flow)
        self.assertEqual(items[0].source_id, 's1')
        self.assertEqual(items[0].last_outcome, {'status': 'ok'})
        workspace().automations.list()
        self.assertEqual(request.call_args.kwargs['params'], {})
        with self.assertRaises(ValueError):
            workspace().automations.list(kind='alert')

    @mock.patch('deepint.util.request.requests.request')
    def test_fetch_all_filters_by_kind(self, request):
        request.return_value = response({'items': [FLOW_ITEM, dict(NOTICE, trigger=None, source='s1')]})
        ws = workspace()
        notices = list(ws.automations.fetch_all(kind='notice'))
        self.assertEqual([a.info.automation_id for a in notices], ['a1'])
        self.assertTrue(notices[0].is_notice)
        self.assertEqual(len(list(ws.automations.fetch_all())), 2)
        self.assertEqual(request.call_count, 1)

    @mock.patch('deepint.util.request.requests.request')
    def test_fetch_by_id_and_name(self, request):
        request.return_value = response(NOTICE)
        a = workspace().automations.fetch(automation_id='a1')
        self.assertEqual(request.call_args.kwargs['url'], 'https://app.air-core.io/api/v2/workspace/ws1/automations/a1')
        self.assertEqual(a.info.condition['rules'][0]['op'], 'gt')
        self.assertEqual(a.info.automation_type, 'update')

        ws = workspace()
        request.side_effect = [response({'items': [dict(NOTICE)]}), response(NOTICE)]
        self.assertEqual(ws.automations.fetch(name='Hot').info.automation_id, 'a1')
        request.side_effect = None
        self.assertIsNone(ws.automations.fetch(name='Other'))

    @mock.patch('deepint.util.request.requests.request')
    def test_create_reports_how_it_was_saved(self, request):
        request.return_value = response({'kind': 'notice', 'saved_as': {'kind': 'notice', 'reason': 'SIMPLE'},
                                         'automation': NOTICE, 'webhook_secret': 'whsec', 'warnings': ['LIST_EMPTY']})
        a = workspace().automations.create(name='Hot', trigger={'type': 'source_updated', 'source': 's1'},
                                           condition=NOTICE['condition'],
                                           actions=[{'type': 'email', 'to': 'list'},
                                                    {'type': 'webhook', 'url': 'https://hooks.example.com/x'}])
        kwargs = request.call_args.kwargs
        self.assertEqual(kwargs['method'], 'POST')
        self.assertTrue(kwargs['url'].endswith('/api/v2/workspace/ws1/automations'))
        self.assertEqual(set(kwargs['json']), {'name', 'trigger', 'condition', 'actions'})
        self.assertEqual(a.saved_as, {'kind': 'notice', 'reason': 'SIMPLE'})
        self.assertEqual(a.info.automation_id, 'a1')
        self.assertTrue(a.is_notice)
        self.assertEqual(a.webhook_secret, 'whsec')
        self.assertEqual(a.warnings, ['LIST_EMPTY'])

    @mock.patch('deepint.util.request.requests.request')
    def test_update_sends_only_what_changes(self, request):
        saved = {'kind': 'flow', 'saved_as': {'kind': 'flow', 'reason': 'EDITING'},
                 'automation': dict(FLOW_ITEM, name='Nightly')}
        request.return_value = response(saved)
        a = Automation('org1', 'ws1', CREDENTIALS, AutomationInfo('f1', AutomationKind.flow))
        out = a.update(name='Nightly', enabled=False)
        kwargs = request.call_args.kwargs
        self.assertEqual(kwargs['method'], 'PUT')
        self.assertTrue(kwargs['url'].endswith('/api/v2/workspace/ws1/automations/f1'))
        self.assertEqual(kwargs['json'], {'name': 'Nightly', 'enabled': False})
        self.assertEqual(out, saved)
        self.assertEqual(a.info.name, 'Nightly')
        workspace().automations.update('f1', description='d')
        self.assertEqual(request.call_args.kwargs['json'], {'description': 'd'})
        with self.assertRaises(TypeError):
            workspace().automations.update('f1', color='#fff')

    @mock.patch('deepint.util.request.requests.request')
    def test_editing_never_changes_the_kind(self, request):
        request.return_value = response({'code': 'NOT_A_NOTICE', 'message': 'This automation is a simple notice'}, 409)
        a = Automation('org1', 'ws1', CREDENTIALS, AutomationInfo('a1', AutomationKind.notice))
        with self.assertRaises(DeepintHTTPError) as ctx:
            a.update(model='m1')
        self.assertEqual(ctx.exception.code, 'NOT_A_NOTICE')
        request.return_value = response({'code': 'NOTICE_FIXED', 'message': 'only its name and description'}, 409)
        with self.assertRaises(DeepintHTTPError) as ctx:
            a.update(condition={'kind': 'all'})
        self.assertEqual(ctx.exception.code, 'NOTICE_FIXED')

    @mock.patch('deepint.util.request.requests.request')
    def test_delete_history_and_test(self, request):
        ws = workspace()
        request.return_value = response({'result': 'success', 'kind': 'notice', 'id': 'a1'})
        self.assertEqual(ws.automations.delete('a1')['kind'], 'notice')
        self.assertEqual(request.call_args.kwargs['method'], 'DELETE')
        self.assertTrue(request.call_args.kwargs['url'].endswith('/api/v2/workspace/ws1/automations/a1'))

        request.return_value = response({'kind': 'notice', 'page': 0, 'limit': 10, 'pages_count': 1,
                                         'items_count': 0, 'items': []})
        ws.automations.history('a1', page=0, limit=10)
        self.assertEqual(request.call_args.kwargs['method'], 'GET')
        self.assertTrue(request.call_args.kwargs['url'].endswith('/automations/a1/history'))
        self.assertEqual(request.call_args.kwargs['params'], {'page': 0, 'limit': 10})

        request.return_value = response({'kind': 'notice', 'dry_run': True, 'would_fire': False})
        self.assertTrue(ws.automations.test('a1')['dry_run'])
        self.assertEqual(request.call_args.kwargs['method'], 'POST')
        self.assertTrue(request.call_args.kwargs['url'].endswith('/automations/a1/test'))

    @mock.patch('deepint.util.request.requests.request')
    def test_from_url(self, request):
        request.return_value = response(NOTICE)
        a = Automation.from_url('https://app.air-core.io/api/v2/workspace/ws1/automations/a1', organization_id='org1',
                                credentials=CREDENTIALS)
        self.assertEqual((a.workspace_id, a.info.automation_id), ('ws1', 'a1'))
        self.assertEqual(parse_url('https://app.air-core.io/api/v2/workspace/ws1/source/s1')[0],
                         {'workspace_id': 'ws1', 'source_id': 's1'})

    def test_webhook_signature(self):
        body = b'{"event":"automation"}'
        header = 'sha256=' + hmac.new(b'secret', body, hashlib.sha256).hexdigest()
        self.assertTrue(Automation.verify_webhook_signature('secret', body, header))
        self.assertFalse(Automation.verify_webhook_signature('other', body, header))
        self.assertFalse(Automation.verify_webhook_signature('secret', body, None))


class TestAlertsRemoved(unittest.TestCase):

    def alert(self):
        info = AlertInfo(alert_id='al1', name='n', description='', created=None, last_modified=None, subscriptions=[],
                         color='#000', alert_type=None, source_id='s', condition={}, time_stall=None)
        return Alert('org1', 'ws1', CREDENTIALS, info)

    @mock.patch('deepint.util.request.requests.request')
    def test_alert_methods_raise_without_calling_the_api(self, request):
        a = self.alert()
        ws = workspace()
        calls = [
            (lambda: Alert.build('org1', 'ws1', 'al1', credentials=CREDENTIALS), 'Automation.build'),
            (lambda: Alert.from_url('https://app.air-core.io/api/v1/workspace/ws1/alerts/al1', 'org1', CREDENTIALS),
             'Automation.from_url'),
            (a.load, 'Automation.load()'),
            (lambda: a.update(name='x'), 'Automation.update'),
            (a.delete, 'Automation.delete()'),
            (a.instances.fetch, 'Automation.history()'),
            (a.webhook.get, 'Automation.load()'),
            (lambda: a.webhook.set('https://hooks.example.com/x'), 'Automation.update'),
            (a.webhook.delete, 'Automation.update'),
            (a.webhook.rotate_secret, 'rotate_secret=True'),
            (a.webhook.test, 'Automation.test()'),
            (ws.alerts.load, 'workspace.automations.load()'),
            (lambda: ws.alerts.create('n', '', [], '#000', None, 's'), 'workspace.automations.create'),
            (lambda: ws.alerts.fetch(alert_id='al1'), 'workspace.automations.fetch'),
            (lambda: list(ws.alerts.fetch_all()), "workspace.automations.fetch_all(kind='notice')"),
        ]
        for call, replacement in calls:
            with self.assertRaises(DeepintAlertsRemovedError) as ctx:
                call()
            e = ctx.exception
            self.assertEqual(e.code, 'ALERTS_REMOVED')
            self.assertIn(replacement, e.replacement)
            self.assertIn('410', e.message)
            self.assertIn(replacement, str(e))
            # an alert error is an error of the SDK and of the API
            self.assertIsInstance(e, DeepintHTTPError)
            self.assertIsInstance(e, DeepintBaseError)
        request.assert_not_called()

    @mock.patch('deepint.util.request.requests.request')
    def test_410_of_the_api(self, request):
        request.return_value = response({'code': 'ALERTS_REMOVED', 'message': 'The alerts were removed from API v1.',
                                         'docs': 'https://app.air-core.io/docs/api#tag-automations',
                                         'replacement': 'GET /api/v2/workspace/ws1/automations'}, 410)
        with self.assertRaises(DeepintAlertsRemovedError) as ctx:
            CustomEndpointCall('org1', CREDENTIALS).call('GET', '/api/v1/workspace/ws1/alerts', headers=None,
                                                          parameters=None)
        self.assertEqual(ctx.exception.replacement, 'GET /api/v2/workspace/ws1/automations')
        self.assertEqual(ctx.exception.docs, 'https://app.air-core.io/docs/api#tag-automations')
        # not retried
        self.assertEqual(request.call_count, 1)

    def test_signature_check_of_the_alerts_still_works(self):
        body = b'{"event":"alert"}'
        header = 'sha256=' + hmac.new(b'secret', body, hashlib.sha256).hexdigest()
        self.assertTrue(AlertWebhook.verify_signature('secret', body, header))

    @mock.patch('deepint.util.request.requests.request')
    def test_workspace_build_loads_automations_not_alerts(self, request):
        def answer(method, url, **kwargs):
            if url.endswith('/workspace/ws1'):
                return response({'id': 'ws1', 'name': 'w', 'sources_count': 0, 'dashboards_count': 0,
                                 'visualizations_count': 0, 'models_count': 0, 'size_bytes': 0})
            if url.endswith('/emails'):
                return response([])
            return response({'items': [], 'page': 0, 'pages_count': 1})
        request.side_effect = answer
        Workspace.build('org1', 'ws1', credentials=CREDENTIALS)
        urls = [c.kwargs['url'] for c in request.call_args_list]
        self.assertIn('https://app.air-core.io/api/v2/workspace/ws1/automations', urls)
        self.assertFalse(any('/alerts' in u for u in urls))
        self.assertTrue(all('/api/v2/' in u for u in urls))


if __name__ == '__main__':
    unittest.main()
