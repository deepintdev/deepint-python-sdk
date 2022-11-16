#!usr/bin/python

# Copyright 2023 Deep Intelligence
# See LICENSE for details.

import json
import os
import platform
import uuid
from datetime import datetime, timedelta
from time import sleep

import pandas as pd
import pytest
from deepint import *

# create test credentials

TEST_CSV = None
TEST_CSV2 = None
TEST_EMAIL = None
DEEPINT_TOKEN = None
DEEPINT_ORGANIZATION = None
TEST_EXTERNAL_SOURCE_URL = None
TEST_CREDENTIALS_FILE = 'test_config.json'

try:
    with open(TEST_CREDENTIALS_FILE, 'r') as f:
        raw_content = f.read()
        content = json.loads(raw_content)
    TEST_CSV = content.get("TEST_CSV")
    TEST_CSV2 = content.get("TEST_CSV2")
    TEST_EMAIL = content.get("TEST_EMAIL")
    DEEPINT_TOKEN = content.get("DEEPINT_TOKEN")
    DEEPINT_ORGANIZATION = content.get("DEEPINT_ORGANIZATION")
    TEST_EXTERNAL_SOURCE_URL = content.get("TEST_EXTERNAL_SOURCE_URL")
except:
    print(f'If you are in a local enviroment, you can load your test credentials from the \'{TEST_CREDENTIALS_FILE}\' file.')

if TEST_CSV is None:
    TEST_CSV = 'https://people.sc.fsu.edu/~jburkardt/data/csv/letter_frequency.csv'

if TEST_CSV2 is None:
    TEST_CSV2 = 'https://people.sc.fsu.edu/~jburkardt/data/csv/letter_frequency.csv'

if TEST_EMAIL is None:
    TEST_EMAIL = 'test@deepint.net'

if DEEPINT_TOKEN is None:
    DEEPINT_TOKEN = os.environ.get('DEEPINT_TOKEN')

if DEEPINT_ORGANIZATION is None:
    DEEPINT_ORGANIZATION = os.environ.get('DEEPINT_ORGANIZATION')

if TEST_EXTERNAL_SOURCE_URL is None:
    TEST_EXTERNAL_SOURCE_URL = os.environ.get('TEST_EXTERNAL_SOURCE_URL')

# objects names
PYTHON_VERSION_NAME = platform.python_version()
TEST_WS_NAME = f'{PYTHON_VERSION_NAME}_automated_python_sdk_test_ws'
TEST_WS_DESC = f'{PYTHON_VERSION_NAME}_Automated python SDK test ws'
TEST_SRC_NAME = f'{PYTHON_VERSION_NAME}_automated_python_sdk_test_src'
TEST_SRC_DESC = f'{PYTHON_VERSION_NAME}_Automated python SDK test src'
TEST_MODEL_NAME = f'{PYTHON_VERSION_NAME}_automated_python_sdk_test_model'
TEST_MODEL_DESC = f'{PYTHON_VERSION_NAME}_Automated python SDK test model'
TEST_ALERT_NAME = f'{PYTHON_VERSION_NAME}_automated_python_sdk_test_alert'
TEST_ALERT_DESC = f'{PYTHON_VERSION_NAME}_Automated python SDK test alert'
TEST_ALERT_SUBSCRIPTIONS = [f'{PYTHON_VERSION_NAME}_example@example.com']
TEST_VISUALIZATION_NAME = f'{PYTHON_VERSION_NAME}_automated_python_sdk_test_visualization'
TEST_VISUALIZATION_DESC = f'{PYTHON_VERSION_NAME}_Automated python SDK test visualization'
TEST_DASHBOARD_NAME = f'{PYTHON_VERSION_NAME}_automated_python_sdk_test_dashboard'
TEST_DASHBOARD_DESC = f'{PYTHON_VERSION_NAME}_Automated python SDK test dashboard'

# credentials load
os.environ["DEEPINT_TOKEN"] = DEEPINT_TOKEN
os.environ["DEEPINT_ORGANIZATION"] = DEEPINT_ORGANIZATION


def serve_name(object_type):
    return f'{object_type}_{uuid.uuid4()}'[:70]


