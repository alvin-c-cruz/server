from datetime import date
from dataclasses import dataclass
from ... packages import Voucher

@dataclass
class CD(Voucher):
    cd_num: str = None
    record_date: date = None
    vendor_id: int = None
    description: str = None
