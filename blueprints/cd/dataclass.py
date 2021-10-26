from flask import flash
from datetime import date
from dataclasses import dataclass
from ... packages import Voucher

@dataclass
class CD(Voucher):
    cd_num: str = ""
    record_date: str = str(date.today())
    vendor_id: int = 0
    check_number: str = ""
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
                    tbl_cd.cd_num,
    				tbl_cd.record_date,
    				tbl_vendor.name as vendor_name,
                    tbl_cd.check_number,
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
                    tbl_cd.check_number,
    				tbl_vendor.name as vendor_name,
    				tbl_cd.description
    			FROM tbl_cd
    			INNER JOIN tbl_vendor ON tbl_vendor.id = tbl_cd.vendor_id
    		"""
    		return self.db.execute(sql).fetchall()


    def range(self, date_from, date_to):
        if True:
            sql = f"""
                SELECT 
                    tbl_cd.id,
                    tbl_cd.cd_num,
                    tbl_cd.record_date,
                    tbl_vendor.name as vendor_name,
                    tbl_cd.check_number,
                    tbl_cd.description
                FROM tbl_cd
                INNER JOIN tbl_vendor ON tbl_vendor.id = tbl_cd.vendor_id
                WHERE tbl_cd.record_date>=? AND tbl_cd.record_date<=?
            """
            return self.db.execute(sql, (date_from, date_to)).fetchall()


    def is_validated(self):
        if self.id:
            if self.db.execute('SELECT COUNT(*) FROM tbl_cd WHERE cd_num=? AND id!=?;', (self.cd_num, self.id)).fetchone()[0]:
                flash("CD Number is already in use.")
                return False
            if self.db.execute('SELECT COUNT(*) FROM tbl_cd WHERE check_number=? AND id!=?;', (self.check_number, self.id)).fetchone()[0]:
                flash("Check Number is already in use.")
                return False
        else:
            if self.db.execute('SELECT COUNT(*) FROM tbl_cd WHERE cd_num=?;', (self.cd_num, )).fetchone()[0]:
                flash("CD Number is already in use.")
                return False
            if self.db.execute('SELECT COUNT(*) FROM tbl_cd WHERE check_number=?;', (self.check_number, )).fetchone()[0]:
                flash("Check Number is already in use.")
                return False
                
        return True


	# def all(self, **filter):
	# 	if filter:
	# 		clause = [f'{key}=?' for key in filter]
	# 		return self.db.execute(f'SELECT * FROM {self.table_name} WHERE {", ".join(clause)};', tuple(filter.values())).fetchall()
	# 	else:
	# 		return self.db.execute(f'SELECT * FROM {self.table_name};').fetchall()