def test_credentials_load():

    # test token given in enviroment
    os.environ["DEEPINT_TOKEN"] = "token"
    c = Credentials.build()
    del os.environ['DEEPINT_TOKEN']
    assert (c.token == "token")

    # test token given in credentials file
    credentials_file = f'{os.path.expanduser("~")}/.deepint.ini'
    with open(credentials_file, 'w+') as f:
        f.write("[DEFAULT]\ntoken = file")
    c = Credentials.build()
    os.unlink(credentials_file)
    assert (c.token == "file")

    # test token given locally
    c = Credentials.build(token='local')
    assert (c.token == "local")

    # set token to default
    os.environ["DEEPINT_TOKEN"] = DEEPINT_TOKEN
    os.environ["DEEPINT_ORGANIZATION"] = DEEPINT_ORGANIZATION


def test_organization_CRUD():
    # create
    org = Organization.build(organization_id=DEEPINT_ORGANIZATION)
    org.clean()

    assert (org.account is not None)
    assert (not list(org.workspaces.fetch_all()))


def test_workspace_CRUD():

    # load organization
    org = Organization.build(organization_id=DEEPINT_ORGANIZATION)

    # create
    ws_name = serve_name(TEST_WS_NAME)
    original_ws = org.workspaces.create(name=ws_name, description=TEST_WS_DESC)

    # retrieve (single)
    retrieved_ws = Workspace.build(organization_id=DEEPINT_ORGANIZATION,
                                   credentials=org.credentials, workspace_id=original_ws.info.workspace_id)
    assert (
        retrieved_ws.info.workspace_id == original_ws.info.workspace_id and retrieved_ws.info.name == ws_name and retrieved_ws.info.description == TEST_WS_DESC)

    # update
    original_ws.update(name=f'{ws_name}2', description=f'{TEST_WS_DESC}2')
    retrieved_ws.load()
    assert (retrieved_ws.info.name ==
            f'{ws_name}2' and retrieved_ws.info.description == f'{TEST_WS_DESC}2')

    # retrieve (in organization)
    selected_ws = org.workspaces.fetch(
        workspace_id=original_ws.info.workspace_id)
    assert (selected_ws is not None)

    # delete
    original_ws.delete()
    try:
        ws = Workspace.build(organization_id=DEEPINT_ORGANIZATION,
                             credentials=org.credentials, workspace_id=original_ws.info.workspace_id)
        assert False
    except DeepintHTTPError:
        assert True

    # export
    ws_name = serve_name(TEST_WS_NAME)
    ws = org.workspaces.create(name=ws_name, description=TEST_WS_DESC)
    zip_path = ws.export(wait_for_download=True)
    assert (os.path.isfile(zip_path) == True)
    os.unlink(zip_path)

    task = ws.export(wait_for_download=False)
    zip_path = ws.export(task=task)
    assert (os.path.isfile(zip_path) == True)
    os.unlink(zip_path)

    # import
    ws_name = serve_name(TEST_WS_NAME)
    ws = org.workspaces.create(name=ws_name, description=TEST_WS_DESC)
    zip_path = ws.export(wait_for_download=True)
    assert (os.path.isfile(zip_path) == True)
    workspace = org.workspaces.import_ws(
        name=ws_name, description=TEST_WS_DESC, file_path=zip_path, wait_for_creation=True)
    assert (workspace.info.workspace_id != ws.info.workspace_id)
    os.unlink(zip_path)

    # clone
    ws_name = serve_name(TEST_WS_NAME)
    ws = org.workspaces.create(name=ws_name, description=TEST_WS_DESC)
    new_ws = ws.clone()
    assert(ws != new_ws)

    # TODO: crud emails

    # TODO: fetch_iframe_token

    # create if not exists
    ws_name = serve_name(TEST_WS_NAME)
    ws = org.workspaces.create_if_not_exists(ws_name)
    ws1 = org.workspaces.create_if_not_exists(ws_name)
    assert (ws == ws1)
    ws.delete()


