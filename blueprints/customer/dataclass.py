from dataclasses import dataclass
from sqlite_data_model import sqliteDataModel

@dataclass
class Customer(sqliteDataModel):
	name: str = None
	tin: str = None
	address: str = None


	@property
	def init_db(self):
		self.delete_table
		self.create_table


	def is_related(self):
		# for voucher in ('sj',):	
		# 	if self.db.execute(f'SELECT COUNT(*) FROM tbl_{voucher} WHERE customer_id = ?;', (self.id, )).fetchone()[0]:
		# 		return True
		return False
