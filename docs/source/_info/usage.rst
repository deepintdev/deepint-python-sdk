
Usage
=====

In this section the principal usage examples of the package are providen.

Load organization and access information and components
-------------------------------------------------------

.. code-block:: python3

    from deepint import Organization

    org = Organization.build(organization_id="3a874c05-26d1-4b8c-894d-caf90e40078b")

    print(org.account)
    print(org.workspaces.fetch_all())
    ws = org.workspaces.fetch_all()[0]

    print(ws.automations.list())
    print(ws.tasks.fetch_all())
    print(ws.models.fetch_all())
    print(ws.sources.fetch_all())
    print(ws.dashboards.fetch_all())
    print(ws.visualizations.fetch_all())

    print(ws.info)
    print(ws.automations.list()[0])
    print(ws.tasks.fetch_all()[0].info)
    print(ws.models.fetch_all()[0].info)
    print(ws.sources.fetch_all()[0].output_features)
    print(ws.sources.fetch_all()[0].input_features.fetch_all())
    print(ws.sources.fetch_all()[0].info)
    print(ws.sources.fetch_all()[0].features.fetch_all())
    print(ws.dashboards.fetch_all()[0].info)
    print(ws.visualizations.fetch_all()[0].info)

    # also all elements have to_dict method
    print(ws.info.to_dict())


Create workspace, source, automation and model
----------------------------------------------

.. code-block:: python3

    from deepint import Organization, ModelType, ModelMethod

    org = Organization.build(organization_id="3a874c05-26d1-4b8c-894d-caf90e40078b")
    workspace = org.workspaces.create(name='example', description='example')
    source = workspace.sources.create(name='example', description='example', features=[])
    target_feature = source.features.fetch_all()[0]
    model = workspace.models.create(name='example', description='example', model_type=ModelType.regressor, method=ModelMethod.tree, source=source, target_feature_name=target_feature.name)
    automation = workspace.automations.create(name='example', description='example', trigger={'type': 'source_updated', 'source': source.info.source_id})
    task = workspace.tasks.fetch_all(force_reload=True)[0]


Load elements with builder
--------------------------

.. code-block:: python3

    from deepint import Organization, Workspace, Model, Automation, Task, Source

    t_id = 'f88cd9ac-8bc7-49db-ab49-b53512b6adc9'
    a_id = 'ce92588d-700a-42d6-92f9-76863b648359'
    m_id = 'a1dec81d-b46d-44a0-8c7d-3d9db6b45449'
    ws_id = '03f695f2-8b6a-4b7d-9f66-e2479f8025a4'
    src_id = 'e7da542c-f38c-42bf-bc1d-e89eac179047'
    org_id = 'organization_id="3a874c05-26d1-4b8c-894d-caf90e40078b'

    ws = Workspace.build(credentials=org.credentials, workspace_id=ws_id, organization_id=org_id)
    task = Task.build(task_id=a_id, workspace_id=ws_id, organization_id=org_id, credentials=org.credentials)
    model = Model.build(model_id=a_id, workspace_id=ws_id, organization_id=org_id, credentials=org.credentials)
    automation = Automation.build(automation_id=a_id, workspace_id=ws_id, organization_id=org_id, credentials=org.credentials)
    src = Source.build(source_id=src_id, workspace_id=ws_id, organization_id=org_id, credentials=org.credentials)


Load elements with URL
----------------------

