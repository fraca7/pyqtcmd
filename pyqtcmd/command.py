#!/usr/bin/env python3

"""
Base and generic commands
"""

class Command:
    """
    Command objects encapsulate a change to the document/project/etc's
    state. You should provide an __str__ method for logging purposes.
    """

    def do(self):
        """Override this to implement the change"""
        raise NotImplementedError # pragma: no cover

    def undo(self):
        """Override this to implement the change undo"""
        raise NotImplementedError # pragma: no cover

    def redo(self):
        """Override this to implement the change redo (calls do() by default)"""
        self.do()

    def label(self):
        """Provide a description of the command, to be used in menu items and tooltips"""


class UpdateStateCommand(Command):
    """
    A Command that updates an object's state through its
    __getstate__/__setstate__ special methods
    """

    def __init__(self, target, **state):
        super().__init__()
        self.__target = target
        self.__old = dict(target.__getstate__())
        self.__new = dict(self.__old)
        self.__new.update(state)

    def do(self):
        self.__target.__setstate__(self.__new)

    def undo(self):
        self.__target.__setstate__(self.__old)

    def __str__(self):
        return 'Update state of %s from %s to %s' % (self.__target, self.__old, self.__new)


class CompositeCommand(Command):
    """
    A Command that groups several other commands together.
    """

    def __init__(self, label=None):
        super().__init__()
        self.__commands = []
        self.__label = label

    def add_command(self, cmd):
        """
        Adds a new command to the chain. Commands will be run in
        order, and undone in reverse order.
        """
        self.__commands.append(cmd)

    def do(self):
        for cmd in self.__commands:
            cmd.do()

    def undo(self):
        for cmd in reversed(self.__commands):
            cmd.undo()

    def label(self):
        return self.__label

    def __str__(self):
        return self.__label or 'Composition of: %s' % ', '.join(map(str, self.__commands))
