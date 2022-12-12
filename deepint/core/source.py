#!usr/bin/python

# Copyright 2023 Deep Intelligence
# See LICENSE for details.

import enum
import warnings
from datetime import datetime
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
from dateutil.parser import parse as python_date_parser

from ..auth import Credentials
from ..error import DeepintBaseError
from ..util import handle_request, parse_date, parse_url
from .task import Task

warnings.simplefilter(action='ignore', category=FutureWarning)


class SourceType(enum.Enum):
    """Available source types in the system.
    """

    mysql = 0
    ms_sql = 1
    oracle = 2
    pg = 3
    url_parameters = 4
    url_sql = 5
    url_sqlite = 6
    file_csv = 7
    file_parameters = 8
    file_sql = 9
    file_sqlite = 10
    url_csv = 11
    url_json = 12
    ckan = 13
    s3 = 14
    mqtt = 15
    mongo = 16
    influx = 17
    empty = 18
    derived = 19
    external = 20
    rt = 21
    unknown = 22

    @classmethod
    def from_string(cls, _str: str) -> 'SourceType':
        """Builds the :obj:`deepint.core.source.SourceType` from a :obj:`str`.

        Args:
            _str: name of the source type.

        Returns:
            the model type converted to :obj:`deepint.core.source.SourceType`.
        """
        return cls.unknown if _str not in [e.name for e in cls] else cls[_str]

    @classmethod
    def all(cls) -> List[str]:
        """ Returns all available model types serialized to :obj:`str`.

        Returns:
            all available source types.
        """
        return [e.name for e in cls]


class DerivedSourceType(enum.Enum):
    """Available derived source types in the system.
    """

    filter = 0
    extend = 1
    join = 2
    merge = 3
    aggregate = 4

    @classmethod
    def from_string(cls, _str: str) -> 'SourceType':
        """Builds the :obj:`deepint.core.source.SourceType` from a :obj:`str`.

        Args:
            _str: name of the source type.

        Returns:
            the model type converted to :obj:`deepint.core.source.SourceType`.
        """
        return cls.unknown if _str not in [e.name for e in cls] else cls[_str]

    @classmethod
    def all(cls) -> List[str]:
        """ Returns all available model types serialized to :obj:`str`.

        Returns:
            all available source types.
        """
        return [e.name for e in cls]


class FeatureType(enum.Enum):
    """Available feature types in the system.
    """
    text = 1
    date = 2
    logic = 3
    nominal = 4
    numeric = 5
    unknown = 6

    @classmethod
    def from_string(cls, _str: str) -> 'FeatureType':
        """Builds the :obj:`deepint.core.source.FeatureType` from a :obj:`str`.

        Args:
            _str: name of the feature type.

        Returns:
            the feature type converted to :obj:`deepint.core.source.FeatureType`.
        """
        return cls.unknown if _str not in [e.name for e in cls] else cls[_str]

    @classmethod
    def from_pandas_type(cls, column: pd.Series, min_text_size: int = 256) -> List['FeatureType']:
        """Builds a :obj:`deepint.core.source.FeatureType` from a :obj:`pandas.Series`.

        Checks the type of the elements stored in the column attribute, to detect the python native type
        or the :obj:`pandas` type, and build the corresponding :obj:`deepint.core.source.FeatureType`.

        Args:
            column: column of a :obj:`pd.DataFrame` to obtain the associated :obj:`deepint.core.source.FeatureType`
            min_text_size: the minimum length of an element to consider the type as text instead of nominal.

        Returns:
            The feature type associated to the given column
        """

        t = column.dtype
        # Cf. generic types in
        # https://numpy.org/doc/stable/reference/arrays.scalars.html
        if np.issubdtype(t, np.integer):
            return cls.nominal
        elif np.issubdtype(t, np.floating):
            return cls.numeric
        elif np.issubdtype(t, np.bool_):
            return cls.logic
        elif np.issubdtype(t, np.character):
            try:
                _ = python_date_parser(column.iloc[0])
                is_date = True
            except:
                is_date = False
            if is_date:
                return cls.date
            elif column.str.len().max() >= min_text_size:
                return cls.text
            else:
                return cls.nominal
        elif np.issubdtype(t, np.datetime64) or np.issubdtype(t, np.timedelta64):
            return cls.date
        else:
            # by default return nominal
            return cls.nominal


