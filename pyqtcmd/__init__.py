#!/usr/bin/env python3

"""
PyQt5/PyQt6 implementation of the Command pattern, with niceties
"""

from .history import History, ConsistencyError
from .command import Command, UpdateStateCommand, CompositeCommand
from .uicommand import UICommand, UndoUICommandMixin, RedoUICommandMixin, \
     NeedsSelectionUICommandMixin
