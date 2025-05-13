from abc import ABC, abstractmethod
from typing import Any, Optional

class BaseOutput(ABC):
    """Base class for output formatting"""
    
    def __init__(self):
        self.format_config = {}
    
    @abstractmethod
    def format(self, content: Any) -> str:
        """Format the content according to specific rules"""
        pass
    
    @abstractmethod
    def configure(self, **kwargs) -> None:
        """Configure output formatting settings"""
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """Clear any stored formatting state"""
        pass 