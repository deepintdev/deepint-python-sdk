
Authentication
==============

This package interacts with `AIR-Core API <https://app.air-core.io/api/v1/documentation/>`_. Therefore, it is necessary to provide a token in the header of each transaction, which must be provided to this package in order to operate. 
This section discusses how to provide such a token to the package in the various ways in which it is offered.


How to setup credentials
------------------------

Credentials can be set up with one of the following methods (the token is loaded in the priority defined in the order of the following items):
 - instance credentials object with the token and instance optional parameters `c = Credentials(token='a token', instance='app.air-core.io')`
 - create a environment variable called `AIRCORE_TOKEN` with the token value and another one called `AIRCORE_INSTANCE`. The previous names `DEEPINT_TOKEN` and `DEEPINT_INSTANCE` are still supported; when both are set, the `AIRCORE_*` variables take precedence.
 - create a .ini file in your home directory called `.deepint` coninting in the `DEFAULT` section the key `token` and the key `instance` like in following example

.. code-block::
   :caption: ~/.deepint.ini

	[DEFAULT]
	token=a token
   instance=host to connect with (if not providen app.air-core.io will be taken by default)

Note: If instance is not providen, the default value will be the SaaS instance `app.air-core.io`. Since version 1.5.0 this default changed from `app.deepint.net`; if you need to keep using that host, set it explicitly with the `instance` parameter, the `AIRCORE_INSTANCE`/`DEEPINT_INSTANCE` environment variable or the `.deepint.ini` file.


How to obtain a token
---------------------

In order to interact with the AIR-Core API, it is necessary to obtain a token that is attached to each request. To do this, first, you must log in, after which you must go to the `account configuration page <https://app.air-core.io/workspace?ws=&s=account>`_  and go to the "Authorizations" section. There you must click on the "Create new authorization token" button as shown in the image below:

.. image:: ../../static/images/obtain_token_step_1.PNG
   :width: 600

After that, a modal will appear, where you can configure the permissions and expiration of the token:

.. image:: ../../static/images/obtain_token_step_2.PNG
   :width: 600

Finally, by pressing the key button as shown in the image below, the token is obtained:

.. image:: ../../static/images/obtain_token_step_3.PNG
   :width: 600

It is important to highlight that the token is associated to the user and not to the organization, which means that the same token can be used to access multiple organizations.


How to set a on-premise instance
--------------------------------

If you are using a on-premise instance of AIR-Core, it's neccesary to setup the instance parameter in one of the following ways
 - provide the host or IP of the on-premise instance when instancing the credentials or using the `Credentials.build` method `c = Credentials(token='a token', instance='onpremise.example.com')`
 - create a environment variable called `AIRCORE_INSTANCE` (or the legacy `DEEPINT_INSTANCE`) with the host or IP of the on-premise instance.
 - create a .ini file in your home directory called `.deepint` coninting in the `DEFAULT` section the key `instance` with the host or IP of the on-premise instance.
