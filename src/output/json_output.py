import json
from typing import Any, Dict, List, Optional
from .base_output import BaseOutput

class JSONOutput(BaseOutput):
    """JSON output formatter"""
    
    def __init__(self):
        super().__init__()
        self.format_config = {
            "indent": 2,
            "ensure_ascii": False,
            "include_metadata": True
        }
        self._buffer: List[Dict[str, Any]] = []
        
    def format(self, content: Any) -> str:
        """Format content as JSON"""
        if isinstance(content, str):
            data = {"text": content}
        elif isinstance(content, dict):
            data = content
        else:
            data = {"content": str(content)}
            
        if self.format_config["include_metadata"]:
            data["metadata"] = {
                "timestamp": "TIMESTAMP",  # Replace with actual timestamp
                "format_version": "1.0"
            }
            
        return json.dumps(
            data,
            indent=self.format_config["indent"],
            ensure_ascii=self.format_config["ensure_ascii"]
        )
    
    def configure(self, **kwargs) -> None:
        """Configure JSON formatting settings"""
        self.format_config.update(kwargs)
    
    def clear(self) -> None:
        """Clear JSON buffer"""
        self._buffer = []
        
    def append(self, content: Any) -> None:
        """Append content to buffer"""
        if isinstance(content, str):
            self._buffer.append({"text": content})
        elif isinstance(content, dict):
            self._buffer.append(content)
        else:
            self._buffer.append({"content": str(content)})
    
    def get_formatted_json(self) -> str:
        """Get all formatted content as JSON array"""
        return json.dumps(
            self._buffer,
            indent=self.format_config["indent"],
            ensure_ascii=self.format_config["ensure_ascii"]
        ) 