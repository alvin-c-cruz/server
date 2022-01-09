from dataclasses import dataclass
from sqlite_data_model import sqliteDataModel

@dataclass
class Account(sqliteDataModel):
    account_number: str = None
    name: str = None

    @property
    def init_db(self):
        self.delete_table
        self.create_table
        

    def is_related(self):
    	for voucher in ('cd', 'ap', 'x_cd'):
    		if self.db.execute(f'SELECT COUNT(*) FROM tbl_{voucher}_entry WHERE account_id = ?;', (self.id, )).fetchone()[0]:
    			return True
    	return False
