from dataclasses import dataclass
from sqlite_data_model import sqliteDataModel

@dataclass
class Vendor(sqliteDataModel):
	name: str = None
	tin: str = None
	address: str = None


	@property
	def init_db(self):
		self.delete_table
		self.create_table


	def is_related(self):
		for voucher in ('cd',):	
			if self.db.execute('SELECT COUNT(*) FROM tbl_cd WHERE vendor_id = ?;', (self.id, )).fetchone()[0]:
				return True
		return False
