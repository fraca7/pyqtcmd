#!/usr/bin/env python3

"""
Base history mechanism
"""

import collections
import contextlib
import logging

try:
    from PyQt5 import QtCore
except ModuleNotFoundError: # pragma: no cover
    from PyQt6 import QtCore


class HistoryVersion(collections.namedtuple('HistoryVersion', ['major', 'minor'])):
    """
    History version. Internal use only.
    """
    def __str__(self):
        return '.'.join(map(str, self))


class ConsistencyError(Exception):
    """
    Thrown when something bad happens (trying to undo with an empty
    past list for instance).
    """

class History(QtCore.QObject):
    """
    Maintains lists of past and future commands as they are done and
    undone. The `changed` signal is emitted whenever the history state
    changes. This class also maintains a pointer to a 'saved' state
    and can tell if its current state is the saved one or not (see
    is_modified()).
    """

    changed = QtCore.pyqtSignal()

    logger = logging.getLogger('pyqtcmd.History')

    def __init__(self):
        self.__past = []
        self.__future = []
        self.__version = HistoryVersion(0, 0)
        self.__saved_version = self.__version
        super().__init__()

    @contextlib.contextmanager
    def freeze(self): # pylint: disable=R0201
        """
        This context manager will wrap calls to
        Command.(undo|redo|do). You can override it to provide some
        sort of batch updating/signalling in your own project.
        """
        yield

    def check(self):
        """
        This just emits the changed signal; use it when you think
        UICommand states should be updated, when add_check_signal is
        not enough.
        """
        self.changed.emit()

    def reset(self, is_new=True):
        """
        Resets the history state. This is typically called when a new
        document has been loaded or created. If `is_new` is False, the
        saved state is not reset, so is_modified() will still return
        True. This is intended for session management, when loading a
        document that hasn't actually been saved yet.
        """
        self.__version = self.__version._replace(major=self.__version.major + 1)
        self.__past = []
        self.__future = []
        if is_new:
            self.__saved_version = self.__version
        self.logger.debug('Reset to version %s (saved %s)', self.__version, self.__saved_version)
        self.changed.emit()

    def is_modified(self):
        """
        Returns True if the history state is different from what it
        was when save_point() was last called (or when constructed, or
        reset with is_new=False).
        """
        return self.__version != self.__saved_version

    def save_point(self):
        """
        Sets the 'saved' state as the current one. Call this after
        saving a document to disk for instance.
        """
        self.__saved_version = self.__version
        self.logger.debug('Saved (version is now %s/%s)', self.__version, self.__saved_version)
        self.changed.emit()

    def run(self, command):
        """
        Run a command and put it in the past. In order to keep things
        consistent, the future list is deleted.
        """
        with self.freeze():
            self.logger.debug('Will run command "%s"', command)
            command.do()
            self.logger.debug('Ran command "%s"', command)
        self.__past.append(command)
        self.__future = []
        self.__version = self.__version._replace(minor=self.__version.minor + 1)
        self.logger.debug('Version is now %s/%s', self.__version, self.__saved_version)
        self.changed.emit()

    def can_undo(self):
        """Returns True if there is at least one past command"""
        return bool(self.__past)

    def undo_label(self):
        """The text for the current undo command, or None"""
        if self.__past:
            return self.__past[-1].label()
        return ''

    def can_redo(self):
        """Returns True if there is at least one future command"""
        return bool(self.__future)

    def redo_label(self):
        """The text for the current redo command, or None"""
        if self.__future:
            return self.__future[-1].label()
        return ''

    def undo(self):
        """
        Undo the latest command that was run. Throws ConsistencyError
        if there are no commands to undo.
        """
        if not self.__past:
            raise ConsistencyError('No command to undo')
        cmd = self.__past.pop()
        with self.freeze():
            self.logger.debug('Will undo "%s"', cmd)
            cmd.undo()
            self.logger.debug('Undid "%s"', cmd)
        self.__future.append(cmd)
        self.__version = self.__version._replace(minor=self.__version.minor - 1)
        self.logger.debug('Version is now %s/%s', self.__version, self.__saved_version)
        self.changed.emit()

    def redo(self):
        """
        Redo the latest command that was undone. Throws
        ConsistencyError if there are no command to redo.
        """
        if not self.__future:
            raise ConsistencyError('No command to redo')
        cmd = self.__future.pop()
        with self.freeze():
            self.logger.debug('Will redo "%s"', cmd)
            cmd.redo()
            self.logger.debug('Redid "%s"', cmd)
        self.__past.append(cmd)
        self.__version = self.__version._replace(minor=self.__version.minor + 1)
        self.logger.debug('Version is now %s/%s', self.__version, self.__saved_version)
        self.changed.emit()

    def past(self):
        """
        Return a copy of past Command objects. This may be useful in
        situation where, for instance, a modal dialog has a 'local'
        history, and you want to encapsulate everything that has been
        done in this dialog in a single CompositeCommand when the
        dialog is closed, and add it to the 'main' history.
        """
        return self.__past[:]
