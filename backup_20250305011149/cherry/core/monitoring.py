"""
Monitoring utilities for tracking system health and errors.
"""
import logging
import time
import threading
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)


@dataclass
class ErrorEvent:
    """Represents a single error occurrence."""
    error_type: str
    message: str
    timestamp: datetime = field(default_factory=datetime.now)
    context: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "error_type": self.error_type,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "context": self.context
        }


class ErrorMonitor:
    """
    Monitors and tracks errors in the system.
    """
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(ErrorMonitor, cls).__new__(cls)
                cls._instance._initialize()
            return cls._instance
    
    def _initialize(self) -> None:
        """Initialize the error monitor."""
        self.recent_errors: List[ErrorEvent] = []
        self.error_counts: Dict[str, int] = {}
        self.error_thresholds: Dict[str, int] = {}
        self.alerts: Set[Tuple[str, str]] = set()  # Set of (error_type, message) tuples
        self.max_recent_errors = 100
        self._lock = threading.Lock()
    
    def record_error(self, error_type: str, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """
        Record an error occurrence.
        
        Args:
            error_type: Type of the error (e.g., "AgentTimeoutError")
            message: Error message
            context: Additional context information
        """
        context = context or {}
        event = ErrorEvent(error_type, message, datetime.now(), context)
        
        with self._lock:
            # Add to recent errors, maintaining maximum size
            self.recent_errors.append(event)
            if len(self.recent_errors) > self.max_recent_errors:
                self.recent_errors.pop(0)
            
            # Update error counts
            self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
            
            # Check thresholds and trigger alerts if needed
            self._check_thresholds(error_type)
    
    def set_threshold(self, error_type: str, max_count: int) -> None:
        """
        Set an alert threshold for a specific error type.
        
        Args:
            error_type: The error type to monitor
            max_count: Maximum number of occurrences before alerting
        """
        with self._lock:
            self.error_thresholds[error_type] = max_count
    
    def _check_thresholds(self, error_type: str) -> None:
        """Check if an error threshold has been exceeded and trigger an alert if needed."""
        if error_type not in self.error_thresholds:
            return
            
        count = self.error_counts.get(error_type, 0)
        threshold = self.error_thresholds[error_type]
        
        if count >= threshold:
            alert_key = (error_type, f"Threshold of {threshold} exceeded")
            if alert_key not in self.alerts:
                self.alerts.add(alert_key)
                logger.critical(
                    f"ALERT: Error threshold exceeded for {error_type}. "
                    f"Count: {count}, Threshold: {threshold}"
                )
                # Here you could add additional alert mechanisms like:
                # - Send email
                # - Send notification to Slack/Teams
                # - Trigger pager duty, etc.
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get a summary of recent errors."""
        with self._lock:
            return {
                "total_errors": sum(self.error_counts.values()),
                "error_counts": self.error_counts.copy(),
                "recent_errors": [e.to_dict() for e in self.recent_errors[-10:]],
                "alerts": list(self.alerts)
            }
    
    def clear_old_errors(self, max_age_hours: int = 24) -> None:
        """Clear errors older than the specified age."""
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        
        with self._lock:
            self.recent_errors = [e for e in self.recent_errors if e.timestamp >= cutoff_time]
    
    def export_errors(self, filepath: str) -> None:
        """Export error logs to a JSON file."""
        with self._lock:
            data = {
                "export_time": datetime.now().isoformat(),
                "error_counts": self.error_counts,
                "errors": [e.to_dict() for e in self.recent_errors]
            }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
