from dataclasses import dataclass
from ... packages import SimpleEntry

@dataclass
class Vendor(SimpleEntry):
    vendor_name: str = None
    tin: str = None
