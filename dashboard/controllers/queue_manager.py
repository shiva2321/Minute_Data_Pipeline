"""
Thread-safe queue manager for symbol processing
"""
from PyQt6.QtCore import QObject
from threading import Lock
from collections import deque
from typing import Dict, List, Optional
from enum import Enum


class SymbolStatus(Enum):
    """Symbol processing status"""
    QUEUED = "queued"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


class QueueManager(QObject):
    """
    Thread-safe queue for managing symbol processing
    """
    
    def __init__(self):
        super().__init__()
        self.queue = deque()
        self.processing = {}  # symbol -> {status, progress, data_points, etc.}
        self.completed = {}   # symbol -> profile dict
        self.failed = {}      # symbol -> error dict
        self.skipped = {}     # symbol -> reason
        self.lock = Lock()
    
    def add_symbols(self, symbols: List[str]):
        """
        Add symbols to queue
        
        Args:
            symbols: List of ticker symbols
        """
        with self.lock:
            for symbol in symbols:
                # Don't add duplicates or already processing/completed symbols
                if (symbol not in self.queue and 
                    symbol not in self.processing and
                    symbol not in self.completed):
                    self.queue.append(symbol)
    
    def get_next_symbol(self) -> Optional[str]:
        """
        Get next symbol from queue
        
        Returns:
            Next symbol to process, or None if queue is empty
        """
        with self.lock:
            if self.queue:
                symbol = self.queue.popleft()
                self.processing[symbol] = {
                    'status': SymbolStatus.PROCESSING.value,
                    'progress': 0,
                    'data_points': 0,
                    'date_range': '-',
                    'api_calls': 0,
                    'duration': 0
                }
                return symbol
            return None
    
    def update_status(
        self,
        symbol: str,
        status: str,
        progress: int = 0,
        **kwargs
    ):
        """
        Update symbol processing status
        
        Args:
            symbol: Ticker symbol
            status: Status string (e.g., 'Fetching', 'Engineering')
            progress: Progress percentage (0-100)
            **kwargs: Additional metadata (data_points, api_calls, etc.)
        """
        with self.lock:
            if symbol in self.processing:
                self.processing[symbol].update({
                    'status': status,
                    'progress': progress,
                    **kwargs
                })
    
    def mark_completed(self, symbol: str, profile: Dict):
        """
        Mark symbol as successfully completed
        
        Args:
            symbol: Ticker symbol
            profile: Completed profile data
        """
        with self.lock:
            if symbol in self.processing:
                del self.processing[symbol]
            self.completed[symbol] = profile
    
    def mark_failed(self, symbol: str, error: str):
        """
        Mark symbol as failed
        
        Args:
            symbol: Ticker symbol
            error: Error message
        """
        with self.lock:
            if symbol in self.processing:
                del self.processing[symbol]
            self.failed[symbol] = {
                'error': error,
                'timestamp': None  # Could add timestamp
            }
    
    def mark_skipped(self, symbol: str, reason: str):
        """
        Mark symbol as skipped
        
        Args:
            symbol: Ticker symbol
            reason: Reason for skipping
        """
        with self.lock:
            if symbol in self.processing:
                del self.processing[symbol]
            self.skipped[symbol] = reason
    
    def remove_symbol(self, symbol: str):
        """
        Remove symbol from all queues
        
        Args:
            symbol: Ticker symbol to remove
        """
        with self.lock:
            # Remove from queue
            if symbol in self.queue:
                self.queue.remove(symbol)
            
            # Remove from other collections
            for collection in [self.processing, self.completed, self.failed, self.skipped]:
                if symbol in collection:
                    del collection[symbol]
    
    def retry_failed(self, symbol: str):
        """
        Retry a failed symbol
        
        Args:
            symbol: Ticker symbol to retry
        """
        with self.lock:
            if symbol in self.failed:
                del self.failed[symbol]
                self.queue.append(symbol)
    
    def clear_all(self):
        """Clear all queues"""
        with self.lock:
            self.queue.clear()
            self.processing.clear()
            self.completed.clear()
            self.failed.clear()
            self.skipped.clear()
    
    def get_stats(self) -> Dict:
        """
        Get queue statistics
        
        Returns:
            Dictionary with counts for each status
        """
        with self.lock:
            return {
                'queued': len(self.queue),
                'processing': len(self.processing),
                'completed': len(self.completed),
                'failed': len(self.failed),
                'skipped': len(self.skipped),
                'total': (len(self.queue) + len(self.processing) + 
                         len(self.completed) + len(self.failed) + len(self.skipped))
            }
    
    def get_all_symbols(self) -> Dict[str, Dict]:
        """
        Get all symbols with their current status
        
        Returns:
            Dictionary mapping symbols to their status info
        """
        with self.lock:
            result = {}
            
            # Queued symbols
            for symbol in self.queue:
                result[symbol] = {
                    'status': SymbolStatus.QUEUED.value,
                    'progress': 0
                }
            
            # Processing symbols
            for symbol, info in self.processing.items():
                result[symbol] = info
            
            # Completed symbols
            for symbol, profile in self.completed.items():
                result[symbol] = {
                    'status': SymbolStatus.SUCCESS.value,
                    'progress': 100,
                    'data_points': profile.get('data_points_count', 0),
                    'date_range': f"{profile.get('data_date_range', {}).get('start', 'N/A')} to {profile.get('data_date_range', {}).get('end', 'N/A')}"
                }
            
            # Failed symbols
            for symbol, error_info in self.failed.items():
                result[symbol] = {
                    'status': SymbolStatus.FAILED.value,
                    'progress': 0,
                    'error': error_info.get('error', 'Unknown error')
                }
            
            # Skipped symbols
            for symbol, reason in self.skipped.items():
                result[symbol] = {
                    'status': SymbolStatus.SKIPPED.value,
                    'progress': 0,
                    'reason': reason
                }
            
            return result

