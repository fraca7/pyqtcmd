#!/usr/bin/env python3

import unittest

from pyqtcmd import History, Command, UpdateStateCommand, CompositeCommand


class TestObject:
    def __init__(self):
        self.a = 42
        self.b = 'spam'

    def __getstate__(self):
        return dict(a=self.a, b=self.b)

    def __setstate__(self, state):
        self.a, self.b = state['a'], state['b']


class CommandTestCase(unittest.TestCase):
    def test_default_redo(self):
        class CustomCommand(Command):
            def __init__(self):
                self.ok = False
            def do(self):
                self.ok = True

        cmd = CustomCommand()
        cmd.redo()
        self.assertTrue(cmd.ok)


class UpdateStateCommandTestCase(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.history = History()
        self.obj = TestObject()
        self.cmd = UpdateStateCommand(self.obj, a=13)
        self.history.run(self.cmd)

    def test_state_updated(self):
        self.assertEqual(self.obj.a, 13)
        self.assertEqual(self.obj.b, 'spam')

    def test_undo(self):
        self.history.undo()
        self.assertEqual(self.obj.a, 42)
        self.assertEqual(self.obj.b, 'spam')

    def test_redo(self):
        self.history.undo()
        self.history.redo()
        self.assertEqual(self.obj.a, 13)
        self.assertEqual(self.obj.b, 'spam')


class DummyCommand(Command):
    def __init__(self, owner):
        super().__init__()
        self._owner = owner

    def do(self):
        self._owner.onDone(self)

    def undo(self):
        self._owner.onUndone(self)


class CompositeCommandTestCase(unittest.TestCase):
    def setUp(self):
        self.history = History()
        self.cmd1 = DummyCommand(self)
        self.cmd2 = DummyCommand(self)
        self.cmd = CompositeCommand()
        self.cmd.add_command(self.cmd1)
        self.cmd.add_command(self.cmd2)
        self.done = []
        self.undone = []

    def onDone(self, cmd):
        self.done.append(cmd)

    def onUndone(self, cmd):
        self.undone.append(cmd)

    def test_do(self):
        self.history.run(self.cmd)
        self.assertEqual(self.done, [self.cmd1, self.cmd2])

    def test_undo(self):
        self.history.run(self.cmd)
        self.history.undo()
        self.assertEqual(self.undone, [self.cmd2, self.cmd1])


if __name__ == '__main__':
    unittest.main()
