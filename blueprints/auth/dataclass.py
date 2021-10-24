from dataclasses import dataclass
from ... packages import SimpleEntry

@dataclass
class User(SimpleEntry):
    username: str = None
    email: str = None
    password: str = None
    level: int = 5  #  Levels: 1=admin; 2=audit; 3=accountant; 4=bookkeeper; 5=viewer


