from typing import Any, Optional
from .base_output import BaseOutput

class TextOutput(BaseOutput):
    """Text output formatter"""
    
    def __init__(self):
        super().__init__()
        self.format_config = {
            "capitalize_sentences": True,
            "add_punctuation": True,
            "remove_extra_spaces": True
        }
        self._buffer = []
    
    def format(self, content: Any) -> str:
        """Format text content"""
        text = str(content)
        
        if self.format_config["remove_extra_spaces"]:
            text = " ".join(text.split())
            
        if self.format_config["capitalize_sentences"]:
            sentences = text.split(". ")
            sentences = [s.capitalize() for s in sentences]
            text = ". ".join(sentences)
            
        if self.format_config["add_punctuation"]:
            if not text.endswith((".", "!", "?")):
                text += "."
                
        return text
    
    def configure(self, **kwargs) -> None:
        """Configure text formatting settings"""
        self.format_config.update(kwargs)
    
    def clear(self) -> None:
        """Clear text buffer"""
        self._buffer = []
        
    def append(self, text: str) -> None:
        """Append text to buffer"""
        self._buffer.append(text)
        
    def get_formatted_text(self) -> str:
        """Get all formatted text from buffer"""
        return " ".join(self.format(text) for text in self._buffer) 