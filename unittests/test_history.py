#!/usr/bin/env python3

import unittest

from pyqtcmd import History, Command, ConsistencyError


class DummyCommand(Command):
    def __init__(self):
        self.done = False

    def do(self):
        self.done = True

    def undo(self):
        self.done = False


class HistoryBaseTestCase(unittest.TestCase):
    def setUp(self):
        self.history = History()
        self.changed = 0
        self.history.changed.connect(self._changed)

    def tearDown(self):
        self.history.changed.disconnect(self._changed)

    def _changed(self):
        self.changed += 1


class HistoryInitialTestCase(HistoryBaseTestCase):
    def test_cannot_undo(self):
        self.assertFalse(self.history.can_undo())

    def test_cannot_redo(self):
        self.assertFalse(self.history.can_redo())

    def test_is_not_modified(self):
        self.assertFalse(self.history.is_modified())

    def test_undo_raises(self):
        with self.assertRaises(ConsistencyError):
            self.history.undo()

    def test_redo_raises(self):
        with self.assertRaises(ConsistencyError):
            self.history.redo()


class HistoryPastTestCase(HistoryBaseTestCase):
    def setUp(self):
        super().setUp()
        self.cmd = DummyCommand()
        self.history.run(self.cmd)

    def test_command_done(self):
        self.assertTrue(self.cmd.done)

    def test_command_can_undo(self):
        self.assertTrue(self.history.can_undo())

    def test_command_cannot_redo(self):
        self.assertFalse(self.history.can_redo())

    def test_command_changed(self):
        self.assertEqual(self.changed, 1)

    def test_command_is_modified(self):
        self.assertTrue(self.history.is_modified())


class HistoryFutureTestCase(HistoryBaseTestCase):
    def setUp(self):
        super().setUp()
        self.cmd = DummyCommand()
        self.history.run(self.cmd)
        self.history.undo()

    def test_command_undone(self):
        self.assertFalse(self.cmd.done)

    def test_command_cannot_undo(self):
        self.assertFalse(self.history.can_undo())

    def test_command_can_redo(self):
        self.assertTrue(self.history.can_redo())

    def test_command_changed(self):
        self.assertEqual(self.changed, 2)

    def test_command_is_not_modified(self):
        self.assertFalse(self.history.is_modified())

    def test_redo_done(self):
        self.history.redo()
        self.assertTrue(self.cmd.done)

    def test_redo_can_undo(self):
        self.history.redo()
        self.assertTrue(self.history.can_undo())

    def test_redo_cannot_redo(self):
        self.history.redo()
        self.assertFalse(self.history.can_redo())

    def test_redo_changed(self):
        self.history.redo()
        self.assertEqual(self.changed, 3)

    def test_redo_is_modified(self):
        self.history.redo()
        self.assertTrue(self.history.is_modified())


class HistorySaveTestCase(HistoryBaseTestCase):
    def setUp(self):
        super().setUp()
        self.cmd1 = DummyCommand()
        self.cmd2 = DummyCommand()
        self.history.run(self.cmd1)
        self.history.save_point()
        self.history.run(self.cmd2)

    def test_is_modified(self):
        self.assertTrue(self.history.is_modified())

    def test_undo_is_not_modified(self):
        self.history.undo()
        self.assertFalse(self.history.is_modified())

    def test_undo_twice_is_modified(self):
        self.history.undo()
        self.history.undo()
        self.assertTrue(self.history.is_modified())


class HistoryResetNewTestCase(HistoryBaseTestCase):
    def setUp(self):
        super().setUp()
        self.history.run(DummyCommand())
        self.history.run(DummyCommand())
        self.history.undo()
        self.changed = 0
        self.history.reset()

    def test_changed(self):
        self.assertEqual(self.changed, 1)

    def test_is_not_modified(self):
        self.assertFalse(self.history.is_modified())

    def test_cannot_undo(self):
        self.assertFalse(self.history.can_undo())

    def test_cannot_redo(self):
        self.assertFalse(self.history.can_redo())


class HistoryResetNotNewTestCase(HistoryBaseTestCase):
    def setUp(self):
        super().setUp()
        self.history.run(DummyCommand())
        self.history.run(DummyCommand())
        self.history.undo()
        self.changed = 0
        self.history.reset(is_new=False)

    def test_changed(self):
        self.assertEqual(self.changed, 1)

    def test_is_modified(self):
        self.assertTrue(self.history.is_modified())

    def test_cannot_undo(self):
        self.assertFalse(self.history.can_undo())

    def test_cannot_redo(self):
        self.assertFalse(self.history.can_redo())


if __name__ == '__main__':
    unittest.main()