class SourceFeature:
    """ Stores the index, name, type and stats of a feature associated with a deepint.net source.

    Attributes:
        index: Feature index, starting with 0.
        name: Feature name (max 120 characters).
        feature_type: The type of the feature. Must be one of the values given in :obj:`deepint.core.source.FeatureType`.
        date_format: format used to parse the date if this feature is the type :obj:`deepint.core.source.FeatureType.date`.
        computed: True if the feature is computed (value based on operations over other features).
        null_count: Number of instances with value null.
        min_value: Min value.
        max_value: Max value..
        mean_value: Average value.
        deviation: Standard deviation.
        mapped_to: Index of the feature to map the existing data. You can specify -1 for no mapping.
    """

    def __init__(self, index: int, name: str, feature_type: FeatureType, indexed: bool,
                 date_format: str, computed: bool, null_count: int, min_value: float,
                 max_value: float, mean_value: float, deviation: float, mapped_to: int) -> None:

        if index is not None and not isinstance(index, int):
            raise ValueError('index must be int')

        if name is not None and not isinstance(name, str):
            raise ValueError('name must be str')

        if feature_type is not None and (not isinstance(feature_type, FeatureType) and not isinstance(feature_type, int)):
            raise ValueError('feature_type must be FeatureType')

        if indexed is not None and not isinstance(indexed, bool):
            raise ValueError('indexed must be bool')

        if date_format is not None and not isinstance(date_format, str):
            raise ValueError('date_format must be str')

        if computed is not None and not isinstance(computed, bool):
            raise ValueError('computed must be bool')

        if mapped_to is not None and not isinstance(mapped_to, int):
            raise ValueError('mapped_to must be int')

        self.index = index
        self.name = name
        self.feature_type = feature_type
        self.indexed = indexed
        self.date_format = date_format if not (
            date_format is None and feature_type == FeatureType.date) else 'YYYY-MM-DD'
        self.computed = computed
        self.null_count = null_count
        self.min_value = min_value
        self.max_value = max_value
        self.mean_value = mean_value
        self.deviation = deviation
        self.mapped_to = mapped_to if mapped_to is not None else index

    def __eq__(self, other):
        if other is not None and not isinstance(other, SourceFeature):
            return False
        else:
            return self.name == other.name and (self.feature_type == other.feature_type or self.feature_type == FeatureType.unknown or other.feature_type == FeatureType.unknown)

    def __str__(self):
        return '<SourceFeature ' + ' '.join([f'{k}={v}' for k, v in self.to_dict().items()]) + '>'

    @staticmethod
    def from_dict(obj: Any) -> 'SourceFeature':
        """Builds a SourceFeature with a dictionary.

        Args:
            obj: :obj:`object` or :obj:`dict` containing the a serialized SourceFeature.

        Returns:
            SourceFeature containing the information stored in the given dictionary.
        """

        index = int(obj.get("index"))
        name = obj.get("name")
        feature_type = FeatureType.from_string(obj.get("type"))
        indexed = bool(obj.get("indexed"))
        date_format = obj.get("date_format")
        computed = bool(obj.get("computed"))
        null_count = int(obj.get("null_count")) if obj.get(
            "null_count") is not None else None
        min_value = obj.get("min") if obj.get('min') is None or feature_type != FeatureType.date else parse_date(
            obj.get('min'))
        max_value = obj.get("max") if obj.get('max') is None or feature_type != FeatureType.date else parse_date(
            obj.get('max'))
        mean_value = obj.get("mean")
        deviation = obj.get("deviation")
        mapped_to = int(obj.get("mapped_to")) if obj.get(
            "mapped_to") is not None else None
        return SourceFeature(index, name, feature_type, indexed, date_format,
                             computed, null_count, min_value, max_value, mean_value, deviation, mapped_to)

    def to_dict(self) -> Dict[str, Any]:
        """Builds a dictionary containing the information stored in current object.

        Returns:
            dictionary containing the information stored in the current object.
        """

        return {"index": self.index, "name": self.name, "type": self.feature_type.name, "indexed": self.indexed,
                "date_format": self.date_format, "computed": self.computed, "null_count": self.null_count,
                "min": self.min_value, "max": self.max_value, "mean": self.mean_value,
                "deviation": self.deviation, "mapped_to": self.mapped_to}

    def to_dict_minimized(self) -> Dict[str, Any]:
        """Builds a dictionary containing the minimal information stored in current object.

        The given resulting dictionary only contains fields for the name, type, indexed, date_format
        and mapped_to attributes.

        Returns:
            dictionary containing the information stored in the current object.
        """

        return {"name": self.name, "type": self.feature_type.name, "indexed": self.indexed,
                "date_format": self.date_format, "mapped_to": self.mapped_to}

    @classmethod
    def from_dataframe(cls, df: pd.DataFrame, date_formats: Dict[str, str] = None, min_text_length: int = 1000) -> List[
            'SourceFeature']:
        """Given an :obj:`pandas.DataFrame` buils the list of :obj:`deepint.core.source.SourceFeature` associated with each of its columns.

        The given resulting ditionary only contains fields for the name, type, indexed, date_format
        and mapped_to attributes.

        Note: The index values are assigned with the order of the columns in the given :obj:`pandas.DataFrame`

        Args:
            df: :obj:`pandas.DataFrame` from which the data types for each of its columns will be constructed.
            date_formats: dicionary contianing the association between column name and date format like the ones specified
                in [#/date_formats]. Is optional to provide value for any column, but if not provided will be considered as
                null and the date format (in case of being a date type) will be the default one assigned by Deep Intelligence.
            min_text_length: the minimun length of an element to consider the type as text instead of nominal.

        Returns:
            collection of features in the format of Deep Intellgience corresponding to the given DataFrame.
        """

        # prepare date formats
        date_formats = {} if date_formats is None else date_formats
        date_formats = {
            c: None if c not in date_formats else date_formats[c] for c in df.columns}

        # build features
        return [cls(i, c, FeatureType.from_pandas_type(df[c]), True, date_formats[c], False, None, None, None,
                    None, None, None) for i, c in enumerate(df.columns)]


class SourceInfo:
    """Stores the information of a Deep Intelligence source.

    Attributes:
        source_id: source's id in format uuid4.
        created: Creation date.
        last_modified: Last modified date.
        last_access: Last access date.
        name: source's name.
        description: source's description.
        source_type: type of source (mongodb, SQL, CSV, etc).
        instances: Number of instances.
        size_bytes: Source size in bytes.
    """

    def __init__(self, source_id: str, created: datetime,
                 last_modified: datetime, last_access: datetime, name: str,
                 description: str, source_type: SourceType, instances: int,
                 size_bytes: int) -> None:

        if source_id is not None and not isinstance(source_id, str):
            raise ValueError('source_id must be str')

        if created is not None and not isinstance(created, datetime):
            raise ValueError('created must be datetime.datetime')

        if last_modified is not None and not isinstance(last_modified, datetime):
            raise ValueError('last_modified must be datetime.datetime')

        if last_access is not None and not isinstance(last_access, datetime):
            raise ValueError('last_access must be datetime.datetime')

        if name is not None and not isinstance(name, str):
            raise ValueError('name must be str')

        if description is not None and not isinstance(description, str):
            raise ValueError('description must be str')

        if source_type is not None and (not isinstance(source_type, str) and not isinstance(source_type, SourceType)):
            raise ValueError('source_type must be SourceType')

        if instances is not None and not isinstance(instances, int):
            raise ValueError('instances must be int')

        if size_bytes is not None and not isinstance(size_bytes, int):
            raise ValueError('size_bytes must be int')

        self.source_id = source_id
        self.created = created
        self.last_modified = last_modified
        self.last_access = last_access
        self.name = name
        self.description = description
        self.source_type = source_type
        self.instances = instances
        self.size_bytes = size_bytes

    def __eq__(self, other):
        if other is not None and not isinstance(other, SourceInfo):
            return False
        else:
            return self.source_id == other.source_id

    def __str__(self):
        return ' '.join([f'{k}={v}' for k, v in self.to_dict().items()])

    @staticmethod
    def from_dict(obj: Any) -> 'SourceInfo':
        """Builds a SourceInfo with a dictionary.

        Args:
            obj: :obj:`object` or :obj:`dict` containing the a serialized SourceInfo.

        Returns:
            SourceInfo containing the information stored in the given dictionary.
        """

        source_id = obj.get("id")
        created = parse_date(obj.get("created"))
        last_modified = parse_date(obj.get("last_modified"))
        last_access = parse_date(obj.get("last_access"))
        name = obj.get("name")
        description = obj.get("description")
        source_type = SourceType.from_string(obj.get("type"))
        instances = int(obj.get("instances"))
        size_bytes = int(obj.get("size_bytes"))
        return SourceInfo(source_id, created, last_modified, last_access, name,
                          description, source_type, instances,
                          size_bytes)

    def to_dict(self) -> Dict[str, Any]:
        """Builds a dictionary containing the information stored in current object.

        Returns:
            dictionary containing the information stored in the current object.
        """

        return {"id": self.source_id, "created": self.created.isoformat(),
                "last_modified": self.last_modified.isoformat(), "last_access": self.last_access.isoformat(),
                "name": self.name, "description": self.description, "source_type": self.source_type.name,
                "instances": int(self.instances), "size_bytes": int(self.size_bytes)}


class SourceInstances:
    """Operates over the instances of a concrete source.

    Note: This class should not be instanced, and only be used within an :obj:`deepint.core.source.Source`

    Attributes:
        source: the source with which to operate with its instances
    """

    def __init__(self, source: 'Source') -> None:
        self.source = source

    def fetch(self,
              select: str = None,
              where: str = None,
              order_by: str = None,
              order_type: str = None,
              offset: int = None,
              limit: int = None) -> pd.DataFrame:
        """Retrieves a source's instances.

        Args:
            select: features to retrieve. Note: all features must belon to the source.
            where: query in Deepint Query Language.
            order_by: feature by which to sort instances during retrieval.
            order_type: must be asc or desc.
            offset: number of instances to ignore during the retrieval.
            limit: maximum number of instances to retrieve.

        Returns:
            :obj:`pd.DataFrame`: containing the retrieved data.
        """

        order_type = 'asc' if order_type is None else order_type
        order_by = f'{order_by},{order_type}' if order_by is not None else None

        path = f'/api/v1/workspace/{self.source.workspace_id}/source/{self.source.info.source_id}/instances'
        headers = {'x-deepint-organization': self.source.organization_id}
        parameters = {
            'select': select,
            'where': where,
            'order_by': order_by,
            'offset': offset,
            'limit': limit
        }
        response = handle_request(method='GET', path=path, headers=headers,
                                  credentials=self.source.credentials, parameters=parameters)

        # format response
        result = [{
            feature['name']: instance[feature['index']]
            for feature in response['features']
        } for instance in response['instances']]

        df = pd.DataFrame(data=result)

        return df

    def update(self,
               data: pd.DataFrame,
               replace: bool = False,
               pk: str = None,
               date_format_feature: int = None,
               send_with_index: bool = False,
               **kwargs) -> Task:
        """Updates a source's instances.

        Args:
            data: data to update the instances. The column names must correspond to source's feature names.
            replace: if set to True the source's content is replaced by the new insertions.
            pk: feature used primary key during the instances insertion, to update the existing values and insert the not
                existing ones. If is provided with the replace set to True, all the instances will be replaced.
            date_format_feature: the input pk for the request body.
            send_with_index: if set to False the data is send without the index as first field. Else index is send.

        Returns:
            reference to task created to perform the source instances update operation.
        """

        # check arguments
        if data is not None and not isinstance(data, pd.DataFrame):
            raise DeepintBaseError(
                code='TYPE_MISMATCH', message='The provided input is not a DataFrame.')
        elif data.empty or data is None:
            raise DeepintBaseError(
                code='EMPTY_DATA', message='The provided DataFrame is empty.')
        elif len(data.columns) != len([f for f in self.source.features.fetch_all() if not f.computed]):
            raise DeepintBaseError(code='INPUTS_MISMATCH',
                                   message='The provided DataFrame must have same number of columns as current source.')
        else:
            for c in data.columns:
                if self.source.features.fetch(name=c) is None:
                    raise DeepintBaseError(code='INPUTS_MISMATCH',
                                           message='The provided DataFrame columns must have same names as the soure\'s features.')

        # retrieve index of date_format
        date_format = None
        if date_format_feature is not None:
            f = self.source_id.features.fetch(index=date_format_feature)
            if f is not None:
                date_format = f.date_format

        # convert content to CSV
        try:
            column_order = [
                f.name for f in self.source.features.fetch_all() if not f.computed]
            streaming_values_data = data.to_csv(sep=',',
                                                index=send_with_index,
                                                columns=column_order)
        except:
            raise DeepintBaseError(code='CONVERSION_ERROR',
                                   message='Unable to convert DataFrame to CSV. Please, check the index, columns and the capability of serialization for the DataFrame fields.')

        # request
        path = f'/api/v1/workspace/{self.source.workspace_id}/source/{self.source.info.source_id}/instances'
        headers = {'x-deepint-organization': self.source.organization_id}
        files = [('file', ('file', streaming_values_data))]
        parameters = {
            'replace': replace,
            'pk': pk if not replace else None,
            'separator': ',',
            'quotes': '"',
            'csv_header': 'yes',
            'parameters_fields': '',
            'date_format': date_format
        }
        response = handle_request(method='POST', path=path, headers=headers,
                                  parameters=parameters, files=files, credentials=self.source.credentials)

        # map response
        task = Task.build(task_id=response['task_id'], workspace_id=self.source.workspace_id,
                          organization_id=self.source.organization_id, credentials=self.source.credentials)

        return task

    def clean(self, where: str = None) -> Task:
        """ Removes a source's instances.

        Args:
            where: query in Deepint Query Language, to select which instances delete.

        Returns:
            reference to task created to perform the source instances deletion operation.
        """

        path = f'/api/v1/workspace/{self.source.workspace_id}/source/{self.source.info.source_id}/instances'
        headers = {'x-deepint-organization': self.source.organization_id}
        parameters = {
            'where': where
        }
        response = handle_request(method='DELETE', path=path, headers=headers,
                                  credentials=self.source.credentials, parameters=parameters)

        # map response
        task = Task.build(task_id=response['task_id'], workspace_id=self.source.workspace_id,
                          organization_id=self.source.organization_id, credentials=self.source.credentials)

        return task


class SourceFeatures:
    """Operates over the features of a concrete source.

    Note: This class should not be instanced, and only be used within an :obj:`deepint.core.source.Source`.

    Attributes:
        source: the source with which to operate with its features.
    """

    def __init__(self, source: 'Source', features: List[SourceFeature]) -> None:

        if features is not None and not isinstance(features, list):
            raise ValueError('features must be list')

        if features is not None:
            for f in features:
                if f is not None and not isinstance(f, SourceFeature):
                    raise ValueError(f'features must be a list of {SourceFeature.__class__}')

        self.source = source
        self._features = features
        if self._features is not None:
            self._features.sort(key=lambda x: x.index)

    def __eq__(self, other) -> bool:
        if other is not None and not isinstance(other, SourceFeatures):
            return False
        else:
            for f in self._features:
                other_f = other.fetch(name=f.name)
                if (other_f is not None) and f != other_f:
                    return False
            return True

    def load(self):
        """Loads a source's features.

        If the features were already loaded, this ones are replace by the new ones after retrieval.
        """

        # request
        path = f'/api/v1/workspace/{self.source.workspace_id}/source/{self.source.info.source_id}'
        headers = {'x-deepint-organization': self.source.organization_id}
        response = handle_request(
            method='GET', path=path, headers=headers, credentials=self.source.credentials)

        # map results
        self._features = [SourceFeature.from_dict(
            f) for f in response['features']]

    def update(self, features: List[SourceFeature] = None) -> Task:
        """Updates a source's features.

        If the features were already loaded, this ones are replace by the new ones after retrieval.

        Args:
            features: the new eatures to update the source. If not provided the source's internal ones are used.

        Returns:
            reference to task created to perform the source features update operation.
        """

        # check parameters
        features = features if features is not None else self._features

        # request
        path = f'/api/v1/workspace/{self.source.workspace_id}/source/{self.source.info.source_id}/features'
        headers = {'x-deepint-organization': self.source.organization_id}
        parameters = {'features': [f.to_dict_minimized() for f in features]}
        response = handle_request(method='POST', path=path, headers=headers,
                                  parameters=parameters, credentials=self.source.credentials)

        # update local state
        self._features = features

        # map response
        task = Task.build(task_id=response['task_id'], workspace_id=self.source.workspace_id,
                          organization_id=self.source.organization_id, credentials=self.source.credentials)

        return task

    def fetch(self, index: int = None, name: str = None, force_reload: bool = False) -> Optional[SourceFeature]:
        """Search for a feature in the source.

        Note: if no name or index is provided, the returned value is None.

        Args:
            index: feature's index to search by.
            name: feature's name to search by.
            force_reload: if set to True, features are reloaded before the search with the
                :obj:`deepint.core.source.SourceFeature.load` method.

        Returns:
            retrieved feature if found, and in other case None.
        """

        # if set to true reload
        if force_reload:
            self.load()

        # check parameters
        if index is None and name is None:
            return None

        # search
        for f in self._features:
            if f.index == index or f.name == name:
                return f
        return None

    def fetch_all(self, force_reload: bool = False) -> List[SourceFeature]:
        """Retrieves all source's features.

        Args:
            force_reload: if set to True, features are reloaded before the search with the
                :obj:`deepint.core.source.SourceFeature.load` method.

        Returns:
            the source's features.
        """

        # if set to true reload
        if force_reload:
            self.load()

        return self._features