def test_source_CRUD():
    # load organization and create workspace
    org = Organization.build(organization_id=DEEPINT_ORGANIZATION)
    ws = org.workspaces.create(name=serve_name(
        TEST_WS_NAME), description=TEST_WS_DESC)

    # create empty source
    src_name = serve_name(TEST_SRC_NAME)
    empty_source = ws.sources.create(
        name=src_name, description=TEST_SRC_DESC, features=[])
    assert (not empty_source.features.fetch_all())
    empty_source.delete()

    # create source
    data = pd.read_csv(TEST_CSV)
    src_name = serve_name(TEST_SRC_NAME)
    source = ws.sources.create_and_initialize(
        name=src_name, description=TEST_SRC_DESC, data=data)

    # retrieve
    retrieved_src = Source.build(organization_id=DEEPINT_ORGANIZATION, source_id=source.info.source_id, workspace_id=ws.info.workspace_id,
                                 credentials=org.credentials)
    assert (
        retrieved_src.info.source_id == source.info.source_id and retrieved_src.info.name == src_name and retrieved_src.info.description == TEST_SRC_DESC)

    # update source info
    source.update(name=f'{src_name}2', description=f'{TEST_SRC_DESC}2')
    retrieved_src.load()
    assert (retrieved_src.info.name ==
            f'{src_name}2' and retrieved_src.info.description == f'{TEST_SRC_DESC}2')

    # update features
    feature = source.features.fetch(index=0, force_reload=True)
    feature.feature_type = FeatureType.date
    task = source.features.update()
    task.resolve()
    updated_feature = source.features.fetch(
        index=feature.index, force_reload=True)
    assert (feature.index == updated_feature.index and FeatureType.date ==
            updated_feature.feature_type)

    # update instances
    data = pd.read_csv(TEST_CSV)
    task = source.instances.update(data=data)
    task.resolve()

    # retrieve instances
    retrieved_data = source.instances.fetch()
    assert (len(retrieved_data) >= len(data))

    # delete instances
    task = source.instances.clean()
    task.resolve()

    # retrieve instances
    retrieved_data = source.instances.fetch()
    assert (retrieved_data.empty == True)

    # delete source
    source.delete()
    try:
        _ = Source.build(organization_id=DEEPINT_ORGANIZATION, source_id=source.info.source_id, workspace_id=ws.info.workspace_id,
                           credentials=org.credentials)
        assert False
    except DeepintHTTPError:
        assert True

    # create if not exists
    src_name = serve_name(TEST_SRC_NAME)
    source = ws.sources.create_if_not_exists(src_name)
    source1 = ws.sources.create_if_not_exists(src_name)
    assert (source == source1)
    source.delete()

    # create if not exists (with initialization and update)
    data2 = pd.read_csv(TEST_CSV2)
    src_name = serve_name(TEST_SRC_NAME)
    source = ws.sources.create_else_update(src_name, data)
    source1 = ws.sources.create_else_update(src_name, data2, replace=True)
    assert (source == source1)
    assert (source.features == source1.features)

    # clone
    cloned_source = source.clone(name='cloned source')
    assert(cloned_source != source)

    cloned_source.delete()

    #  create derived
    src_name = serve_name(TEST_SRC_NAME)
    derived_source = ws.sources.create_derived(name=src_name, description=TEST_WS_DESC, derived_type=DerivedSourceType.filter, origin_source_id=source.info.source_id, origin_source_b_id=None, query={}, features=source.features.fetch_all(), feature_a=None, feature_b=None, is_encrypted=False, is_shuffled=False, wait_for_creation=True)
    derived_source.delete()

    source.delete()

    # create autoupdated and test configuration
    src_name = serve_name(TEST_SRC_NAME)
    auto_updated_source = ws.sources.create_autoupdated(
        name=src_name, description=TEST_WS_DESC, source_type=SourceType.url_json, url='https://app.deepint.net/static/sources/iris.json', json_fields=["sepalLength", "sepalWidth", "petalLength", "petalWidth", "species"], json_prefix=None, http_headers=None, ignore_security_certificates=True, is_single_json_obj=False, wait_for_creation=True
    )

    auto_updated_source.update_actualization_config(auto_update=False)
    configuration = auto_updated_source.fetch_actualization_config()
    assert(configuration['enabled'] == False)

    auto_updated_source.delete()

    # delete workspace
    ws.delete()


