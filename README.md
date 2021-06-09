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
- **run tests**: install test dependencies with `python3 -m pip install deepint-sdk[tests]`, then define the enviroment variables `DEEPINT_TOKEN`, `DEEPINT_ORGANIZATION` and `TEST_CSV` (the last one is a CSV file to test the features of the SKD). Finally, go to the tests foleder and run `pytest -vv test.py`
- **generate doc**: install documentation dependencies with `python3 -m pip install -e deepint-sdk[docs]`, then go to the docs foleder and run `make html`

## Documentation
Visit the documentation page at <a href="https://pypi.org/project/deepint/" target="_blanck">Pypi</a> or <a href="https://deepint-python-sdk.readthedocs.io/en/latest/index.html" target="_blanck">readthedocs</a> 

## Setup credentials
Credentials can be set up with one of the following methods (the token is loaded in the priority defined in the order of the following items):
 - instance credentials object with the token and organization optional parameters `c = Credentials(token='a token', organization='a organization')`
 - create a environment variable called `DEEPINT_TOKEN` with the token value and another one called `DEEPINT_ORGANIZATION` with the organization.
 - create a .ini file in your home directory called `.deepint` coninting in the `DEFAULT` section the keys `token` and `organization` like in following example
     ```
     [DEFAULT]
     token=a token
     organization=a organization id
     ```
To learn more about credentials setup, please visit the <a href="https://deepint-python-sdk.readthedocs.io/en/latest/_info/authentication.html" target="_blank" >official documentation<a>.

## Usage of main components

##### Load organization and access information and components

```python3
from deepint import Organization

org = Organization.build()

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

org = Organization.build()
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

org = Organization.build()

t_id = 'f88cd9ac-8bc7-49db-ab49-b53512b6adc9'
a_id = 'ce92588d-700a-42d6-92f9-76863b648359'
m_id = 'a1dec81d-b46d-44a0-8c7d-3d9db6b45449'
ws_id = '03f695f2-8b6a-4b7d-9f66-e2479f8025a4'
src_id = 'e7da542c-f38c-42bf-bc1d-e89eac179047'

ws = Workspace.build(credentials=org.credentials, workspace_id=ws_id)
task = Task.build(task_id=a_id, workspace_id=ws_id, credentials=org.credentials)
model = Model.build(model_id=a_id, workspace_id=ws_id, credentials=org.credentials)
alert = Alert.build(alert_id=a_id, workspace_id=ws_id, credentials=org.credentials)
src = Source.build(source_id=src_id, workspace_id=ws_id, credentials=org.credentials)
```

##### Load elements with URL

```python3
from deepint import Organization, Workspace, Model, Alert, Task, Alert, Source

org = Organization.build()

t_id = 'f88cd9ac-8bc7-49db-ab49-b53512b6adc9'
a_id = 'ce92588d-700a-42d6-92f9-76863b648359'
m_id = 'a1dec81d-b46d-44a0-8c7d-3d9db6b45449'
ws_id = '03f695f2-8b6a-4b7d-9f66-e2479f8025a4'
src_id = 'e7da542c-f38c-42bf-bc1d-e89eac179047'

ws = Workspace.from_url(url=f'https://app.deepint.net/workspace?ws={ws_id}', credentials=org.credentials)
ws = Workspace.from_url(url=f'https://app.deepint.net/api/v1/workspace/{ws_id}', credentials=org.credentials)
t = Task.from_url(url=f'https://app.deepint.net/api/v1/workspace/{ws_id}/task/{t_id}', credentials=org.credentials)
t = Task.from_url(url=f'https://app.deepint.net/workspace?ws={ws_id}&s=task&i={t_id}', credentials=org.credentials)
m = Model.from_url(url=f'https://app.deepint.net/workspace?ws={ws_id}&s=model&i={m_id}', credentials=org.credentials)
m = Model.from_url(url=f'https://app.deepint.net/api/v1/workspace/{ws_id}/models/{m_id}', credentials=org.credentials)
a = Alert.from_url(url=f'https://app.deepint.net/workspace?ws={ws_id}&s=alert&i={a_id}', credentials=org.credentials)
a = Alert.from_url(url=f'https://app.deepint.net/api/v1/workspace/{ws_id}/alerts/{a_id}', credentials=org.credentials)
src = Source.from_url(url=f'https://app.deepint.net/workspace?ws={ws_id}&s=source&i={src_id}', credentials=org.credentials)
src = Source.from_url(url=f'https://app.deepint.net/api/v1/workspace/{ws_id}/source/{src_id}', credentials=org.credentials)
```

##### Create source from pandas.DataFrame

```python3
import pandas as pd
from deepint import Organization, Source

org = Organization.build()
ws = org.workspaces.fetch(name='example')

# create empty source
empty_source = ws.sources.create(name='example', description='example', features=[])

# create source from dataframe (creates columns with the index, name nad type)
data = pd.read_csv('example.csv')
source = ws.sources.create_and_initialize(name='exampe', description='exampe', data=data)
```

##### Use sources

```python3
import pandas as pd
from deepint import Organization, Source, Task

ws_id = '03f695f2-8b6a-4b7d-9f66-e2479f8025a4'

org = Organization.build()
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
source = ws.sources.create_and_initialize_if_not_exists('test', data)
source1 = ws.sources.create_and_initialize_if_not_exists('test', data)
if source == source1:
    print('source is equal to source1 because the method works!')
source.delete()

# delete source
source.delete()
```

##### Use models

```python3
import pandas as pd
from deepint import Organization, Model, Task

org = Organization.build()
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
```

##### Use tasks

```python3
import pandas as pd
from deepint import Organization, Model, Task, TaskStatus
from deepint DeepintTaskError

org = Organization.build()
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
