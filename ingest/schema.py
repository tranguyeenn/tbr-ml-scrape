from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class UserBook:
    title: str
    author: Optional[str]
    status: str
    dates: Optional[datetime]