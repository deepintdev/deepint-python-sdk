#!usr/bin/python

# Copyright 2021 Deep Intelligence
# See LICENSE for details.

import os
import uuid
import platform
import pandas as pd
from time import sleep

from deepint import *

TEST_CSV = os.environ.get('TEST_CSV')
DEEPINT_TOKEN = os.environ.get('DEEPINT_TOKEN')
DEEPINT_ORGANIZATION = os.environ.get('DEEPINT_ORGANIZATION')

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


def serve_name(object_type):
    return f'{object_type}_{uuid.uuid4()}'


def test_credentials_load():
    # test token given in enviroment
    os.environ["DEEPINT_TOKEN"] = "token"
    os.environ["DEEPINT_ORGANIZATION"] = "org"
    c = Credentials.build()
    del os.environ['DEEPINT_TOKEN']
    assert (c.token == "token")
    assert (c.organization == "org")

    # test token given in credentials file
    credentials_file = f'{os.path.expanduser("~")}/.deepint.ini'
    with open(credentials_file, 'w+') as f:
        f.write("[DEFAULT]\ntoken = file\norganization = org")
    c = Credentials.build()
    os.unlink(credentials_file)
    assert (c.token == "file")
    assert (c.organization == "org")

    # test token given locally
    c = Credentials.build(token='local', organization='local_org')
    assert (c.token == "local")
    assert (c.organization == "local_org")

    # set token to default
    os.environ["DEEPINT_TOKEN"] = DEEPINT_TOKEN
    os.environ["DEEPINT_ORGANIZATION"] = DEEPINT_ORGANIZATION


#def test_organization_CRUD():
#    # create
#    org = Organization.build()
#    org.clean()
#
#    assert (org.account is not None)
#    assert (not list(org.workspaces.fetch_all()))


def test_workspace_CRUD():
    # load organization
    org = Organization.build()

    # create
    ws_name = serve_name(TEST_WS_NAME)
    original_ws = org.workspaces.create(name=ws_name, description=TEST_WS_DESC)

    # retrieve (single)
    retrieved_ws = Workspace.build(credentials=org.credentials, workspace_id=original_ws.info.workspace_id)
    assert (
                retrieved_ws.info.workspace_id == original_ws.info.workspace_id and retrieved_ws.info.name == ws_name and retrieved_ws.info.description == TEST_WS_DESC)

    # update
    original_ws.update(name=f'{ws_name}2', description=f'{TEST_WS_DESC}2')
    retrieved_ws.load()
    assert (retrieved_ws.info.name == f'{ws_name}2' and retrieved_ws.info.description == f'{TEST_WS_DESC}2')

    # retrieve (in organization)
    selected_ws = org.workspaces.fetch(workspace_id=original_ws.info.workspace_id)
    assert (selected_ws is not None)

    # delete 
    original_ws.delete()
    try:
        ws = Workspace.build(credentials=org.credentials, workspace_id=original_ws.info.workspace_id)
        assert False
    except DeepintHTTPError:
        assert True

    # create if not exists
    ws_name = serve_name(TEST_WS_NAME)
    ws = org.workspaces.create_if_not_exists(ws_name)
    ws1 = org.workspaces.create_if_not_exists(ws_name)
    assert (ws == ws1)
    ws.delete()


