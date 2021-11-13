from dataclasses import dataclass
from sqlite_data_model import sqliteDataModel

@dataclass
class Customer(sqliteDataModel):
	name: str = None
	tin: str = None
	address: str = None

	def is_related(self):
		# for voucher in ('sj',):	
		# 	if self.db.execute('SELECT COUNT(*) FROM tbl_sj WHERE customer_id = ?;', (self.id, )).fetchone()[0]:
		# 		return True
		return False
