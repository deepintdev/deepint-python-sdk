[![codecov](https://codecov.io/gh/deepintdev/deepint-python-sdk/branch/master/graph/badge.svg?token=QNAP7Y8CT1)](https://codecov.io/gh/deepintdev/deepint-python-sdk)
# DeepIntelligence SDK for Python

<p align="center">
 <img src="https://deepint.net/sites/default/files/logo2.svg" align="center" width=300 height=300>
</p>

##### DeepIntelligence SDK
deepint is a python package to work with <a href="https://deepint.net/" target="_blank" >DeepIntelligence<a> in a more easy and intuitive way, allowing the programmer to develop in a fast way the data, analisys and visualization flows.
The package consists in a wrapper arround <a href="https://app.deepint.net/api/v1/documentation/" target="_blank" >DeepIntelligence API<a>, with some extra facilities.

##### Deep Intelligence 
Deep Intelligence has been designed to help you select optimal AI & Machine Learning algorithms for the analysis of your business’ datasets. This platform can be customized to read any type of data from webs, files, databases, sensors…, it can also stream data in real time if needed, it’s all very simple!

A highly attractive, user-friendly and intuitive visualization environment will guide you in the creation and configuration of algorithms that will analyze your data optimally. The platform makes it possible to create dashboards for better visualization experience, moreover, they can be easily integrated into any other online application. Improve your business decision-making without any expert IT knowledge!

Deep Intelligence is a platform for Fintech, IoT, Smart Cities, Smart Grids, Biomedical analysis, Logistics, Industry 4.0, etc. Some of our customers have already increased their business’ profits by 50%!

Our extensive team of data analysis experts will be at your complete disposal for any information, guidance and support you may need.

Visit the DeepIntelligence on it's <a href="https://deepint.net/" target="_blank" >website<a>.

## Installation

- **install**: `python3 -m pip install deepint`
- **run tests**: install test dependencies with `python3 -m pip install deepint[tests]`, then define the enviroment variables `DEEPINT_TOKEN` and `DEEPINT_ORGANIZATION`. Finally, go to the tests foleder and run `pytest -vv test.py`
- **generate doc**: install documentation dependencies with `python3 -m pip install -e deepint[docs]`, then go to the docs foleder and run `make html`

## Documentation
Visit the documentation page at <a href="https://pypi.org/project/deepint/" target="_blanck">Pypi</a> or <a href="https://deepint-python-sdk.readthedocs.io/en/latest/index.html" target="_blanck">readthedocs</a> 

## Setup credentials
Credentials can be set up with one of the following methods (the token and instance is loaded in the priority defined in the order of the following items):
 - instance credentials object with the token and instance optional parameters `c = Credentials(token='a token', instance='app.deepint.net')`
 - create a environment variable called `DEEPINT_TOKEN` with the token value and another one called `DEEPINT_INSTANCE`.
 - create a .ini file in your home directory called `.deepint` coninting in the `DEFAULT` section the key `token` and the key `instance` like in following example
     ```
     [DEFAULT]
        token=a token
        instance=host to connect with (if not providen app.deepint.net will be taken by default)
     ```
Note: If instance is not providen, the default value will be the SaaS instance `app.deepint.net`.

To learn more about credentials setup, please visit the <a href="https://deepint-python-sdk.readthedocs.io/en/latest/_info/authentication.html" target="_blank" >official documentation<a>.

## Usage of main components

##### Load organization and access information and components

```python3
from deepint import Organization

org = Organization.build(organization_id="3a874c05-26d1-4b8c-894d-caf90e40078b")

print(org.account)
print(org.workspaces.fetch_all())
ws = org.workspaces.fetch_all()[0]

print(ws.alerts.fetch_all())
print(ws.tasks.fetch_all())
print(ws.models.fetch_all())
print(ws.sources.fetch_all())
print(ws.dashboards.fetch_all())
print(ws.visualizations.fetch_all())

print(ws.info)
print(ws.alerts.fetch_all()[0].info)
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
```

##### Create workspace, source, alert and model

```python3
from deepint import Organization, AlertType, ModelType, ModelMethod

org = Organization.build(organization_id="3a874c05-26d1-4b8c-894d-caf90e40078b")
workspace = org.workspaces.create(name='example', description='example')
source = workspace.sources.create(name='example', description='example', features=[])
target_feature = source.features.fetch_all()[0]
model = workspace.models.create(name='example', description='example', model_type=ModelType.regressor, method=ModelMethod.tree, source=source, target_feature_name=target_feature.name)
alert = workspace.alerts.create(name='example', description='example', subscriptions=['example@example.ex'], color='#FF00FF', alert_type=AlertType.update, source_id=source.info.source_id)
task = workspace.tasks.fetch_all(force_reload=True)[0]
```

##### Load elements with builder

```python3
from deepint import Organization, Workspace, Model, Alert, Task, Alert, Source

t_id = 'f88cd9ac-8bc7-49db-ab49-b53512b6adc9'
a_id = 'ce92588d-700a-42d6-92f9-76863b648359'
m_id = 'a1dec81d-b46d-44a0-8c7d-3d9db6b45449'
ws_id = '03f695f2-8b6a-4b7d-9f66-e2479f8025a4'
src_id = 'e7da542c-f38c-42bf-bc1d-e89eac179047'
org_id = 'organization_id="3a874c05-26d1-4b8c-894d-caf90e40078b'

ws = Workspace.build(credentials=org.credentials, workspace_id=ws_id, organization_id=org_id)
task = Task.build(task_id=a_id, workspace_id=ws_id, organization_id=org_id, credentials=org.credentials)
model = Model.build(model_id=a_id, workspace_id=ws_id, organization_id=org_id, credentials=org.credentials)
alert = Alert.build(alert_id=a_id, workspace_id=ws_id, organization_id=org_id, credentials=org.credentials)
src = Source.build(source_id=src_id, workspace_id=ws_id, organization_id=org_id, credentials=org.credentials)
```

##### Load elements with URL

```python3
from deepint import Organization, Workspace, Model, Alert, Task, Alert, Source


t_id = 'f88cd9ac-8bc7-49db-ab49-b53512b6adc9'
a_id = 'ce92588d-700a-42d6-92f9-76863b648359'
m_id = 'a1dec81d-b46d-44a0-8c7d-3d9db6b45449'
ws_id = '03f695f2-8b6a-4b7d-9f66-e2479f8025a4'
src_id = 'e7da542c-f38c-42bf-bc1d-e89eac179047'
org_id = 'organization_id="3a874c05-26d1-4b8c-894d-caf90e40078b'

ws = Workspace.from_url(url=f'https://app.deepint.net/o/{org_id}/workspace?ws={ws_id}', credentials=org.credentials)
ws = Workspace.from_url(url=f'https://app.deepint.net/api/v1/workspace/{ws_id}', credentials=org.credentials, organization_id=org_id)
t = Task.from_url(url=f'https://app.deepint.net/api/v1/workspace/{ws_id}/task/{t_id}', credentials=org.credentials, organization_id=org_id)
t = Task.from_url(url=f'https://app.deepint.net/o/{org_id}/workspace?ws={ws_id}&s=task&i={t_id}', credentials=org.credentials)
m = Model.from_url(url=f'https://app.deepint.net/o/{org_id}/workspace?ws={ws_id}&s=model&i={m_id}', credentials=org.credentials)
m = Model.from_url(url=f'https://app.deepint.net/api/v1/workspace/{ws_id}/models/{m_id}', credentials=org.credentials, organization_id=org_id)
a = Alert.from_url(url=f'https://app.deepint.net/o/{org_id}/workspace?ws={ws_id}&s=alert&i={a_id}', credentials=org.credentials)
a = Alert.from_url(url=f'https://app.deepint.net/api/v1/workspace/{ws_id}/alerts/{a_id}', credentials=org.credentials, organization_id=org_id)
src = Source.from_url(url=f'https://app.deepint.net/o/{org_id}/workspace?ws={ws_id}&s=source&i={src_id}', credentials=org.credentials)
src = Source.from_url(url=f'https://app.deepint.net/api/v1/workspace/{ws_id}/source/{src_id}', credentials=org.credentials, organization_id=org_id)
```

##### Create source from pandas.DataFrame

```python3
import pandas as pd
from deepint import Organization, Source

org = Organization.build(organization_id="3a874c05-26d1-4b8c-894d-caf90e40078b")
ws = org.workspaces.fetch(name='example')

# create empty source
empty_source = ws.sources.create(name='example', description='example', features=[])

# create source from dataframe (creates columns with the index, name nad type)
data = pd.read_csv('example.csv')
source = ws.sources.create_and_initialize(name='exampe', description='exampe', data=data)
```

##### Use workspaces

```python3
from deepint import Organization, Credentials

# load organization
credentials = Credentials.build(token='3e6913ad-49f4-4fed-a50d-1ab703716a75')
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
```

##### Use sources

```python3
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
query = {...} # query of deepint.net
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
    name='autoupdated', description='desc', source_type=SourceType.url_json, url='https://app.deepint.net/static/sources/iris.json', json_fields=["sepalLength", "sepalWidth", "petalLength", "petalWidth", "species"], json_prefix=None, http_headers=None, ignore_security_certificates=True, is_single_json_obj=False, wait_for_creation=True
)

# fetch and update the autoupdate configuration
auto_updated_source.update_actualization_config(auto_update=False)
configuration = auto_updated_source.fetch_actualization_config()
```

###### Use Real Time Sources

```python3
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
```

###### Use External sources

```python3
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
```

##### Use models

```python3
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
del data_one_instance['country'] # delete target feature
prediction_result = model.predictions.predict(data_one_instance)

# predict batch
data_some_instances = data.head(n=25)
del data_some_instances['name'] # delete target feature
prediction_result = model.predictions.predict_batch(data_some_instances)

# predict with variaions
variations = [i/100 for i in range(100)]
prediction_result = model.predictions.predict_unidimensional(data_one_instance, variations, 'water_percentage')

# delete model
model.delete()
```

##### Use tasks

```python3
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
```

##### Use visualizations

```python3
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
```

##### Use dashboards

```python3
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
```

##### Use emails

```python3
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
```

#### Use custom endpoint

```python3
from deepint import Organization

# load organization and create workspace
org = Organization.build(organization_id='e612d27d-9c81-479f-a35f-85cac80c0718')
ws = org.workspaces.create(name='example', description='example')

# perform call to /api/v1/who
response = org.endpoint.call(http_operation='GET', path='/api/v1/who', headers=None, parameters=None, is_paginated=False)
```
