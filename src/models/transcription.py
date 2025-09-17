from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Transcription:
    """Modelo para representar una transcripción."""
    id: Optional[str] = None
    name: str = ""
    text: str = ""
    timestamp: datetime = None
    language: str = "es"
    mode: str = "monologo"  # monologo o dialogo
    file_path: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def to_dict(self):
        """Convierte la transcripción a diccionario para MongoDB."""
        return {
            "name": self.name,
            "text": self.text,
            "timestamp": self.timestamp,
            "language": self.language,
            "mode": self.mode,
            "file_path": self.file_path
        }
    
    @classmethod
    def from_dict(cls, data):
        """Crea una transcripción desde un diccionario de MongoDB."""
        return cls(
            id=str(data.get("_id", "")),
            name=data.get("name", ""),
            text=data.get("text", ""),
            timestamp=data.get("timestamp", datetime.now()),
            language=data.get("language", "es"),
            mode=data.get("mode", "monologo"),
            file_path=data.get("file_path")
        )
