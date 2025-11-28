"""
Background worker thread for non-blocking operations
"""
from PyQt6.QtCore import QThread
from typing import Callable, Any


class WorkerThread(QThread):
    """
    Generic worker thread for background tasks
    Prevents UI freezing during long operations
    """

    def __init__(self, target: Callable, *args, **kwargs):
        """
        Initialize worker thread

        Args:
            target: Function to execute in background
            *args, **kwargs: Arguments to pass to target function
        """
        super().__init__()
        self.target = target
        self.args = args
        self.kwargs = kwargs
        self.result = None
        self.error = None

    def run(self):
        """Execute the target function"""
        try:
            self.result = self.target(*self.args, **self.kwargs)
        except Exception as e:
            self.error = e

