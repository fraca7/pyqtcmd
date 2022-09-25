#!/usr/bin/env python3

"""
Integration of commands with UI elements
"""

try:
    from PyQt5 import QtWidgets
    QAction = QtWidgets.QAction
except ModuleNotFoundError: # pragma: no cover
    from PyQt6 import QtGui
    QAction = QtGui.QAction


class UICommand(QAction):
    """
    An UICommand is the intermediate between UI elements and the
    underlying Commands. A Command encapsulates a single behavior; an
    UICommand has a longer life time since it's associated to a UI
    element. Its role is to instantiate and run the right Command when
    the user interacts with the element. It also has an
    enabled/disabled state that you can manage by overriding the
    should_be_enabled() method.
    """
    def __init__(self, parent=None, *, text=None, icon=None, shortcut=None, tip=None):
        super().__init__(parent)
        self.triggered.connect(self.do)
        self._check()
        self.history().changed.connect(self._check)

        if text is not None:
            self.setText(text) # pragma: no cover
        if icon is not None:
            self.setIcon(icon) # pragma: no cover
        if shortcut is not None:
            self.setShortcut(shortcut) # pragma: no cover
        if tip is not None:
            self.setToolTip(tip)
            self.setStatusTip(tip)

    def history(self):
        """Override this to return the History object"""
        raise NotImplementedError # pragma: no cover

    def add_signal_check(self, signal):
        """
        Call this, passing it a signal that could change the UIAction
        state (enabled/disabled, etc) when it's fired. The signal's
        signature does not matter.
        """
        signal.connect(self._check)

    def should_be_enabled(self): # pylint: disable=R0201
        """Return False from this method if the underlying UI element should be disabled."""
        return True

    def do(self):
        """
        Subclasses should override this to do whatever is necessary
        (for instance show a dialog for choosing a file name, etc) and
        then instantiate the right Command class and run() it.
        """
        raise NotImplementedError # pragma: no cover

    def set_button(self, btn):
        """
        Associates this command to a push button.
        """
        def changed():
            btn.setText(self.text())
            btn.setIcon(self.icon())
            btn.setEnabled(self.isEnabled())
            btn.setToolTip(self.toolTip())
            btn.setStatusTip(self.statusTip())
            btn.setVisible(self.isVisible())
        btn.clicked.connect(self.do)
        self.changed.connect(changed)
        changed()

    def _check(self, *unused_):
        self.setEnabled(self.should_be_enabled())


class UndoUICommandMixin:
    """
    Undo UICommand. This is a mixin so you can inherit from your concrete UICommand subclass.
    """
    def __init__(self, *args, text=None, **kwargs):
        self.__original_text = text
        super().__init__(*args, text=text, **kwargs)

    def do(self): # pylint: disable=C0111
        self.history().undo()

    def should_be_enabled(self): # pylint: disable=C0111
        return self.history().can_undo()

    def _check(self, *unused_):
        self.setText(self.history().undo_label() or self.__original_text)
        super()._check()


class RedoUICommandMixin:
    """
    Redo UICommand. This is a mixin so you can inherit from your concrete UICommand subclass.
    """
    def __init__(self, *args, text=None, **kwargs):
        self.__original_text = text
        super().__init__(*args, text=text, **kwargs)

    def do(self): # pylint: disable=C0111
        self.history().redo()

    def should_be_enabled(self): # pylint: disable=C0111
        return self.history().can_redo()

    def _check(self, *unused_):
        self.setText(self.history().redo_label() or self.__original_text)
        super()._check()


class NeedsSelectionUICommandMixin:
    """
    A mixin for UICommand. The constructor takes a `container` keyword
    argument. This must be an object which implements a
    `selectionChanged` signal (of any signature) and a `selection()`
    method, which should return the selection as an object with a
    __len__.
    """

    def __init__(self, parent=None, *, container, **kwargs):
        self._container = container
        super().__init__(parent, **kwargs)
        self.add_signal_check(container.selectionChanged)

    def container(self):
        """
        Accessor for the underlying container
        """
        return self._container

    def selection(self):
        """
        Returns the current selection. If you want to implement more
        drastic limitations than 'selection is not empty' you can
        override this to filter the actual underlying selection. The
        action will be enabled iff this returns a non-empty iterable.
        """
        return self.container().selection()

    def should_be_enabled(self): # pylint: disable=C0111
        return len(self.selection()) != 0 and super().should_be_enabled()
