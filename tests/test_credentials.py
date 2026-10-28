#!usr/bin/python

# Copyright 2023 Deep Intelligence
# See LICENSE for details.

# Offline tests for credentials loading. They do not need a running instance.

import pytest
from deepint import Credentials, DeepintCredentialsError

ENV_VARS = ('AIRCORE_TOKEN', 'AIRCORE_INSTANCE', 'DEEPINT_TOKEN', 'DEEPINT_INSTANCE')


@pytest.fixture(autouse=True)
def clean_env(monkeypatch, tmp_path):
    for name in ENV_VARS:
        monkeypatch.delenv(name, raising=False)
    # isolate the ~/.deepint.ini lookup from the real home directory
    monkeypatch.setenv('HOME', str(tmp_path))
    return tmp_path


def test_default_instance():
    assert Credentials(token='t').instance == 'app.air-core.io'
    assert Credentials.build(token='t').instance == 'app.air-core.io'


def test_explicit_instance_is_kept():
    assert Credentials(token='t', instance='app.deepint.net').instance == 'app.deepint.net'
    assert Credentials.build(token='t', instance='app.deepint.net').instance == 'app.deepint.net'


def test_legacy_env_vars(monkeypatch):
    monkeypatch.setenv('DEEPINT_TOKEN', 'legacy')
    monkeypatch.setenv('DEEPINT_INSTANCE', 'app.deepint.net')
    c = Credentials.build()
    assert c.token == 'legacy'
    assert c.instance == 'app.deepint.net'


def test_legacy_token_env_default_instance(monkeypatch):
    monkeypatch.setenv('DEEPINT_TOKEN', 'legacy')
    assert Credentials.build().instance == 'app.air-core.io'


def test_aircore_env_vars_take_precedence(monkeypatch):
    monkeypatch.setenv('DEEPINT_TOKEN', 'legacy')
    monkeypatch.setenv('DEEPINT_INSTANCE', 'app.deepint.net')
    monkeypatch.setenv('AIRCORE_TOKEN', 'new')
    monkeypatch.setenv('AIRCORE_INSTANCE', 'onpremise.example.com')
    c = Credentials.build()
    assert c.token == 'new'
    assert c.instance == 'onpremise.example.com'


def test_mixed_env_vars(monkeypatch):
    monkeypatch.setenv('AIRCORE_TOKEN', 'new')
    monkeypatch.setenv('DEEPINT_INSTANCE', 'app.deepint.net')
    c = Credentials.build()
    assert c.token == 'new'
    assert c.instance == 'app.deepint.net'


def test_home_file(clean_env):
    (clean_env / '.deepint.ini').write_text('[DEFAULT]\ntoken = file\n')
    c = Credentials.build()
    assert c.token == 'file'
    assert c.instance == 'app.air-core.io'


def test_home_file_instance(clean_env):
    (clean_env / '.deepint.ini').write_text('[DEFAULT]\ntoken = file\ninstance = app.deepint.net\n')
    assert Credentials.build().instance == 'app.deepint.net'


def test_missing_token_raises():
    with pytest.raises(DeepintCredentialsError):
        Credentials.build()