def test_real_time_source_CRUD():

    # load organization and create workspace
    org = Organization.build(organization_id=DEEPINT_ORGANIZATION)
    ws = org.workspaces.create(name=serve_name(TEST_WS_NAME), description=TEST_WS_DESC)

    # create base source to extract feature info
    data = pd.read_csv(TEST_CSV)
    src_name = serve_name(TEST_SRC_NAME)
    source = ws.sources.create_and_initialize(name=src_name, description=TEST_SRC_DESC, data=data, wait_for_initialization=True)

    # create source
    src_name = serve_name(TEST_SRC_NAME)

    features = source.features.fetch_all(force_reload=True)
    features[0].feature_type = FeatureType.date
    features[0].name = 'timestamp'

    rt_source = ws.sources.create_real_time(name=src_name, description=TEST_SRC_DESC, features=features)

    # update connection
    connection_value = 10
    rt_source.update_connection(max_age=connection_value, regenerate_password=True)

    # retrieve connection
    connection_info = rt_source.fetch_connection()
    assert(connection_info['max_age'] == connection_value)

    # update instances
    data = data.rename(columns={list(data.columns)[0]: 'timestamp'})
    rt_source.instances.update(data=data)

    # retrieve instances
    instances = rt_source.instances.fetch()
    assert (len(instances) > 0)

    # clear queued instances
    to_time = datetime.now()
    from_time = datetime.now() - timedelta(minutes=5)
    rt_source.instances.clear_queued_instances(from_time=from_time, to_time=to_time)

    # delete workspace
    ws.delete()


def test_external_source_CRUD():

    # load organization and create workspace
    org = Organization.build(organization_id=DEEPINT_ORGANIZATION)
    ws = org.workspaces.create(name=serve_name(TEST_WS_NAME), description=TEST_WS_DESC)

    # create source
    src_name = serve_name(TEST_SRC_NAME)
    features = [SourceFeature.from_dict(f) for f in [

        {"index": 0, "name": "sepalLength", "type": "numeric", "dateFormat": "", "indexed": True}, {"index": 1, "name": "sepalWidth", "type": "numeric", "dateFormat": "", "indexed": True}, {"index": 2, "name": "petalLength", "type": "numeric", "dateFormat": "", "indexed": True}, {"index": 3, "name": "petalWidth", "type": "numeric", "dateFormat": "", "indexed": True}, {"index": 4, "name": "species", "type": "nominal", "dateFormat": "", "indexed": True}
    ]]
    external_source = ws.sources.create_external(name=src_name, description=TEST_SRC_DESC, url=TEST_EXTERNAL_SOURCE_URL, features=features)

    # update instances
    try:

        data = [{
            "sepalLength": 4.6,
            "sepalWidth": 3.2,
            "petalLength": 1.4,
            "petalWidth": 0.2,
            "species": "setosa"
        }]
        data = pd.DataFrame(data=data)
        external_source.instances.update(data=data)

        assert False
    except DeepintBaseError:
        assert True

    # connection update and retrieval
    external_source.update_connection(url=TEST_EXTERNAL_SOURCE_URL)
    connection_url = external_source.fetch_connection()
    assert(connection_url == TEST_EXTERNAL_SOURCE_URL)


def test_task_CRUD():

    # load organization and create workspace and source
    org = Organization.build(organization_id=DEEPINT_ORGANIZATION)
    ws_name = serve_name(TEST_WS_NAME)
    ws = org.workspaces.create(name=ws_name, description=TEST_WS_DESC)
    data = pd.read_csv(TEST_CSV)
    src_name = serve_name(TEST_SRC_NAME)
    source = ws.sources.create_and_initialize(
        name=src_name, description=TEST_SRC_DESC, data=data)

    # retrieve
    tasks = ws.tasks.fetch_all(force_reload=True)
    assert (len(list(tasks)) >= 1)

    # wait for task
    task = source.instances.update(data=data)
    task.resolve()
    assert (task.info.status == TaskStatus.success)

    # delete task
    try:
        data = pd.read_csv(TEST_CSV)
        task = source.instances.update(data=data)
        task.delete()
        # wait a little until task is stopped
        sleep(5)
        task.load()
        assert (task.info.status ==
                TaskStatus.failed or task.info.status == TaskStatus.success)
    except:
        pass

    # delete workspace
    ws.delete()