def test_source_CRUD():
    # load organization and create workspace
    org = Organization.build()
    ws = org.workspaces.create(name=serve_name(TEST_WS_NAME), description=TEST_WS_DESC)

    # create empty source
    src_name = serve_name(TEST_SRC_NAME)
    empty_source = ws.sources.create(name=src_name, description=TEST_SRC_DESC, features=[])
    assert (not empty_source.features.fetch_all())
    empty_source.delete()

    # create source
    data = pd.read_csv(TEST_CSV)
    src_name = serve_name(TEST_SRC_NAME)
    source = ws.sources.create_and_initialize(name=src_name, description=TEST_SRC_DESC, data=data)

    # retrieve
    retrieved_src = Source.build(source_id=source.info.source_id, workspace_id=ws.info.workspace_id,
                                 credentials=org.credentials)
    assert (
                retrieved_src.info.source_id == source.info.source_id and retrieved_src.info.name == src_name and retrieved_src.info.description == TEST_SRC_DESC)

    # update source info
    source.update(name=f'{src_name}2', description=f'{TEST_SRC_DESC}2')
    retrieved_src.load()
    assert (retrieved_src.info.name == f'{src_name}2' and retrieved_src.info.description == f'{TEST_SRC_DESC}2')

    # update features
    feature = source.features.fetch(index=0, force_reload=True)
    feature.feature_type = FeatureType.date
    task = source.features.update()
    task.resolve()
    updated_feature = source.features.fetch(index=feature.index, force_reload=True)
    assert (feature.index == updated_feature.index and FeatureType.date == updated_feature.feature_type)

    # update instances
    data = pd.read_csv(TEST_CSV)
    task = source.instances.update(data=data)
    task.resolve()

    # retrieve instances
    retrieved_data = source.instances.fetch()
    assert (len(retrieved_data) == len(data))

    # delete instances
    task = source.instances.clean()
    task.resolve()

    # retrieve instances
    retrieved_data = source.instances.fetch()
    assert (retrieved_data.empty == True)

    # delete source
    source.delete()
    try:
        src = Source.build(source_id=source.info.source_id, workspace_id=ws.info.workspace_id,
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
    src_name = serve_name(TEST_SRC_NAME)
    source = ws.sources.create_else_update(src_name, data)
    source1 = ws.sources.create_else_update(src_name, data)
    assert (source == source1)
    source.delete()

    # delete workspace
    ws.delete()


def test_task_CRUD():
    # load organization and create workspace and source
    org = Organization.build()
    ws_name = serve_name(TEST_WS_NAME)
    ws = org.workspaces.create(name=ws_name, description=TEST_WS_DESC)
    data = pd.read_csv(TEST_CSV)
    src_name = serve_name(TEST_SRC_NAME)
    source = ws.sources.create_and_initialize(name=src_name, description=TEST_SRC_DESC, data=data)

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
        assert (task.info.status == TaskStatus.failed or task.info.status == TaskStatus.success)
    except:
        pass

    # delete workspace
    ws.delete()


def test_alert_CRUD():
    # load organization and create workspace and source
    org = Organization.build()
    ws_name = serve_name(TEST_WS_NAME)
    ws = org.workspaces.create(name=ws_name, description=TEST_WS_DESC)
    src_name = serve_name(TEST_SRC_NAME)
    source = ws.sources.create(name=src_name, description=TEST_SRC_DESC, features=[])

    # create
    alert_name = serve_name(TEST_ALERT_NAME)
    alert = ws.alerts.create(name=alert_name, description=TEST_ALERT_DESC, subscriptions=TEST_ALERT_SUBSCRIPTIONS,
                             color='#FF00FF', alert_type=AlertType.update, source_id=source.info.source_id)

    # retrieve (single)
    retrieved_alert = Alert.build(credentials=org.credentials, workspace_id=ws.info.workspace_id,
                                  alert_id=alert.info.alert_id)
    assert (
                retrieved_alert.info.alert_id == alert.info.alert_id and retrieved_alert.info.name == alert_name and retrieved_alert.info.description == TEST_ALERT_DESC)

    # update
    retrieved_alert.update(name=f'{alert_name}2', description=f'{TEST_ALERT_DESC}2')
    retrieved_alert.load()
    assert (
                retrieved_alert.info.name == f'{alert_name}2' and retrieved_alert.info.description == f'{TEST_ALERT_DESC}2')

    # retrieve (in organization)
    selected_alert = ws.alerts.fetch(alert_id=retrieved_alert.info.alert_id, force_reload=True)
    assert (selected_alert is not None)

    # delete 
    alert.delete()
    try:
        a = Alert.build(credentials=org.credentials, workspace_id=retrieved_alert.info.alert_id,
                        alert_id=alert.info.alert_id)
        assert False
    except DeepintHTTPError:
        assert True

    # delete workspace
    ws.delete()


def test_model_CRUD():
    # load organization, create workspace and source (with initialization)
    org = Organization.build()
    ws_name = serve_name(TEST_WS_NAME)
    ws = org.workspaces.create(name=ws_name, description=TEST_WS_DESC)
    data = pd.read_csv(TEST_CSV)
    src_name = serve_name(TEST_SRC_NAME)
    source = ws.sources.create_and_initialize(name=src_name, description=TEST_SRC_DESC, data=data)

    # create model    
    target_feature = None
    for f in source.features.fetch_all():
        if f.feature_type == FeatureType.numeric:
            target_feature = f
            break
    model_name = serve_name(TEST_MODEL_NAME)
    model = ws.models.create(name=model_name, description=TEST_MODEL_DESC, model_type=ModelType.regressor,
                             method=ModelMethod.tree, source=source, target_feature_name=target_feature.name)

    # retrieve
    retrieved_model = Model.build(model_id=model.info.model_id, workspace_id=ws.info.workspace_id,
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
    vary_target_feature = source.features.fetch_all()
    for f in source.features.fetch_all():
        if f.feature_type == FeatureType.numeric and f.name != target_feature.name:
            vary_target_feature = f
            break
    variations = [float(i) / 255 for i in range(255)]
    prediction_result = model.predictions.predict_unidimensional(data_one_instance, variations,
                                                                 vary_target_feature.name)
    assert (target_feature.name in prediction_result.columns and len(prediction_result) == 255)

    # delete source
    model.delete()
    try:
        m = Model.build(model_id=model.info.model_id, workspace_id=ws.info.workspace_id, credentials=org.credentials)
        assert False
    except DeepintHTTPError:
        assert True

    # delete workspace
    ws.delete()


def test_url_parser():
    # load organization and create workspace, source and alert
    org = Organization.build()

    workspace = org.workspaces.create(name=serve_name(TEST_WS_NAME), description=TEST_WS_DESC)

    data = pd.read_csv(TEST_CSV)
    source = workspace.sources.create_and_initialize(name=serve_name(TEST_SRC_NAME), description=TEST_SRC_DESC, data=data)

    target_feature = None
    for f in source.features.fetch_all():
        if f.feature_type == FeatureType.numeric:
            target_feature = f
            break
    model = workspace.models.create(name=serve_name(TEST_MODEL_NAME), description=TEST_MODEL_DESC, model_type=ModelType.regressor,
                                    method=ModelMethod.tree,
                                    source=source, target_feature_name=target_feature.name)

    alert = workspace.alerts.create(name=serve_name(TEST_ALERT_NAME), description=TEST_ALERT_DESC,
                                    subscriptions=TEST_ALERT_SUBSCRIPTIONS,
                                    color='#FF00FF', alert_type=AlertType.update, source_id=source.info.source_id)

    task = list(workspace.tasks.fetch_all(force_reload=True))[0]

    # extract id
    t_id = task.info.task_id
    a_id = alert.info.alert_id
    m_id = model.info.model_id
    src_id = source.info.source_id
    ws_id = workspace.info.workspace_id

    # check
    ws = Workspace.from_url(url=f'https://app.deepint.net/workspace?ws={ws_id}', credentials=org.credentials)
    assert (ws.info.workspace_id == ws_id)

    ws = Workspace.from_url(url=f'https://app.deepint.net/api/v1/workspace/{ws_id}', credentials=org.credentials)
    assert (ws.info.workspace_id == ws_id)

    src = Source.from_url(url=f'https://app.deepint.net/workspace?ws={ws_id}&s=source&i={src_id}',
                          credentials=org.credentials)
    assert (src.workspace_id == ws_id and src.info.source_id == src_id)

    src = Source.from_url(url=f'https://app.deepint.net/api/v1/workspace/{ws_id}/source/{src_id}',
                          credentials=org.credentials)
    assert (src.workspace_id == ws_id and src.info.source_id == src_id)

    a = Alert.from_url(url=f'https://app.deepint.net/api/v1/workspace/{ws_id}/alerts/{a_id}',
                       credentials=org.credentials)
    assert (a.info.alert_id == a_id)

    a = Alert.from_url(url=f'https://app.deepint.net/workspace?ws={ws_id}&s=alert&i={a_id}',
                       credentials=org.credentials)
    assert (a.info.alert_id == a_id)

    t = Task.from_url(url=f'https://app.deepint.net/api/v1/workspace/{ws_id}/task/{t_id}', credentials=org.credentials)
    assert (t.info.task_id == t_id)

    t = Task.from_url(url=f'https://app.deepint.net/workspace?ws={ws_id}&s=task&i={t_id}', credentials=org.credentials)
    assert (t.info.task_id == t_id)

    m = Model.from_url(url=f'https://app.deepint.net/api/v1/workspace/{ws_id}/models/{m_id}',
                       credentials=org.credentials)
    assert (m.info.model_id == m_id)

    m = Model.from_url(url=f'https://app.deepint.net/workspace?ws={ws_id}&s=model&i={m_id}',
                       credentials=org.credentials)
    assert (m.info.model_id == m_id)

    # finally delete workspace
    ws.delete()


if __name__ == '__main__':
    test_credentials_load()
    test_workspace_CRUD()
    test_source_CRUD()
    test_task_CRUD()
    test_alert_CRUD()
    test_model_CRUD()
    test_url_parser()