class Source:
    """A Deep Intelligence source.

    Note: This class should not be instanced directly, and it's recommended to use the :obj:`deepint.core.source.Source.build`
    or :obj:`deepint.core.source.Source.from_url` methods.

    Attributes:
        organization_id: organization where source is located.
        workspace_id: workspace where source is located.
        info: :obj:`deepint.core.source.SourceInfo` to operate with source's information.
        instances: :obj:`deepint.core.source.SourceInstances` to operate with source's instances.
        features: :obj:`deepint.core.source.SourceFeatures` to operate with source's features.
        credentials: credentials to authenticate with Deep Intelligence API and be allowed to perform operations over the source. If
                 not provided, the credentials are generated with the :obj:`deepint.auth.credentials.Credentials.build`.
    """

    def __init__(self, organization_id: str, workspace_id: str, credentials: Credentials,
                 info: SourceInfo, features: List[SourceFeature]) -> None:

        if organization_id is not None and not isinstance(organization_id, str):
            raise ValueError('organization_id must be str')

        if workspace_id is not None and not isinstance(workspace_id, str):
            raise ValueError('workspace_id must be str')

        if credentials is not None and not isinstance(credentials, Credentials):
            raise ValueError(f'credentials must be {Credentials.__class__}')

        if info is not None and not isinstance(info, SourceInfo):
            raise ValueError(f'info must be {SourceInfo.__class__}')

        if features is not None and not isinstance(features, list):
            raise ValueError('features must be list')

        if features is not None:
            for f in features:
                if f is not None and not isinstance(f, SourceFeature):
                    raise ValueError(f'features must be a list of {SourceFeature.__class__}')

        self.info = info
        self.credentials = credentials
        self.workspace_id = workspace_id
        self.organization_id = organization_id
        self.instances = SourceInstances(self)
        self.features = SourceFeatures(self, features)

    def __str__(self):
        return f'<Source organization_id={self.organization_id} workspace={self.workspace_id} {self.info} features={self.features.fetch_all()}>'

    def __eq__(self, other):
        if other is not None and not isinstance(other, Source):
            return False
        else:
            return self.info == other.info

    @classmethod
    def build(cls, organization_id: str, workspace_id: str, source_id: str, credentials: Credentials = None) -> 'Source':
        """Builds a source.

        Note: when source is created, the source's information and features are retrieved from API.

        Args:
            organization_id: organization where source is located.
            workspace_id: workspace where source is located.
            source_id: source's id.
            credentials: credentials to authenticate with Deep Intelligence API and be allowed to perform operations over the source. If
                 not provided, the credentials are generated with the :obj:`deepint.auth.credentials.Credentials.build`.

        Returns:
            the source build with the given parameters and credentials.
        """

        credentials = credentials if credentials is not None else Credentials.build()
        src_info = SourceInfo(source_id=source_id, created=None, last_modified=None, last_access=None,
                              name=None, description=None, source_type=None, instances=None, size_bytes=None)
        src = cls(organization_id=organization_id, workspace_id=workspace_id,
                  credentials=credentials, info=src_info, features=None)
        src.load()
        src.features.load()

        # build the other source types classes if neccesary
        auto_updated_source_type = [SourceType.mysql, SourceType.ms_sql, SourceType.oracle, SourceType.pg, SourceType.url_parameters, SourceType.url_sql, SourceType.url_sqlite, SourceType.file_csv, SourceType.file_parameters, SourceType.file_sql, SourceType.file_sqlite, SourceType.url_csv, SourceType.url_json, SourceType.ckan, SourceType.s3, SourceType.mqtt, SourceType.mongo, SourceType.influx]

        if src.info.source_type == SourceType.external:
            src = ExternalSource.build(src)
        elif src.info.source_type == SourceType.rt:
            src = RealTimeSource.build(src)
        elif src.info.source_type in auto_updated_source_type:
            src = AutoUpdatedSource.build(src)

        return src

    @classmethod
    def from_url(cls, url: str, organization_id: str = None, credentials: Credentials = None) -> 'Source':
        """Builds a source from it's API or web associated URL.

        The url must contain the workspace's id and the source's id as in the following examples:

        Example:
            - https://app.deepint.net/o/3a874c05-26d1-4b8c-894d-caf90e40078b/workspace?ws=f0e2095f-fe2b-479e-be4b-bbc77207f42d&s=source&i=db98f976-f4bb-43d5-830e-bc18a3a89641
            - https://app.deepint.net/api/v1/workspace/f0e2095f-fe2b-479e-be4b-bbc77207f42/source/db98f976-f4bb-43d5-830e-bc18a3a89641

        Note: when source is created, the source's information and features are retrieved from API.
            Also it is remmarkable that if the API URL is providen, the organization_id must be provided in the optional parameter, otherwise
            this ID won't be found on the URL and the Organization will not be created, raising a value error.

        Args:
            url: the source's API or web associated URL.
            organization_id: the id of the organziation. Must be providen if the API URL is used.
            credentials: credentials to authenticate with Deep Intelligence API and be allowed to perform operations over the source. If
                 not provided, the credentials are generated with the :obj:`deepint.auth.credentials.Credentials.build`.

        Returns:
            the source build with the URL and credentials.
        """

        url_info, hostname = parse_url(url)

        if 'organization_id' not in url_info and organization_id is None:
            raise ValueError(
                'Fields organization_id must be in url to build the object. Or providen as optional parameter.')

        if 'workspace_id' not in url_info or 'source_id' not in url_info:
            raise ValueError(
                'Fields workspace_id and source_id must be in url to build the object.')

        organization_id = url_info['organization_id'] if 'organization_id' in url_info else organization_id

        # create new credentials
        new_credentials = Credentials(
            token=credentials.token, instance=hostname)

        return cls.build(organization_id=organization_id, workspace_id=url_info['workspace_id'], source_id=url_info['source_id'],
                         credentials=new_credentials)

    def load(self):
        """Loads the source's information.

        If the source's information is already loaded, is replace by the new one after retrieval.
        """

        # request
        path = f'/api/v1/workspace/{self.workspace_id}/source/{self.info.source_id}'
        headers = {'x-deepint-organization': self.organization_id}
        response = handle_request(
            method='GET', path=path, headers=headers, credentials=self.credentials)

        # map results
        self.info = SourceInfo.from_dict(response)

    def update(self, name: str = None, description: str = None):
        """Updates a source's name and description.

        Args:
            name: source's name. If not provided the source's name stored in the :obj:`deepint.core.source.Source.source_info` attribute is taken.
            descrpition: source's description. If not provided the source's description stored in the :obj:`deepint.core.source.Source.source_info` attribute is taken.
        """

        # check parameters
        name = name if name is not None else self.info.name
        description = description if description is not None else self.info.description

        # request
        path = f'/api/v1/workspace/{self.workspace_id}/source/{self.info.source_id}'
        headers = {'x-deepint-organization': self.organization_id}
        parameters = {'name': name, 'description': description}
        _ = handle_request(method='POST', path=path, headers=headers,
                                  parameters=parameters, credentials=self.credentials)

        # update local state
        self.info.name = name
        self.info.description = description

    def delete(self):
        """Deletes a source.
        """

        # request
        path = f'/api/v1/workspace/{self.workspace_id}/source/{self.info.source_id}'
        headers = {'x-deepint-organization': self.organization_id}
        handle_request(method='DELETE', path=path,
                       headers=headers, credentials=self.credentials)

    def clone(self, name: str = None) -> 'Source':
        """Clones a source.

        Args:
            name: name for the new source. If not providen the name will be `Copy of <current visualization's name>`

        Returns:
            the cloned source instance.
        """

        # generate name if not present
        if name is None:
            name = f'Copy of {self.info.name}'

        # request visualization clone
        path = f'/api/v1/workspace/{self.workspace_id}/source/{self.info.source_id}/clone'
        headers = {'x-deepint-organization': self.organization_id}
        parameters = {'name': name}
        response = handle_request(
            method='POST', path=path, parameters=parameters, headers=headers, credentials=self.credentials)

        new_source = Source.build(organization_id=self.organization_id, workspace_id=self.workspace_id,
                                                source_id=response['source_id'], credentials=self.credentials)
        return new_source

    def to_dict(self) -> Dict[str, Any]:
        """Builds a dictionary containing the information stored in current object.

        Returns:
            dictionary contining the information stored in the current object.
        """

        return {"info": self.info.to_dict(), "features": [x.to_dict() for x in self.features.fetch_all()]}


class RealTimeSource(Source):
    """Operates over a Deep Intelligence Real Time Source.

    Note: This class should not be instanced directly, and it's recommended to use the :obj:`deepint.core.source.Source.build`
    or :obj:`deepint.core.source.Source.from_url` methods.

    Attributes:
        organization_id: organization where source is located.
        workspace_id: workspace where source is located.
        info: :obj:`deepint.core.source.SourceInfo` to operate with source's information.
        instances: :obj:`deepint.core.source.SourceInstances` to operate with source's instances.
        features: :obj:`deepint.core.source.SourceFeatures` to operate with source's features.
        credentials: credentials to authenticate with Deep Intelligence API and be allowed to perform operations over the source. If
                 not provided, the credentials are generated with the :obj:`deepint.auth.credentials.Credentials.build`.
    """

    @classmethod
    def build(cls, source: Source) -> 'RealTimeSource':
        """Builds a Real-Time source from an :obj:`deepint.core.source.Source`

        This allows to use the Real Time data sources extra funcionality.

        Args:
            source: original source.

        Returns:
            the source build from the given source and credentials.
        """

        rt_src = cls(organization_id=source.organization_id, workspace_id=source.workspace_id, credentials=source.credentials, info=source.info, features=source.features.fetch_all(force_reload=True))
        rt_src.instances = RealTimeSourceInstances.build(rt_src)

        return rt_src

    def fetch_connection(self) -> Dict[str, Any]:
        """Retrieves Real Time source connection details. Currently on MQTT.

        Returns:
            a dictionary containing max_age number (Max age of registers in milliseconds. Set to 0 or negative
            for unlimited), mqtt_url (Connection URl to the MQTT service), mqtt_user (Username to authenticate
            to the source), mqtt_password (Password to authenticate to the source), mqtt_topic (Topic to
            publish registers to the source)
        """

        # request
        path = f'/api/v1/workspace/{self.workspace_id}/source/{self.info.source_id}/real_time'
        headers = {'x-deepint-organization': self.organization_id}
        response = handle_request(method='GET', path=path, headers=headers, credentials=self.credentials)

        return response

    def update_connection(self, max_age: int, regenerate_password: bool = False) -> None:
        """Updates the Realtime source connection details. Currently on MQTT.

        Args:
            max_age: maximum age of registers in milliseconds. Set to 0 or negative for unlimited
            regenerate_password: set to true to regenerate the MQTT password, if it was compromised. By default is false.
        """

        # request
        path = f'/api/v1/workspace/{self.workspace_id}/source/{self.info.source_id}/real_time'
        headers = {'x-deepint-organization': self.organization_id}
        parameters = {
            'max_age': max_age, 'regenerate_password': regenerate_password
        }
        _ = handle_request(method='POST', path=path, headers=headers, parameters=parameters, credentials=self.credentials)