def test_alert_CRUD():

    # load organization and create workspace and source
    org = Organization.build(organization_id=DEEPINT_ORGANIZATION)
    ws_name = serve_name(TEST_WS_NAME)
    ws = org.workspaces.create(name=ws_name, description=TEST_WS_DESC)
    src_name = serve_name(TEST_SRC_NAME)
    source = ws.sources.create(
        name=src_name, description=TEST_SRC_DESC, features=[])

    # create
    alert_name = serve_name(TEST_ALERT_NAME)
    alert = ws.alerts.create(name=alert_name, description=TEST_ALERT_DESC, subscriptions=TEST_ALERT_SUBSCRIPTIONS,
                             color='#FF00FF', alert_type=AlertType.update, source_id=source.info.source_id)

    # retrieve (single)
    retrieved_alert = Alert.build(organization_id=DEEPINT_ORGANIZATION, credentials=org.credentials, workspace_id=ws.info.workspace_id,
                                  alert_id=alert.info.alert_id)
    assert (
        retrieved_alert.info.alert_id == alert.info.alert_id and retrieved_alert.info.name == alert_name and retrieved_alert.info.description == TEST_ALERT_DESC)

    # update
    retrieved_alert.update(name=f'{alert_name}2',
                           description=f'{TEST_ALERT_DESC}2')
    retrieved_alert.load()
    assert (
        retrieved_alert.info.name == f'{alert_name}2' and retrieved_alert.info.description == f'{TEST_ALERT_DESC}2')

    # retrieve (in organization)
    selected_alert = ws.alerts.fetch(
        alert_id=retrieved_alert.info.alert_id, force_reload=True)
    assert (selected_alert is not None)

    # delete
    alert.delete()
    try:
        _ = Alert.build(credentials=org.credentials, organization_id=DEEPINT_ORGANIZATION, workspace_id=retrieved_alert.info.alert_id,
                        alert_id=alert.info.alert_id)
        assert False
    except DeepintHTTPError:
        assert True

    # delete workspace
    ws.delete()


def test_model_CRUD():

    # load organization, create workspace and source (with initialization)
    org = Organization.build(organization_id=DEEPINT_ORGANIZATION)
    ws_name = serve_name(TEST_WS_NAME)
    ws = org.workspaces.create(name=ws_name, description=TEST_WS_DESC)
    data = pd.read_csv(TEST_CSV).dropna()
    src_name = serve_name(TEST_SRC_NAME)
    source = ws.sources.create_and_initialize(name=src_name, description=TEST_SRC_DESC, data=data, wait_for_initialization=True)

    # create model
    target_feature = [f for f in source.features.fetch_all(
    ) if f.feature_type == FeatureType.nominal][0]
    model_name = serve_name(TEST_MODEL_NAME)

    model = ws.models.create(name=model_name, description=TEST_MODEL_DESC, model_type=ModelType.classifier, method=ModelMethod.bayes, source=source, target_feature_name=target_feature.name, wait_for_model_creation=True)

    # retrieve
    retrieved_model = Model.build(organization_id=DEEPINT_ORGANIZATION, model_id=model.info.model_id, workspace_id=ws.info.workspace_id,
                                  credentials=org.credentials)
    assert (
        retrieved_model.info.model_id == model.info.model_id and retrieved_model.info.name == model_name and retrieved_model.info.description == TEST_MODEL_DESC)

    # update source info
    model.update(name=f'{model_name}2', description=f'{TEST_MODEL_DESC}2')
    retrieved_model.load()
    assert (
        retrieved_model.info.name == f'{model_name}2' and retrieved_model.info.description == f'{TEST_MODEL_DESC}2')

    # get model evaluation
    evaluation = model.predictions.evaluation()
    assert (evaluation is not None)

    # predict one instance
    data_one_instance = data.head(n=1)
    del data_one_instance[target_feature.name]
    prediction_result = model.predictions.predict(data_one_instance)
    assert (target_feature.name in prediction_result.columns and prediction_result[target_feature.name].iloc[
        0] is not None)

    # predict batch
    data_some_instances = data.head(n=25)
    del data_some_instances[target_feature.name]
    prediction_result = model.predictions.predict_batch(data_some_instances)
    assert (target_feature.name in prediction_result.columns and prediction_result[target_feature.name].iloc[
        0] is not None)

    # vary model
    vary_target_feature = [f for f in source.features.fetch_all(
    ) if f.feature_type == FeatureType.numeric and f.name != target_feature.name][0]
    variations = [float(i) / 255 for i in range(255)]
    prediction_result = model.predictions.predict_unidimensional(data_one_instance, variations,
                                                                 vary_target_feature.name)
    assert (target_feature.name in prediction_result.columns and len(
        prediction_result) == 255)

    # delete source
    model.delete()
    try:
        _ = Model.build(organization_id=DEEPINT_ORGANIZATION, model_id=model.info.model_id,
                        workspace_id=ws.info.workspace_id, credentials=org.credentials)
        assert False
    except DeepintHTTPError:
        assert True

    # delete workspace
    ws.delete()


