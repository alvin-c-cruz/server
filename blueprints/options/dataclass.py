from sqlite_data_model import sqliteDataModel
from dataclasses import dataclass

@dataclass
class Options(sqliteDataModel):
    keyword: str = ""
    value: str = ""