class RealTimeSourceInstances(SourceInstances):
    """Operates over a Deep Intelligence Real Time Source's instances.

    Note: This class should not be instanced, and only be used within an :obj:`deepint.core.source.Source`

    Attributes:
        source: the source with which to operate with its instances
    """

    @classmethod
    def build(cls, source: Source) -> 'RealTimeSourceInstances':
        """Builds a Real-Time source instances from an :obj:`deepint.core.source.SourceInstances`

        This allows to use the Real Time data source instances extra funcionality.

        Args:
            source: original source.

        Returns:
            the source instances build from the given source and credentials.
        """

        return cls(source=source)

    def update(self, data: pd.DataFrame, **kwargs) -> None:
        """Overwrites the update on a real time source's instances.

        Note: it's important to highlight that only the data parameter is used.

        Args:
            data: data to update the instances. The column names must correspond to source's feature names.
        """

        # check arguments
        if data is not None and not isinstance(data, pd.DataFrame):
            raise DeepintBaseError(
                code='TYPE_MISMATCH', message='The provided input is not a DataFrame.')
        elif data.empty or data is None:
            raise DeepintBaseError(
                code='EMPTY_DATA', message='The provided DataFrame is empty.')
        elif len(data.columns) != len([f for f in self.source.features.fetch_all() if not f.computed]):
            raise DeepintBaseError(code='INPUTS_MISMATCH',
                                   message='The provided DataFrame must have same number of columns as current source.')
        else:
            for c in data.columns:
                if self.source.features.fetch(name=c) is None:
                    raise DeepintBaseError(code='INPUTS_MISMATCH',
                                           message='The provided DataFrame columns must have same names as the soure\'s features.')

        # calculate column order
        column_order = [f.name for f in self.source.features.fetch_all() if not f.computed]

        # convert dataframe to arrays
        dict_instances = data.to_dict(orient='records')
        instances = [[instance[c] for c in column_order] for instance in dict_instances]

        # request
        for instance in instances:
            path = f'/api/v1/workspace/{self.source.workspace_id}/source/{self.source.info.source_id}/real_time_push'
            headers = {'x-deepint-organization': self.source.organization_id}
            parameters = {
                'data': instance
            }
            _ = handle_request(method='POST', path=path, headers=headers, parameters=parameters, credentials=self.source.credentials)

    def clear_queued_instances(self, from_time: datetime, to_time: datetime) -> None:
        """Clears instances of a real time source between the limit of a time span.

        Args:
            from_time: start of clear range
            to_time: start of clear range
        """

        # convert times to unix timestamp in millis
        from_time_timestamp = from_time.timestamp() * 1e3
        to_time_timestamp = to_time.timestamp() * 1e3

        # request
        path = f'/api/v1/workspace/{self.source.workspace_id}/source/{self.source.info.source_id}/real_time_clear'
        headers = {'x-deepint-organization': self.source.organization_id}
        parameters = {
            'from_time': from_time_timestamp,
            'to_time': to_time_timestamp
        }
        _ = handle_request(method='POST', path=path, headers=headers, parameters=parameters, credentials=self.source.credentials)


class ExternalSource(Source):
    """Operates over a Deep Intelligence External Source.

    To learn more about external sources, please check the (External Sources documentation)[https://deepintdev.github.io/deepint-documentation/EXTERNAL-SOURCES.html].

    Note: This class should not be instanced directly, and it's recommended to use the :obj:`deepint.core.source.Source.build`
    or :obj:`deepint.core.source.Source.from_url` methods.

    Attributes:
        organization_id: organization where source is located.
        workspace_id: workspace where source is located.
        info: :obj:`deepint.core.source.SourceInfo` to operate with source's information.
        instances: :obj:`deepint.core.source.SourceInstances` to operate with source's instances.
        features: :obj:`deepint.core.source.SourceFeatures` to operate with source's features.
        credentials: credentials to authenticate with Deep Intelligence API and be allowed to perform operations over the source. If
                 not provided, the credentials are generated with the :obj:`deepint.auth.credentials.Credentials.build`.
    """

    @classmethod
    def build(cls, source: Source) -> 'ExternalSource':
        """Builds an External source from an :obj:`deepint.core.source.Source`

        This allows to use the External sources extra funcionality.

        Args:
            source: original source.

        Returns:
            the source build from the given source and credentials.
        """

        external_src = cls(organization_id=source.organization_id, workspace_id=source.workspace_id, credentials=source.credentials, info=source.info, features=source.features.fetch_all(force_reload=True))
        external_src.instances = ExternalSourceInstances.build(external_src)

        return external_src

    def fetch_connection(self) -> str:
        """Gets external source connection URL.

        Returns:
            the URL to connect to external source
        """

        # request
        path = f'/api/v1/workspace/{self.workspace_id}/source/{self.info.source_id}/connection'
        headers = {'x-deepint-organization': self.organization_id}
        response = handle_request(method='GET', path=path, headers=headers, credentials=self.credentials)

        # retrieve url
        url = response['url']
        url = url.replace('|EX|', '')

        return url

    def update_connection(self, url: str) -> None:
        """Gets external source connection URL.

        Args:
            url: the URL to connect to external source
        """

        # request
        path = f'/api/v1/workspace/{self.workspace_id}/source/{self.info.source_id}/connection'
        headers = {'x-deepint-organization': self.organization_id}
        parameters = {'url': url}
        _ = handle_request(method='POST', path=path, headers=headers, parameters=parameters, credentials=self.credentials)


