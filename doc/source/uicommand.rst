
uicommand: interfacing commands with UI elements
================================================

Whereas `Command` object encapsulate something that happens to the model, `UICommand` objects are associated to an UI element and are triggered by it (it's actually a subclass of QAction). They will typically create a new `Command` and run it in their `do()` method, each time it's invoked.

.. automodule:: pyqtcmd.uicommand
   :members:
