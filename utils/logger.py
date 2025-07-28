"""Logging utility with Datadog integration."""

import logging
import sys
from typing import Any, Dict
from rich.logging import RichHandler
from rich.console import Console

from config.settings import settings

# Create rich console for better terminal output
console = Console()

class StructuredLogger:
    """Logger with structured logging and Datadog integration."""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Remove existing handlers
        self.logger.handlers.clear()
        
        # Add rich handler for terminal output
        rich_handler = RichHandler(
            console=console,
            show_time=True,
            show_path=False,
            markup=True
        )
        rich_handler.setFormatter(
            logging.Formatter("%(message)s", datefmt="[%X]")
        )
        self.logger.addHandler(rich_handler)
        
        # Initialize Datadog tracing if configured
        if settings.dd_api_key:
            try:
                from ddtrace import tracer
                from ddtrace.contrib.logging import patch
                patch()
                self.tracer = tracer
            except ImportError:
                console.print("[yellow]Warning: Datadog not configured properly[/yellow]")
                self.tracer = None
        else:
            self.tracer = None
    
    def info(self, message: str, **kwargs: Any) -> None:
        """Log info message with optional structured data."""
        extra_data = self._format_extra(kwargs)
        self.logger.info(f"{message} {extra_data}")
    
    def warning(self, message: str, **kwargs: Any) -> None:
        """Log warning message with optional structured data."""
        extra_data = self._format_extra(kwargs)
        self.logger.warning(f"[yellow]{message}[/yellow] {extra_data}")
    
    def error(self, message: str, **kwargs: Any) -> None:
        """Log error message with optional structured data."""
        extra_data = self._format_extra(kwargs)
        self.logger.error(f"[red]{message}[/red] {extra_data}")
    
    def success(self, message: str, **kwargs: Any) -> None:
        """Log success message with optional structured data."""
        extra_data = self._format_extra(kwargs)
        self.logger.info(f"[green]✓ {message}[/green] {extra_data}")
    
    def _format_extra(self, data: Dict[str, Any]) -> str:
        """Format extra data for logging."""
        if not data:
            return ""
        
        formatted_items = []
        for key, value in data.items():
            formatted_items.append(f"[dim]{key}={value}[/dim]")
        
        return f"({', '.join(formatted_items)})"


def get_logger(name: str) -> StructuredLogger:
    """Get a structured logger instance."""
    return StructuredLogger(name) 