.. code-block:: python3

    from deepint import Organization, Workspace, Model, Automation, Task, Source


    t_id = 'f88cd9ac-8bc7-49db-ab49-b53512b6adc9'
    a_id = 'ce92588d-700a-42d6-92f9-76863b648359'
    m_id = 'a1dec81d-b46d-44a0-8c7d-3d9db6b45449'
    ws_id = '03f695f2-8b6a-4b7d-9f66-e2479f8025a4'
    src_id = 'e7da542c-f38c-42bf-bc1d-e89eac179047'
    org_id = 'organization_id="3a874c05-26d1-4b8c-894d-caf90e40078b'

    ws = Workspace.from_url(url=f'https://app.air-core.io/o/{org_id}/workspace?ws={ws_id}', credentials=org.credentials)
    ws = Workspace.from_url(url=f'https://app.air-core.io/api/v1/workspace/{ws_id}', credentials=org.credentials, organization_id=org_id)
    t = Task.from_url(url=f'https://app.air-core.io/api/v1/workspace/{ws_id}/task/{t_id}', credentials=org.credentials, organization_id=org_id)
    t = Task.from_url(url=f'https://app.air-core.io/o/{org_id}/workspace?ws={ws_id}&s=task&i={t_id}', credentials=org.credentials)
    m = Model.from_url(url=f'https://app.air-core.io/o/{org_id}/workspace?ws={ws_id}&s=model&i={m_id}', credentials=org.credentials)
    m = Model.from_url(url=f'https://app.air-core.io/api/v1/workspace/{ws_id}/models/{m_id}', credentials=org.credentials, organization_id=org_id)
        a = Automation.from_url(url=f'https://app.air-core.io/api/v2/workspace/{ws_id}/automations/{a_id}', credentials=org.credentials, organization_id=org_id)
    src = Source.from_url(url=f'https://app.air-core.io/o/{org_id}/workspace?ws={ws_id}&s=source&i={src_id}', credentials=org.credentials)
    src = Source.from_url(url=f'https://app.air-core.io/api/v1/workspace/{ws_id}/source/{src_id}', credentials=org.credentials, organization_id=org_id)


Create source from dataframe
----------------------------

.. code-block:: python3

    import pandas as pd
    from deepint import Organization, Source

    org = Organization.build(organization_id="3a874c05-26d1-4b8c-894d-caf90e40078b")
    ws = org.workspaces.fetch(name='example')

    # create empty source
    empty_source = ws.sources.create(name='example', description='example', features=[])

    # create source from dataframe (creates columns with the index, name nad type)
    data = pd.read_csv('example.csv')
    source = ws.sources.create_and_initialize(name='exampe', description='exampe', data=data)


Use workspaces
--------------