class ExternalSourceInstances(SourceInstances):
    """Operates over a Deep Intelligence External Source's instances.

    Note: This class should not be instanced, and only be used within an :obj:`deepint.core.source.Source`

    Attributes:
        source: the source with which to operate with its instances
        connection_url: url to update instances from  external source.
    """

    @classmethod
    def build(cls, source: Source) -> 'ExternalSourceInstances':
        """Builds a External source instances from an :obj:`deepint.core.source.SourceInstances`

        This allows to use the External source instances extra funcionality.

        Args:
            source: original source.

        Returns:
            the source instances build from the given source and credentials.
        """

        return cls(source=source)

    def update(self, *args, **kwargs) -> None:
        """Overwrites the update on a external source's instances.
        """

        raise DeepintBaseError(code='OPERATION_NOT_ALLOWED', message='An external source can not be updated throught Deep Intelligence. The update must be performed internally.')


class AutoUpdatedSource(Source):
    """Operates over a Deep Intelligence autoupdated source.

    Note: This class should not be instanced directly, and it's recommended to use the :obj:`deepint.core.source.Source.build`
    or :obj:`deepint.core.source.Source.from_url` methods.

    Attributes:
        organization_id: organization where source is located.
        workspace_id: workspace where source is located.
        info: :obj:`deepint.core.source.SourceInfo` to operate with source's information.
        instances: :obj:`deepint.core.source.SourceInstances` to operate with source's instances.
        features: :obj:`deepint.core.source.SourceFeatures` to operate with source's features.
        credentials: credentials to authenticate with Deep Intelligence API and be allowed to perform operations over the source. If
                 not provided, the credentials are generated with the :obj:`deepint.auth.credentials.Credentials.build`.
    """

    @classmethod
    def build(cls, source: Source) -> 'AutoUpdatedSource':
        """Builds an External source from an :obj:`deepint.core.source.Source`

        This allows to use the External sources extra funcionality.

        Args:
            source: original source.

        Returns:
            the source build from the given source and credentials.
        """

        autoupdated_source = cls(organization_id=source.organization_id, workspace_id=source.workspace_id, credentials=source.credentials, info=source.info, features=source.features.fetch_all(force_reload=True))

        return autoupdated_source

    def fetch_actualization_config(self) -> Dict[str, Any]:
        """Retrieves autoupdate configuration.

        Returns:
            a dictionary containing the autoupdate configuration
        """

        # request
        path = f'/api/v1/workspace/{self.workspace_id}/source/{self.info.source_id}/autoupdate'
        headers = {'x-deepint-organization': self.organization_id}
        response = handle_request(method='GET', path=path, headers=headers, credentials=self.credentials)

        # fecth results
        autoupdate_config = response['updateConfig']

        return autoupdate_config

    def update_actualization_config(self, is_json_content: bool = None, is_csv_content: bool = None, auto_update: bool = None, auto_update_period: int = None, replace_on_update: bool = None, pk_for_update: str = None, update_duplicates: bool = None, separator: str = None, quotes: str = None, has_csv_header: bool = None, json_fields: List[str] = None, json_prefix: str = None, is_single_json_obj: bool = None, date_format: str = None, url: str = None, http_headers: Dict[str, str] = None, ignore_security_certificates: bool = None, enable_store_data_parameters: bool = None, stored_data_parameters_name: str = None, stored_data_parameters_sorting_desc: bool = None, database_name: str = None, database_user: str = None, database_password: str = None, database_table: str = None, database_query: str = None, mongodb_sort: Dict[str, Any] = None, mongodb_project: str = None, database_query_limit: int = None, database_host: str = None, database_port: str = None, mqtt_topics: List[str] = None, mqtt_fields: List[Dict[str, str]] = None, database_type: SourceType = None) -> None:
        """Updates the auto udpate source configuration.

        Note: the not providen configuration, is taken from the current source configuration, fetched from Deep Intelligence.

        Args:
            auto_update: set to true to enable auto update
            auto_update_period: auto update delay in milliseconds. Minimum is 5 minutes.
            replace_on_update: set to true to replace the entire data set with each update. False to append the data.
            pk_for_update: Name of the primary key field. In order to check for duplicates when appending.
            update_duplicates: Set to true to update existing rows (by primary key). Set to false to skip duplicate rows. If you set dyn_replace to true. This option does not have any effect.
            separator: separator character for csv files
            quotes: quotes character for csv files.
            has_csv_header: Set to false if the csv files does not have a header.
            json_fields: List of fileds to get, in order, for json files or mongo databases.
            json_prefix: Prefix to tell the engine where the data is in the JSON file. Use dots to split levels.
            is_single_json_obj: Set to true in case there is a single instance in the JSON.
            date_format: Date format in the CSV of JSON file. By default is the ISO format. This uses the Moment.js formats.
            url: URL for url/any and ckan source types. In case of S3. This is the URI of the object inside the bucket. For mongo and influx, this is the connection URL.
            is_csv_content: Set to True to indicate that is a CSV content. Otherwise the content will be considered as JSON.
            http_headers: Custom headers to send by Deep Intelligence for requesting the data. example: "example: Header1: Value1 Header2: Value2"
            ignore_security_certificates:   Set to true to ignore invalid certificates for HTTPs
            enable_store_data_parameters: Set to true to enable stored data parameter in the Query. Any instances of ${SDP} will be replaced.
            stored_data_parameters_name: Name of the field to use for SDP.
            stored_data_parameters_sorting: Sorting direction to calc the SDP. Must be asc or desc.
            database_name: Name of the database or the S3 bucket.
            database_user: User / Access key ID
            database_password: Password / Secret key
            database_table: Name of the table / collection
            database_query: Database Query. For mongo, this is a JSON.
            database_type: the type of database for relational database.
            mongodb_sort: For MongoDB. Sorting
            mongodb_project: MongoDB project.
            database_query_limit: Limit of results per Deep Intelligent data retrieval query against source.
            database_host: Database host
            database_port: Port number
            mqtt_topics: For MQTT, list of topics split by commas.
            mqtt_fields: List of expected fields for MQTT. Read Deep Intelligence advanced documentation for more information.
        """

        # create calculated parameters

        if is_csv_content is True and is_json_content is True:
            raise DeepintBaseError(code='BAD_PARAMETERS', message='Unable to update the source if is_csv_content and is_json_content is True at same time.')

        if is_json_content is not None or is_csv_content is not None:
            parser = 'csv' if is_csv_content is not None and is_csv_content is True else 'json'
        else:
            parser = None

        if is_single_json_obj is not None:
            json_mode = 'single' if is_single_json_obj is True else 'default'
        else:
            json_mode = None

        if stored_data_parameters_sorting_desc is not None:
            stored_data_parameters_sorting = 'desc' if stored_data_parameters_sorting_desc else 'asc'
        else:
            stored_data_parameters_sorting = None

        # apply previous processings

        if http_headers is not None:
            http_headers = ' '.join([f'{k}={v}' for k, v in http_headers.items()]) if http_headers is not None else None

        if mqtt_topics is not None:
            mqtt_topics = ','.join(mqtt_topics) if mqtt_topics is not None else mqtt_topics

        if database_type is not None:
            if database_type not in [SourceType.mysql, SourceType.pg, SourceType.oracle, SourceType.ms_sql, SourceType.mysql]:
                raise DeepintBaseError(code='OPERATION_NOT_ALLOWED', message='The database type providen must be a relational databse such as mysql, pg, oracle, ms_sql or mysql.')
            else:
                database_type = database_type.name

        # fech current configuration and fill not providen parameters

        current_config = self.fetch_actualization_config()
        update_config = current_config['configuration']

        auto_update = auto_update if auto_update is not None else (current_config['enabled'] if 'enabled' in current_config else None)
        auto_update_period = auto_update_period if auto_update_period is not None else (current_config['delay'] if 'delay' in current_config else None)
        replace_on_update = replace_on_update if replace_on_update is not None else (current_config['replace'] if 'replace' in current_config else None)
        pk_for_update = pk_for_update if pk_for_update is not None else (current_config['pk'] if 'pk' in current_config else None)
        update_duplicates = update_duplicates if update_duplicates is not None else (current_config['updateMode'] if 'updateMode' in current_config else None)
        separator = separator if separator is not None else (update_config['separator'] if 'separator' in current_config else None)
        quotes = quotes if quotes is not None else (update_config['quotes'] if 'quotes' in current_config else None)
        has_csv_header = has_csv_header if has_csv_header is not None else ((not update_config['noheader']) if 'noheader' in update_config else None)
        json_fields = json_fields if json_fields is not None else (update_config['json_fields'] if 'json_fields' in update_config else None)
        json_prefix = json_prefix if json_prefix is not None else (update_config['json_prefix'] if 'json_prefix' in update_config else None)
        json_mode = json_mode if json_mode is not None else (update_config['json_mode'] if 'json_mode' in update_config else None)
        date_format = date_format if date_format is not None else (update_config['date_format'] if 'date_format' in update_config else None)
        url = url if url is not None else (update_config['url'] if 'url' in update_config else None)
        parser = parser if parser is not None else (update_config['parser'] if 'parser' in update_config else None)
        http_headers = http_headers if http_headers is not None else (update_config['http_headers'] if 'http_headers' in update_config else None)
        ignore_security_certificates = ignore_security_certificates if ignore_security_certificates is not None else (update_config['rejectUnauthorized'] if 'rejectUnauthorized' in update_config else None)
        enable_store_data_parameters = enable_store_data_parameters if enable_store_data_parameters is not None else (update_config['sdp_enabled'] if 'sdp_enabled' in update_config else None)
        stored_data_parameters_name = stored_data_parameters_name if stored_data_parameters_name is not None else (update_config['sdp_name'] if 'sdp_name' in update_config else None)
        stored_data_parameters_sorting = stored_data_parameters_sorting if stored_data_parameters_sorting is not None else (update_config['sdp_dir'] if 'sdp_dir' in update_config else None)
        database_name = database_name if database_name is not None else (update_config['database'] if 'database' in update_config else None)
        database_user = database_user if database_user is not None else (update_config['user'] if 'user' in update_config else None)
        database_password = database_password if database_password is not None else (update_config['password'] if 'password' in update_config else None)
        database_table = database_table if database_table is not None else (update_config['table'] if 'table' in update_config else None)
        database_query = database_query if database_query is not None else (update_config['query'] if 'query' in update_config else None)
        mongodb_sort = mongodb_sort if mongodb_sort is not None else (update_config['sort'] if 'sort' in update_config else None)
        mongodb_project = mongodb_project if mongodb_project is not None else (update_config['project'] if 'project' in update_config else None)
        database_query_limit = database_query_limit if database_query_limit is not None else (update_config['limit'] if 'limit' in update_config else None)
        database_type = database_type if database_type is not None else (update_config['db'] if 'db' in update_config else None)
        database_host = database_host if database_host is not None else (update_config['host'] if 'host' in update_config else None)
        database_port = database_port if database_port is not None else (update_config['port'] if 'port' in update_config else None)
        mqtt_topics = mqtt_topics if mqtt_topics is not None else (update_config['topics'] if 'topics' in update_config else None)
        mqtt_fields = mqtt_fields if mqtt_fields is not None else (update_config['fields_expected'] if 'fields_expected' in update_config else None)

        # request
        path = f'/api/v1/workspace/{self.workspace_id}/source/{self.info.source_id}/autoupdate'
        headers = {'x-deepint-organization': self.organization_id}
        parameters = {
            "dyn_enabled": auto_update, "dyn_delay": auto_update_period, "dyn_replace": replace_on_update, "dyn_update_mode": update_duplicates, "dyn_pk": pk_for_update, "separator": separator, "quotes": quotes, "noheader": not has_csv_header, "json_prefix": json_prefix, "json_mode": json_mode, "json_fields": json_fields, "date_format": date_format, "url": url, "parser": parser, "http_headers": http_headers, "rejectUnauthorized": ignore_security_certificates, "sdp_enabled": enable_store_data_parameters, "sdp_name": stored_data_parameters_name, "sdp_dir": stored_data_parameters_sorting, "database": database_name, "user": database_user, "password": database_password, "table": database_table, "query": database_query, "sort": mongodb_sort, "project": mongodb_project, "db": database_type, "host": database_host, "limit": database_query_limit, "port": database_port, "topics": mqtt_topics, "fields_expected": mqtt_fields
        }

        _ = handle_request(method='POST', path=path, headers=headers, parameters=parameters, credentials=self.credentials)
