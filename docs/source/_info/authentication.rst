
Authentication
==============

This package interacts with `DeepIntelligence API <https://app.deepint.net/api/v1/documentation/>`_. Therefore, it is necessary to provide a token in the header of each transaction, which must be provided to this package in order to operate. 
This section discusses how to provide such a token to the package in the various ways in which it is offered.

How to setup credentials
------------------------

Credentials can be set up with one of the following methods (the token is loaded in the priority defined in the order of the following items):
 - instance credentials object with the token optional parameter `c = Credentials(token='a token')`
 - create a environment variable called `DEEPINT_TOKEN` with the token value.
 - create a .ini file in your home directory called `.deepint` coninting in the `DEFAULT` section a key called `token` like in following example

.. code-block::
   :caption: ~/.deepint.ini

	[DEFAULT]
	token=a token
