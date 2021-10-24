from dataclasses import dataclass, field
from datetime import date


@dataclass
class SimpleEntry:
	db: any = field(repr=False)
	id: int = None

	table_name: str = field(repr=False,default=None)


	def __post_init__(self):
		class_name = str(self.__class__)
		loc = class_name.rfind('.') + 1
		length = len(class_name) - 2
		self.class_name = class_name[loc: length].lower()


		if not self.table_name: self.table_name = 'tbl_' + self.class_name 


	@property
	def init_db(self):
		self.delete_table
		self.create_table
		return f"{self.table_name} has been initialized."


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
			]

		for sql in commands: self.db.execute(sql)

		return f"{self.table_name} has been created."


	@property
	def delete_table(self):
		commands = [
			f'DROP TABLE IF EXISTS {self.table_name};',
			]
		for sql in commands: self.db.execute(sql)

		return f"{self.table_name} has been deleted."
	

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

				if name in ('db', 'table_name'): continue
				_dict = {'name': name}
				if name == 'id':
					_dict["datatype"] = 'INTEGER PRIMARY KEY'
				else:
					_dict["datatype"] = d_type(name, field.type)

				_list.append(_dict)

		return _list


		

	def delete(self):
		if self.is_related():
			return f"{self.name} has related information and cannot be deleted."
		else:
			commands = [
				f'DELETE FROM {self.table_name} WHERE id={self.id};',
			]

			for sql in commands: self.db.execute(sql)
			self.db.commit()


	def save(self):
		if self.id:
			fields = [f'{field["name"]}=?' for field in self.fields()]
			values = [getattr(self, field['name']) for field in self.fields()]

			self.db.execute(f"UPDATE {self.table_name} set {', '.join(fields)} WHERE id={self.id};", values)

		else:
			fields = [field['name'] for field in self.fields() if field['name'] != 'id']
			field_values = ["?" for field in self.fields() if field['name'] != 'id']
			values = []
			for field in self.fields():
				if field['name'] == 'id': continue
				values.append(getattr(self, field['name']))	

			sql = f"INSERT INTO {self.table_name} ({', '.join(fields)}) VALUES ({', '.join(field_values)});"
			self.db.execute(sql, values)
			self.id = self.db.execute("SELECT last_insert_rowid();").fetchone()[0]

		self.db.commit()


	def get(self, parent_id):
		parent = self.db.execute(f'SELECT * FROM {self.table_name} WHERE id={parent_id};').fetchone()
		self.id = parent['id']
		
		for field in self.fields():
			if field['name'] != 'id':
				setattr(self, field['name'], parent[field['name']])


	def find(self, **filter):
		clause = [f'{key}=?' for key in filter]
		record = self.db.execute(f'SELECT * FROM {self.table_name} WHERE {", ".join(clause)};', tuple(filter.values())).fetchone()

		self.id = record['id']

		for field in self.fields():
			if field['name'] != 'id':
				setattr(self, field['name'], record[field['name']])


	def all(self, **filter):
		if filter:
			clause = [f'{key}=?' for key in filter]
			return self.db.execute(f'SELECT * FROM {self.table_name} WHERE {", ".join(clause)};', tuple(filter.values())).fetchall()
		else:
			return self.db.execute(f'SELECT * FROM {self.table_name};').fetchall()


	def is_related(self):
		return False
