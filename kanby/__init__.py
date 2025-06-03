"""
Kanby - A beautiful terminal-based Kanban board

A simple, elegant Kanban board that runs entirely in your terminal.
Organize your tasks with multiple projects, priorities, and columns.
"""

__version__ = "1.0.21"
__author__ = "Vlad Arbatov"
__description__ = "A beautiful terminal-based Kanban board"

from .main import cli_main

__all__ = ['cli_main', '__version__', '__author__', '__description__']