def test_visualization_CRUD():

    # load organization
    org = Organization.build()

    # create workspace
    ws_name = serve_name(TEST_WS_NAME)
    ws = org.workspaces.create(name=ws_name, description=TEST_WS_DESC)

    # create source
    data = pd.read_csv(TEST_CSV)
    src_name = serve_name(TEST_SRC_NAME)
    source = ws.sources.create_and_initialize(
        name=src_name, description=TEST_SRC_DESC, data=data)

    # create visualization
    visualization_name = serve_name(TEST_VISUALIZATION_NAME)
    vis = ws.visualizations.create(name=visualization_name, description=TEST_VISUALIZATION_DESC, privacy='public',
                                   source=source.info.source_id, configuration={})

    # retrieve
    retrieved_visualization = Visualization.build(visualization_id=vis.info.visualization_id, workspace_id=ws.info.workspace_id,
                                                  credentials=org.credentials, organization_id=DEEPINT_ORGANIZATION)
    assert (
        retrieved_visualization.info.visualization_id == vis.info.visualization_id and retrieved_visualization.info.name == visualization_name
        and retrieved_visualization.info.description == TEST_VISUALIZATION_DESC)

    # update visualization
    vis.update(name=f'{visualization_name}2',
               description=f'{TEST_VISUALIZATION_DESC}2', source=source.info.source_id)
    retrieved_visualization.load()
    assert (retrieved_visualization.info.name == f'{visualization_name}2'
            and retrieved_visualization.info.description == f'{TEST_VISUALIZATION_DESC}2')

    # clone
    visualization_name = serve_name(TEST_VISUALIZATION_NAME)
    vis = ws.visualizations.create(name=visualization_name, description=TEST_VISUALIZATION_DESC, privacy='public',
                                   source=source.info.source_id, configuration={})
    new_vis = vis.clone()
    assert(vis != new_vis)
    new_vis.delete()

    # create token
    url, token = vis.fetch_iframe_token()
    assert(token in url)

    # delete visualization
    vis.delete()

    # delete workspace
    ws.delete()


def test_dashboard_CRUD():

    # load organization
    org = Organization.build(organization_id=DEEPINT_ORGANIZATION)

    # create workspace
    ws_name = serve_name(TEST_WS_NAME)
    ws = org.workspaces.create(name=ws_name, description=TEST_WS_DESC)

    # create dashboard
    dashboard_name = serve_name(TEST_DASHBOARD_NAME)
    dash = ws.dashboards.create(name=dashboard_name, description=TEST_DASHBOARD_DESC, privacy='public',
                                share_opt=" ", ga_id=" ", restricted=True, configuration={})

    # retrieve
    retrieved_dashboard = Dashboard.build(organization_id=DEEPINT_ORGANIZATION, workspace_id=ws.info.workspace_id,
                                          dashboard_id=dash.info.dashboard_id, credentials=org.credentials)
    assert (retrieved_dashboard.info.dashboard_id == dash.info.dashboard_id and retrieved_dashboard.info.name == dash.info.name
            and retrieved_dashboard.info.description == TEST_DASHBOARD_DESC)

    # update dashboard
    dash.update(name=f'{dashboard_name}2',
                description=f'{TEST_DASHBOARD_DESC}2')
    retrieved_dashboard.load()
    assert (retrieved_dashboard.info.name ==
            f'{dashboard_name}2' and retrieved_dashboard.info.description == f'{TEST_DASHBOARD_DESC}2')

    # clone
    dashboard_name = serve_name(TEST_DASHBOARD_NAME)
    dash = ws.dashboards.create(name=dashboard_name, description=TEST_DASHBOARD_DESC, privacy='public',
                                share_opt=" ", ga_id=" ", restricted=True, configuration={})
    new_dash = dash.clone()
    assert(dash != new_dash)
    new_dash.delete()

    # create token
    url, token = dash.fetch_iframe_token()
    assert(token in url)

    # delete dashboard
    dash.delete()

    # delete workspace
    ws.delete()


