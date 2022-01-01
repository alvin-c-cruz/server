from dataclasses import dataclass
from ... packages import SimpleEntry
from sqlite_data_model import sqliteDataModel

@dataclass
class User(sqliteDataModel):
    username: str = None
    email: str = None
    password: str = None
    level: int = 5  #  Levels: 1=admin; 2=audit; 3=accountant; 4=bookkeeper; 5=viewer

    @property
    def init_db(self):
        self.delete_table
        self.create_table