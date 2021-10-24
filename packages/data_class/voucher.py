from dataclasses import dataclass, field
from datetime import date
from flask import session


@dataclass
class Voucher:
	db: any = field(repr=False)
	id: int = None
	user_id: int = None
	entry: list = field(default_factory=list)
	entry_for_deletion: list = field(default_factory=list)

	table_name: str = field(repr=False,default=None)
	entry_table_name: str = field(repr=False,default=None)


	def __post_init__(self):
		class_name = str(self.__class__)
		loc = class_name.rfind('.') + 1
		length = len(class_name) - 2
		self.class_name = class_name[loc: length].lower()


		if not self.table_name: self.table_name = 'tbl_' + self.class_name 
		if not self.entry_table_name: self.entry_table_name = 'tbl_' + self.class_name + '_entry'


	@dataclass
	class Entry:
		id: int = None
		i: int = 0 # Not to be saved in database
		account_id: int = 0
		debit: float = 0.00
		credit: float = 0.00


	@property
	def init_db(self):
		self.delete_table
		self.create_table
		return f"{self.table_name} and {self.entry_table_name} has been initialized."


	@property
	def create_table(self):
		data_fields = self.fields()
		fields = []
		for field in data_fields:
			name = field.get('name')
			datatype = field.get('datatype')

			fields.append(f'{name} {datatype}')

		commands = [
			f'CREATE TABLE {self.table_name} ({", ".join(fields)});',
			f'CREATE TABLE {self.entry_table_name} (id INTEGER PRIMARY KEY, {self.class_name}_id INTEGER, account_id INTEGER, debit FLOAT, credit FLOAT);'
			]

		for sql in commands: self.db.execute(sql)

		return f"{self.table_name} and {self.entry_table_name} has been created."


	@property
	def delete_table(self):
		commands = [
			f'DROP TABLE IF EXISTS {self.table_name};',
			f'DROP TABLE IF EXISTS {self.entry_table_name};',
			]
		for sql in commands: 
			self.db.execute(sql)

		return f"{self.table_name} and {self.entry_table_name} has been deleted."
	


	def fields(self):
		_list = []
		def d_type(name, field_type):
			if field_type == int: return 'INTEGER'
			if field_type == float: return 'FLOAT'
			if field_type == str: return 'TEXT'
			if field_type == bool: return 'BOOLEAN'
			if field_type == date: return 'TIMESTAMP'


		data_fields = self.__dataclass_fields__

		for key in data_fields:
			if key[0] != '_': 
				field = data_fields[key]

				name = field.name

				if name in ('db', 'entry', 'entry_for_deletion', 'table_name','entry_table_name'): continue
				_dict = {'name': name}
				if name == 'id':
					_dict["datatype"] = 'INTEGER PRIMARY KEY'
				else:
					_dict["datatype"] = d_type(name, field.type)

				_list.append(_dict)

		return _list


	def add_entry(self, **kwargs):
		id = kwargs.get('id')
		account_id = kwargs.get('account_id')
		debit = kwargs.get('debit')
		credit = kwargs.get('credit')

		if not account_id: account_id = 0
		if not debit: debit = 0.0
		if not credit: credit = 0.0

		if id:
			self.entry.append(self.Entry(id=id, account_id=account_id, debit=debit, credit=credit))
		else:
			self.entry.append(self.Entry(account_id=account_id, debit=debit, credit=credit))

		for i in range(0, len(self.entry)):
			self.entry[i].i = i + 1

		return True


	def delete_entry(self, index):
		index -= 1
		try:
			entry_id = 	self.entry[index].id

			if entry_id:
				self.entry_for_deletion.append(entry_id)

			self.entry.pop(index)

			return True
		except:
			return False


	def update_entry(self, index, **kwargs):
		index -= 1

		account_id = kwargs.get('account_id')
		debit = kwargs.get('debit')
		credit = kwargs.get('credit')

		if not account_id: return False

		if not debit: debit = 0.0
		if not credit: credit = 0.0

		self.entry[index].account_id = account_id
		self.entry[index].debit = debit
		self.entry[index].credit = credit

		return True
		

	def delete(self):
		commands = [
			f'DELETE FROM {self.table_name} WHERE id={self.id};',
			f'DELETE FROM {self.entry_table_name} WHERE {self.class_name}_id={self.id};'
		]

		for sql in commands: self.db.execute(sql)
		self.db.commit()


	def save(self):
		self.user_id = session.get('user_id')
		if self.id:
			fields = [f'{field["name"]}=?' for field in self.fields()]
			values = [getattr(self, field['name']) for field in self.fields()]

			self.db.execute(f"UPDATE {self.table_name} set {', '.join(fields)} WHERE id={self.id};", values)

			for entry_id in self.entry_for_deletion: self.db.execute(f'DELETE FROM {self.entry_table_name} WHERE id={entry_id};')
			for row in self.entry:
				if row.id:
					self.db.execute(f'UPDATE {self.entry_table_name} set account_id=?, debit=?, credit=? WHERE id={row.id};', (row.account_id, row.debit, row.credit))
				else:
					sql = f'INSERT INTO {self.entry_table_name} ({self.class_name}_id, account_id, debit, credit) VALUES (?, ?, ?, ?);'
					self.db.execute(sql, (self.id, row.account_id, row.debit, row.credit))
					row.id = self.db.execute("SELECT last_insert_rowid();").fetchone()[0]
		else:
			fields = [field['name'] for field in self.fields() if field['name'] != 'id']
			field_values = ["?" for field in self.fields() if field['name'] != 'id']
			values = []
			for field in self.fields():
				if field['name'] == 'id': continue
				values.append(getattr(self, field['name']))	

			sql = f"INSERT INTO {self.table_name} ({', '.join(fields)}) VALUES ({', '.join(field_values)});"
			self.db.execute(sql, values)
			parent_id = self.db.execute("SELECT last_insert_rowid();").fetchone()[0]
			self.id = parent_id

			for row in self.entry:
				self.db.execute(f'INSERT INTO {self.entry_table_name} ({self.class_name}_id, account_id, debit, credit) VALUES (?, ?, ?, ?);', (parent_id, row.account_id, row.debit, row.credit))
				row.id = self.db.execute("SELECT last_insert_rowid();").fetchone()[0]
		self.db.commit()


	def get(self, parent_id):
		parent = self.db.execute(f'SELECT * FROM {self.table_name} WHERE id={parent_id};').fetchone()
		self.id = parent['id']
		
		for field in self.fields():
			if field['name'] != 'id':
				setattr(self, field['name'], parent[field['name']])

		child = self.db.execute(f'SELECT * FROM {self.entry_table_name} WHERE {self.class_name}_id={parent_id};').fetchall()
		for row in child:
			self.add_entry(
				id=row['id'],
				account_id=row['account_id'],
				debit=row['debit'],
				credit=row['credit']
				)
	

	def all(self, **filter):
		if filter:
			clause = [f'{key}=?' for key in filter]
			return self.db.execute(f'SELECT * FROM {self.table_name} WHERE {", ".join(clause)};', tuple(filter.values())).fetchall()
		else:
			return self.db.execute(f'SELECT * FROM {self.table_name};').fetchall()



