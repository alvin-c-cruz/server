from dataclasses import dataclass
from ... packages import SimpleEntry

@dataclass
class Account(SimpleEntry):
    account_number: str = None
    name: str = None


    def is_related(self):
    	for voucher in ('cd',):
    		if self.db.execute('SELECT COUNT(*) FROM tbl_cd_entry WHERE account_id = ?;', (self.id, )).fetchone()[0]:
    			return True
    	return False
