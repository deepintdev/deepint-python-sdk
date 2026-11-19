Alert (removed)
===============

.. deprecated:: 2.0.0
   The alerts were removed from the AIR-Core API and are now automations (:doc:`automation`). Every method of these
   classes that called the API raises :obj:`deepint.error.DeepintAlertsRemovedError`, naming its replacement.

.. autoclass:: deepint.core.Alert
   :exclude-members:
   :members:

.. autoclass:: deepint.core.AlertType
   :exclude-members:
   :members:

.. autoclass:: deepint.core.alert.AlertInfo
   :exclude-members:
   :members:

.. autoclass:: deepint.core.alert.AlertInstances
   :exclude-members:
   :members:

.. autoclass:: deepint.core.alert.AlertWebhook
   :exclude-members:
   :members:
