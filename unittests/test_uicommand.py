#!/usr/bin/env python3

import unittest

from PyQt5 import QtCore, QtWidgets

from pyqtcmd import History, Command, UICommand, UndoUICommandMixin, RedoUICommandMixin, NeedsSelectionUICommandMixin


class DummyCommand(Command):
    def __init__(self):
        self.done = False

    def do(self):
        self.done = True

    def undo(self):
        self.done = False


class DummyUICommand(UICommand):
    def __init__(self, *args, history, **kwargs):
        self.done = False
        self.enabled = True
        self._history = history
        super().__init__(*args, **kwargs)

    def history(self):
        return self._history

    def do(self):
        self.done = True

    def should_be_enabled(self):
        return super().should_be_enabled() and self.enabled


class NeedsSelectionUICommand(NeedsSelectionUICommandMixin, DummyUICommand):
    pass


class DummyContainer(QtCore.QObject):
    selectionChanged = QtCore.pyqtSignal()

    def __init__(self):
        self._selection = set()
        super().__init__()

    def selection(self):
        return self._selection

    def add(self, item):
        self._selection.add(item)
        self.selectionChanged.emit()

    def remove(self, item):
        self._selection.remove(item)
        self.selectionChanged.emit()


class UndoUICommand(UndoUICommandMixin, DummyUICommand):
    pass


class RedoUICommand(RedoUICommandMixin, DummyUICommand):
    pass


class UICommandTestCase(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.app = QtWidgets.QApplication([])
        self.history = History()


class UICommandTest(UICommandTestCase):
    def setUp(self):
        super().setUp()
        self.uicommand = DummyUICommand(history=self.history)

    def test_initial_enabled(self):
        self.assertTrue(self.uicommand.isEnabled())

    def test_trigger(self):
        self.uicommand.trigger()
        self.assertTrue(self.uicommand.done)

    def test_enable_state_change(self):
        self.uicommand.enabled = False
        self.history.changed.emit()
        self.assertFalse(self.uicommand.isEnabled())

    def test_enable_signal_check(self):
        class Test(QtCore.QObject):
            changed = QtCore.pyqtSignal()

        test = Test()
        self.uicommand.add_signal_check(test.changed)
        self.uicommand.enabled = False
        test.changed.emit()
        self.assertFalse(self.uicommand.isEnabled())


class UndoRedoUICommandTest(UICommandTestCase):
    def test_undo_disabled(self):
        undo = UndoUICommand(history=self.history)
        self.assertFalse(undo.isEnabled())

    def test_redo_disabled(self):
        redo = RedoUICommand(history=self.history)
        self.assertFalse(redo.isEnabled())

    def test_command_enables_undo(self):
        undo = UndoUICommand(history=self.history)
        cmd = DummyCommand()
        self.history.run(cmd)
        self.assertTrue(undo.isEnabled())

    def test_command_does_not_enable_redo(self):
        redo = RedoUICommand(history=self.history)
        cmd = DummyCommand()
        self.history.run(cmd)
        self.assertFalse(redo.isEnabled())

    def test_undo_enables_redo(self):
        redo = RedoUICommand(history=self.history)
        cmd = DummyCommand()
        self.history.run(cmd)
        self.history.undo()
        self.assertTrue(redo.isEnabled())

    def test_undo_undoes(self):
        undo = UndoUICommand(history=self.history)
        cmd = DummyCommand()
        self.history.run(cmd)
        undo.do()
        self.assertFalse(cmd.done)

    def test_redo_redoes(self):
        redo = RedoUICommand(history=self.history)
        cmd = DummyCommand()
        self.history.run(cmd)
        self.history.undo()
        redo.do()
        self.assertTrue(cmd.done)


class NeedsSelectionMixinTest(UICommandTestCase):
    def setUp(self):
        super().setUp()
        self.container = DummyContainer()
        self.uicommand = NeedsSelectionUICommand(container=self.container, history=self.history)

    def test_initially_disabled(self):
        self.assertFalse(self.uicommand.isEnabled())

    def test_initially_enabled(self):
        container = DummyContainer()
        container.add(42)
        uicommand = NeedsSelectionUICommand(container=container, history=self.history)
        self.assertTrue(uicommand.isEnabled())

    def test_add_enables(self):
        self.container.add(42)
        self.assertTrue(self.uicommand.isEnabled())

    def test_remove_disables(self):
        self.container.add(42)
        self.container.remove(42)
        self.assertFalse(self.uicommand.isEnabled())
