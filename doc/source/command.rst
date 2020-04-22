
command: where the actual stuff happens
=======================================

Command objects encapsulate a change to the underlying model of your
application. For instance you may have a Command class to change the
project's name, and an instance of this for each actual name
change. Once instantiated it must be actually run by using the History
`run` method.

.. automodule:: pyqtcmd.command
   :members:
