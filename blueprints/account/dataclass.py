from dataclasses import dataclass
from ... packages import SimpleEntry

@dataclass
class Account(SimpleEntry):
    account_number: str = None
    account_title: str = None
