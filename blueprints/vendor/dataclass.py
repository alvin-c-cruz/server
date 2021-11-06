from dataclasses import dataclass
from ... packages import SimpleEntry

@dataclass
class Vendor(SimpleEntry):
	name: str = None
	tin: str = None
	address: str = None

	def is_related(self):
		for voucher in ('cd',):	
			if self.db.execute('SELECT COUNT(*) FROM tbl_cd WHERE vendor_id = ?;', (self.id, )).fetchone()[0]:
				return True
		return False