def test_emails_CRUD():

    # create organization and workspace
    org = Organization.build(organization_id=DEEPINT_ORGANIZATION)
    workspace = org.workspaces.create(name=serve_name(TEST_WS_NAME), description=TEST_WS_DESC)

    # check fetch method
    assert(not workspace.emails.fetch_all())

    # create email
    new_email = workspace.emails.create(email=TEST_EMAIL)
    assert(new_email['email'] == TEST_EMAIL)
    assert(new_email['is_validated'] == False)

    # check fetch all
    emails = workspace.emails.fetch_all(force_reload=True)
    assert(len(emails) == 1)
    assert(workspace.emails.fetch(email=TEST_EMAIL) is not None)

    # check delete
    workspace.emails.delete(email=TEST_EMAIL)
    try:
        workspace.emails.delete(email=TEST_EMAIL)
        assert False
    except DeepintBaseError:
        assert True
    assert(workspace.emails.fetch(email=TEST_EMAIL) is None)


def test_url_parser():

    # load organization and create workspace, source and alert
    org = Organization.build(organization_id=DEEPINT_ORGANIZATION)

    workspace = org.workspaces.create(
        name=serve_name(TEST_WS_NAME), description=TEST_WS_DESC)

    data = pd.read_csv(TEST_CSV).dropna()
    source = workspace.sources.create_and_initialize(
        name=serve_name(TEST_SRC_NAME), description=TEST_SRC_DESC, data=data)

    target_feature = [f for f in source.features.fetch_all() if f.feature_type == FeatureType.nominal][0]
    model_name = serve_name(TEST_MODEL_NAME)
    model = workspace.models.create(name=model_name, description=TEST_MODEL_DESC, model_type=ModelType.classifier,
                                    method=ModelMethod.bayes, source=source, target_feature_name=target_feature.name, wait_for_model_creation=True)

    alert = workspace.alerts.create(name=serve_name(TEST_ALERT_NAME), description=TEST_ALERT_DESC,
                                    subscriptions=TEST_ALERT_SUBSCRIPTIONS,
                                    color='#FF00FF', alert_type=AlertType.update, source_id=source.info.source_id)

    task = list(workspace.tasks.fetch_all(force_reload=True))[0]

    visualization = workspace.visualizations.create(name=serve_name(TEST_VISUALIZATION_NAME), description=TEST_VISUALIZATION_DESC,
                                                    privacy='public', source=source.info.source_id)

    dashboard = workspace.dashboards.create(name=serve_name(TEST_DASHBOARD_NAME), description=TEST_DASHBOARD_DESC, privacy='public',
                                            share_opt=" ", ga_id=" ", restricted=True, configuration={})

    # extract id
    t_id = task.info.task_id
    a_id = alert.info.alert_id
    m_id = model.info.model_id
    src_id = source.info.source_id
    ws_id = workspace.info.workspace_id
    org_id = workspace.organization_id
    v_id = visualization.info.visualization_id
    d_id = dashboard.info.dashboard_id

    # check
    ws = Workspace.from_url(
        url=f'https://app.deepint.net/o/{org_id}/workspace?ws={ws_id}', credentials=org.credentials)
    assert (ws.info.workspace_id == ws_id)

    ws = Workspace.from_url(
        url=f'https://app.deepint.net/api/v1/workspace/{ws_id}', organization_id=org_id, credentials=org.credentials)
    assert (ws.info.workspace_id == ws_id)

    src = Source.from_url(url=f'https://app.deepint.net/o/{org_id}/workspace?ws={ws_id}&s=source&i={src_id}',
                          credentials=org.credentials)
    assert (src.workspace_id == ws_id and src.info.source_id == src_id)

    src = Source.from_url(url=f'https://app.deepint.net/api/v1/workspace/{ws_id}/source/{src_id}',
                          organization_id=org_id, credentials=org.credentials)
    assert (src.workspace_id == ws_id and src.info.source_id == src_id)

    a = Alert.from_url(url=f'https://app.deepint.net/o/{org_id}/workspace?ws={ws_id}&s=alert&i={a_id}',
                       credentials=org.credentials)
    assert (a.info.alert_id == a_id)

    a = Alert.from_url(url=f'https://app.deepint.net/api/v1/workspace/{ws_id}/alerts/{a_id}',
                       organization_id=org_id, credentials=org.credentials)
    assert (a.info.alert_id == a_id)

    t = Task.from_url(
        url=f'https://app.deepint.net/o/{org_id}/workspace?ws={ws_id}&s=task&i={t_id}', credentials=org.credentials)
    assert (t.info.task_id == t_id)

    t = Task.from_url(url=f'https://app.deepint.net/api/v1/workspace/{ws_id}/task/{t_id}', organization_id=org_id,
                      credentials=org.credentials)
    assert (t.info.task_id == t_id)

    m = Model.from_url(
        url=f'https://app.deepint.net/o/{org_id}/workspace?ws={ws_id}&s=model&i={m_id}', credentials=org.credentials)
    assert (m.info.model_id == m_id)

    m = Model.from_url(
        url=f'https://app.deepint.net/api/v1/workspace/{ws_id}/models/{m_id}', organization_id=org_id, credentials=org.credentials)
    assert (m.info.model_id == m_id)

    v = Visualization.from_url(url=f'https://app.deepint.net/o/{org_id}/workspace?ws={ws_id}&s=visualization&i={v_id}',
                               credentials=org.credentials)
    assert (v.info.visualization_id == v_id)

    v = Visualization.from_url(url=f'https://app.deepint.net/api/v1/workspace/{ws_id}/visualization/{v_id}',
                               organization_id=org_id, credentials=org.credentials)
    assert (v.info.visualization_id == v_id)

    d = Dashboard.from_url(url=f'https://app.deepint.net/o/{org_id}/workspace?ws={ws_id}&s=dashboard&i={d_id}',
                           credentials=org.credentials)
    assert (d.info.dashboard_id == d_id)

    d = Dashboard.from_url(url=f'https://app.deepint.net/api/v1/workspace/{ws_id}/dashboard/{d_id}',
                           organization_id=org_id, credentials=org.credentials)
    assert (d.info.dashboard_id == d_id)

    # finally delete workspace
    ws.delete()


def test_custom_endpoint():

    # build organization
    org = Organization.build(organization_id=DEEPINT_ORGANIZATION)

    # prepare parameters
    http_operation = 'GET'
    path = '/api/v1/who'

    # perform call
    response = org.endpoint.call(http_operation=http_operation, path=path, headers=None, parameters=None, is_paginated=False)
    assert(response['user_id'] == org.account['user_id'])


@pytest.fixture(scope="session", autouse=True)
def cleanup(request):
    def clean_organization():
        org = Organization.build(organization_id=DEEPINT_ORGANIZATION)
        org.clean()
    request.addfinalizer(clean_organization)


if __name__ == '__main__':

    test_credentials_load()
    test_organization_CRUD()
    test_workspace_CRUD()
    test_source_CRUD()
    test_real_time_source_CRUD()
    test_external_source_CRUD()
    test_task_CRUD()
    test_alert_CRUD()
    test_model_CRUD()
    test_visualization_CRUD()
    test_dashboard_CRUD()
    test_emails_CRUD()
    test_url_parser()
    test_custom_endpoint()
