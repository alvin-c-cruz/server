from flask import flash
from datetime import date
from dataclasses import dataclass
from ... packages import Voucher

@dataclass
class CD(Voucher):
    cd_num: str = ""
    record_date: str = str(date.today())
    vendor_id: int = 0
    description: str = ""

    @property
    def vendor_name(self):
    	return self.db.execute('SELECT name FROM tbl_vendor WHERE id=?', (self.vendor_id, )).fetchone()[0]	
		

    def all(self, **filter):
    	if filter:
    		clause = [f'{key}=?' for key in filter]
    		sql = f"""
    			SELECT 
    				tbl_cd.id,
    				tbl_cd.record_date,
    				tbl_vendor.name as vendor_name,
    				tbl_cd.description
    			FROM tbl_cd
    			INNER JOIN tbl_vendor ON tbl_vendor.id = tbl_cd.vendor_id
    			WHERE {", ".join(clause)}
    		"""
    		return self.db.execute(sql, tuple(filter.values)).fetchall()
    	else:
    		sql = f"""
    			SELECT 
    				tbl_cd.id,
    				tbl_cd.cd_num,
    				tbl_cd.record_date,
    				tbl_vendor.name as vendor_name,
    				tbl_cd.description
    			FROM tbl_cd
    			INNER JOIN tbl_vendor ON tbl_vendor.id = tbl_cd.vendor_id
    		"""
    		return self.db.execute(sql).fetchall()


    def is_validated(self):
        if self.id:
            if self.db.execute('SELECT COUNT(*) FROM tbl_cd WHERE cd_num=? AND id!=?;', (self.cd_num, self.id)).fetchone()[0]:
                flash("CD Number is already in use.")
                return False
        else:
            if self.db.execute('SELECT COUNT(*) FROM tbl_cd WHERE cd_num=?;', (self.cd_num, )).fetchone()[0]:
                flash("CD Number is already in use.")
                return False


        return True


	# def all(self, **filter):
	# 	if filter:
	# 		clause = [f'{key}=?' for key in filter]
	# 		return self.db.execute(f'SELECT * FROM {self.table_name} WHERE {", ".join(clause)};', tuple(filter.values())).fetchall()
	# 	else:
	# 		return self.db.execute(f'SELECT * FROM {self.table_name};').fetchall()

