from dataclasses import dataclass
from ... packages import SimpleEntry

@dataclass
class User(SimpleEntry):
    username: str = None
    email: str = None
    password: str = None