.. code-block:: python3

    from deepint import Organization, Credentials

    # load organization
    credentials = Credentials.build(token='<your-token>')
    org = Organization.build(organization_id='dfdb7d08-18ce-4b5a-b082-0afa0f557d31', credentials=credentials)
        
    # create workspace
    ws = org.workspaces.create(name='example', description='example')

    # update workspace
    ws.update(name='example2', description='example2')

    # export workspace ZIP file
    zip_path = ws.export()

    # import workspace ZIP file
    new_workspace = org.workspaces.import_ws(new_workspace = org.workspaces.import(name='example2', description='example2', file_path=zip_path)

    # clone workspace
    other_workspace = ws.clone()

    # delayed export of workspace
    task = ws.export(folder_path='./example_ws.zip', wait_for_download=False)
    ws.export(folder_path='./example_ws_delayed.zip', task=task)

    # delete workspace
    ws.delete()


Use sources
-----------

.. code-block:: python3

    import pandas as pd
    from deepint import Organization

    org = Organization.build(organization_id="3a874c05-26d1-4b8c-894d-caf90e40078b")
    ws = org.workspaces.fetch(workspace_id='example')

    # create source from dataframe (creates columns with the index, name nad type)
    data = pd.read_csv('example.csv')
    source = ws.sources.create_and_initialize(name='exampe', description='exampe', data=data)

    # update instances
    data2 = pd.read_csv('example.csv')
    task = source.instances.update(data=data2)

    # wait for task to finish
    task.resolve()

    # retrieve all instances
    retrieved_data = source.instances.fetch()

    # query for instances
    query = {...} # query of AIR-Core
    retrieved_data = source.instances.fetch(where=query)

    # delete instances
    task = source.instances.delete(where=query)
    task.resolve()

    # udpate source name
    source.update(name='example2', description='example2')

    # update source features
    feature = source.features.fetch_all()[0]
    feature.feature_type = FeatureType.unknown
    source.features.update()

    # create source if not exists, else only retrieve
    source = ws.sources.create_if_not_exists('test')
    source1 = ws.sources.create_if_not_exists('test')
    if source == source1:
        print('source is equal to source1 because the method works!')
    source.delete()

    # create (with initialization) source if not exists, else only retrieve
    source = ws.sources.create_else_update(('test', data)
    source1 = ws.sources.create_else_update('test', data)
    if source == source1:
        print('source is equal to source1 because the method works!')
    source1.delete()

    # clone source
    new_source = source.clone()

    # delete source
    new_source.delete()

    #  create derived source
    derived_source = ws.sources.create_derived(name='derived_test', description='desc', derived_type=DerivedSourceType.filter, origin_source_id=source.info.source_id, origin_source_b_id=None, query={}, features=source.features.fetch_all(), feature_a=None, feature_b=None, is_encrypted=False, is_shuffled=False, wait_for_creation=True)

    # create autoupdated and test configuration
    auto_updated_source = ws.sources.create_autoupdated(
        name='autoupdated', description='desc', source_type=SourceType.url_json, url='https://app.air-core.io/static/sources/iris.json', json_fields=["sepalLength", "sepalWidth", "petalLength", "petalWidth", "species"], json_prefix=None, http_headers=None, ignore_security_certificates=True, is_single_json_obj=False, wait_for_creation=True
    )

    # fetch and update the autoupdate configuration
    auto_updated_source.update_actualization_config(auto_update=False)
    configuration = auto_updated_source.fetch_actualization_config()


Use Real Time Sources
---------------------

.. code-block:: python3

    import pandas as pd
    from deepint import Organization

    org = Organization.build(organization_id="3a874c05-26d1-4b8c-894d-caf90e40078b")
    ws = org.workspaces.fetch(workspace_id='example')

    # create real time source
    features = [SourceFeature.from_dict(f) for f in [

        {"index": 0, "name": "sepalLength", "type": "numeric", "dateFormat": "", "indexed": True}, {"index": 1, "name": "sepalWidth", "type": "numeric", "dateFormat": "", "indexed": True}, {"index": 2, "name": "petalLength", "type": "numeric", "dateFormat": "", "indexed": True}, {"index": 3, "name": "petalWidth", "type": "numeric", "dateFormat": "", "indexed": True}, {"index": 4, "name": "species", "type": "nominal", "dateFormat": "", "indexed": True}
    ]]
    rt_source = ws.sources.create_real_time(name='test', description='desc', features=features)

    # update connection
    rt_source.update_connection(max_age=10, regenerate_password=True)

    # retrieve connection
    connection_info = rt_source.fetch_connection()

    # update instances
    data = [{
        "sepalLength": 4.6,
        "sepalWidth": 3.2,
        "petalLength": 1.4,
        "petalWidth": 0.2,
        "species": "setosa"
    }]    
    rt_source.instances.update(data=data)
    
    # retrieve instances
    instances = rt_source.instances.fetch()

    # clear queued instances during last 5 minutes
    to_time = datetime.now()
    from_time = datetime.now() - timedelta(minutes=5)
    rt_source.instances.clear_queued_instances(from_time=from_time, to_time=to_time)


Use External sources
--------------------

.. code-block:: python3

    import pandas as pd
    from deepint import Organization

    org = Organization.build(organization_id="3a874c05-26d1-4b8c-894d-caf90e40078b")
    ws = org.workspaces.fetch(workspace_id='example')

    # create source
    src_name = serve_name(TEST_SRC_NAME)
    features = [SourceFeature.from_dict(f) for f in [

        {"index": 0, "name": "sepalLength", "type": "numeric", "dateFormat": "", "indexed": True}, {"index": 1, "name": "sepalWidth", "type": "numeric", "dateFormat": "", "indexed": True}, {"index": 2, "name": "petalLength", "type": "numeric", "dateFormat": "", "indexed": True}, {"index": 3, "name": "petalWidth", "type": "numeric", "dateFormat": "", "indexed": True}, {"index": 4, "name": "species", "type": "nominal", "dateFormat": "", "indexed": True}
    ]]
    external_source = ws.sources.create_external(name='test', description='desc', url='https://mysource:443/example?pub=03f695f2-8b6a-4b7d-9f66-e2479f8025a4&secret=3a874c05-26d1-4b8c-894d-caf90e40078b', features=features)

    # update instances
    data = [{
        "sepalLength": 4.6,
        "sepalWidth": 3.2,
        "petalLength": 1.4,
        "petalWidth": 0.2,
        "species": "setosa"
    }]
    data = pd.DataFrame(data=data)
    external_source.instances.update(data=data)

    # connection update and retrieval
    external_source.update_connection(url='https://mynewurl:443/example?pub=03f695f2-8b6a-4b7d-9f66-e2479f8025a4&secret=3a874c05-26d1-4b8c-894d-caf90e40078b')
    connection_url = external_source.fetch_connection()


Use models
----------

.. code-block:: python3

    import pandas as pd
    from deepint import Organization, Model, Task

    org = Organization.build(organization_id="3a874c05-26d1-4b8c-894d-caf90e40078b")
    ws = org.workspaces.fetch(name='example')
    data = pd.read_csv('example.csv')
    source = ws.sources.create_and_initialize(name='example', description='example', data=data)

    # create model
    model = ws.models.create(name='example', description='example', model_type=ModelType.classifier, method=ModelMethod.gradient, source=source, target_feature_name='country')

    # update model
    model.update(name=f'other name', description=f'other description')

    # get model evaluation
    evaluation = model.predictions.evaluation()

    # predict one instance
    data_one_instance = data.head(n=1)
    del data_one_instance['country']
    prediction_result = model.predictions.predict(data_one_instance)

    # predict batch
    data_some_instances = data.head(n=25)
    del data_some_instances['name']
    prediction_result = model.predictions.predict_batch(data_some_instances)

    # predict with variaions
    variations = [i/100 for i in range(100)]
    prediction_result = model.predictions.predict_unidimensional(data_one_instance, variations, 'water_percentage')

    # delete model
    model.delete()


Use tasks
---------

.. code-block:: python3

    import pandas as pd
    from deepint import Organization, Model, Task, TaskStatus
    from deepint DeepintTaskError

    org = Organization.build(organization_id="3a874c05-26d1-4b8c-894d-caf90e40078b")
    ws = org.workspaces.fetch(name='example')

    # retrieve tasks by status
    pending_tasks = ws.tasks.fetch_by_status(status=TaskStatus.pending)

    # cancel task
    t = pending_tasks[0]
    t.delete()

    # wait for task to finish
    t = pending_tasks[1]
    try:
      t.resolve()
      result = t.fetch_result()
    except DeepintTaskError as e:
      print(f'the task was errored with error {e}')

    # update and check if errored
    t = pending_tasks[2]
    t.load()
    if t.is_errored():
      print('an errror occurred')


Use visualizations
------------------

.. code-block:: python3

    import pandas as pd
    from deepint import Organization, Visualization, Source

    # load organization and create workspace
    org = Organization.build(organization_id='a1faa528-1d42-4cf0-ae04-e122d0ddf9aa')
    ws = org.workspaces.create(name='example', description='example')

    # create a source for the visualization
    data = pd.read_csv('example.csv')
    src = ws.sources.create_and_initialize(name='exampe', description='exampe', data=data)

    # create visualization
    vis = ws.visualizations.create(name='example', description='example', privacy='public', source='source_id', configuration={})

    # update visualization
    vis.update(name='example2', description='example2', source='source_id')

    # clone visualization
    new_vis = vis.clone()

    # extract token for iframe access
    url, token = vis.fetch_iframe_token()

    # delete visualization
    vis.delete()


Use dashboards
--------------

.. code-block:: python3

    from deepint import Credentials, Organization, Dashboard

    # load organization and create workspace
    org = Organization.build(organization_id='e612d27d-9c81-479f-a35f-85cac80c0718')
    ws = org.workspaces.create(name='example', description='example')

    # create dashboard
    dash = ws.dashboards.create(name='example', description='example', privacy='public', shareOpt="",
                        gaId="", restricted=True, configuration={})
    # update dashboard
    dash.update(name='example2', description='example2')

    # clone dashboard
    new_dash = dash.clone()

    # extract token for iframe access
    url, token = dash.fetch_iframe_token()

    # delete dashboard
    dash.delete()


Use emails
----------

.. code-block:: python3

    from deepint import Organization

    # load organization and create workspace
    org = Organization.build(organization_id='e612d27d-9c81-479f-a35f-85cac80c0718')
    ws = org.workspaces.create(name='example', description='example')

    # create email
    new_email = workspace.emails.create(email='test@test.com')

    # fetch single
    test_email_info = workspace.emails.fetch(email='test@test.com')

    # fetch all emails
    emails = workspace.emails.fetch_all(force_reload=True)

    # delete email
    workspace.emails.delete(email=TEST_EMAIL)


Explainability, model cards and AI activity
-------------------------------------------

These operations need AIR-Core 1.1 or later.

.. code-block:: python3

    from deepint import Organization

    org = Organization.build(organization_id='e612d27d-9c81-479f-a35f-85cac80c0718')
    ws = org.workspaces.fetch(name='example')
    model = ws.models.fetch(name='example')

    # explainability (SHAP, when the explainability module of the instance is enabled)
    importances = model.explanations.global_importances(lang='en')
    explanation = model.explanations.explain_prediction([5.1, 3.5, 1.4, 0.2], lang='en')

    # model card: purpose, data, evaluation, explainability and limitations
    card = model.card(lang='en')

    # audit log of the assistant, MCP and explainability calls (organization administrators)
    activity = org.ai_activity(channel='mcp', limit=20)


Automations (simple notices and flows)
--------------------------------------

The alerts are now **automations** (AIR-Core API v2): the simple notices and the flows of a workspace. AIR-Core saves a new automation as a simple notice when it is exactly one (a ``stall`` trigger, or new rows that meet rules with eq, gt, gte, lt, lte, null, cn, sw or ew, emailed to the whole notice list, with at most one webhook) and as a flow otherwise (a schedule, a model, rows written, other recipients...). ``saved_as`` says which and why. Editing never changes the kind: a change that would turn a notice into a flow raises ``DeepintHTTPError`` with code ``NOT_A_NOTICE`` (create a new automation instead), and the notices of a metric, of the quality of a source or of the monitoring of a model only change their name and description (``NOTICE_FIXED``).

.. code-block:: python3

    from deepint import Organization, Automation

    org = Organization.build(organization_id='e612d27d-9c81-479f-a35f-85cac80c0718')
    ws = org.workspaces.fetch(name='example')
    source = ws.sources.fetch(name='example')

    # a simple notice: email the notice list of the workspace when a new row has temperature > 30
    hot = ws.automations.create(name='Hot', trigger={'type': 'source_updated', 'source': source.info.source_id},
                                condition={'kind': 'rules', 'match': 'all',
                                           'rules': [{'column': 'temperature', 'op': 'gt', 'value': 30}]})
    print(hot.saved_as)  # {'kind': 'notice', 'reason': 'SIMPLE'}

    # a simple notice: no new data for 6 hours
    ws.automations.create(name='Silent', trigger={'type': 'stall', 'source': source.info.source_id, 'hours': 6})

    # a flow: also call a webhook and write the matching rows to another source
    flow = ws.automations.create(name='Hot to log', trigger={'type': 'source_updated', 'source': source.info.source_id},
                                 condition={'kind': 'rules', 'match': 'any',
                                            'rules': [{'column': 'status', 'op': 'cni', 'value': 'error'}]},
                                 actions=[{'type': 'webhook', 'url': 'https://hooks.example.com/aircore'},
                                          {'type': 'append', 'target': 'b3c1e7a0-0000-4000-8000-000000000000'}])
    print(flow.saved_as)        # {'kind': 'flow', 'reason': 'OPERATOR'}
    print(flow.webhook_secret)  # the signing secret of the webhook, returned only now

    # list (all, only notices or only flows), read in full, change, test, history and delete
    ws.automations.list()
    ws.automations.list(kind='flow')
    a = ws.automations.fetch(automation_id=hot.info.automation_id)
    a.update(name='Very hot')         # editing never changes the kind: 409 NOT_A_NOTICE / NOTICE_FIXED
    print(a.test())                   # what would happen now, nothing sent or written
    print(a.history(page=0, limit=20))
    a.delete()

    # a former alert is a simple notice with the same id
    notice = Automation.build(organization_id='e612d27d-9c81-479f-a35f-85cac80c0718', workspace_id=ws.info.workspace_id,
                              automation_id='ce92588d-700a-42d6-92f9-76863b648359', credentials=org.credentials)

    # in the receiver of a webhook: check the x-signature-256 header against the raw body
    Automation.verify_webhook_signature(secret, raw_body, request_headers['x-signature-256'])


Migrating from alerts (2.0)
---------------------------

Every former alert method raises ``DeepintAlertsRemovedError`` (a ``DeepintHTTPError`` with code ``ALERTS_REMOVED``, the code of the HTTP 410 Gone that API v1 answers) naming its replacement, without calling the API. A former alert keeps its id as a simple notice.

.. list-table::
   :header-rows: 1

   * - Before (1.x)
     - Now (2.0)
   * - ``ws.alerts.fetch_all()``
     - ``ws.automations.fetch_all(kind='notice')  # or ws.automations.list()``
   * - ``ws.alerts.fetch(alert_id=a_id)``
     - ``ws.automations.fetch(automation_id=a_id)``
   * - ``ws.alerts.create(name, description, subscriptions, color, AlertType.update, source_id, condition)``
     - ``ws.automations.create(name, trigger={'type': 'source_updated', 'source': source_id}, condition=...)``
   * - ``ws.alerts.create(..., alert_type=AlertType.stall, time_stall=seconds)``
     - ``ws.automations.create(name, trigger={'type': 'stall', 'source': source_id, 'hours': hours})``
   * - ``Alert.build(org_id, ws_id, alert_id)``
     - ``Automation.build(org_id, ws_id, automation_id=alert_id)``
   * - ``Alert.from_url(url)``
     - ``Automation.from_url('https://app.air-core.io/api/v2/workspace/{ws}/automations/{id}', organization_id=org_id)``
   * - ``alert.update(...) / alert.delete()``
     - ``automation.update(...) / automation.delete()``
   * - ``alert.instances.fetch()``
     - ``automation.history()``
   * - ``alert.webhook.set(url) / alert.webhook.delete()``
     - ``automation.update(actions=[{'type': 'email', 'to': 'list'}, {'type': 'webhook', 'url': url}])``
   * - ``alert.webhook.test()``
     - ``automation.test()``
   * - ``AlertWebhook.verify_signature(...)``
     - ``Automation.verify_webhook_signature(...)  # the old one still works``


API version
-----------

The SDK calls AIR-Core API v2 (``/api/v2/...``), which serves every operation of API v1 except the alerts. API v1 is deprecated and keeps working: to keep calling it, use ``set_api_version('v1')`` or the ``AIRCORE_API_VERSION=v1`` environment variable (the automations always use v2). Paths given to ``org.endpoint.call(...)`` are sent as written.

.. code-block:: python3

    from deepint import set_api_version, get_api_version

    print(get_api_version())  # 'v2'
    set_api_version('v1')     # only to keep calling the deprecated API v1


Use custom endpoint
-------------------

.. code-block:: python3

    from deepint import Organization

    # load organization and create workspace
    org = Organization.build(organization_id='e612d27d-9c81-479f-a35f-85cac80c0718')
    ws = org.workspaces.create(name='example', description='example')

    # perform call to /api/v2/who
    response = org.endpoint.call(http_operation='GET', path='/api/v2/who', headers=None, parameters=None, is_paginated=False)
