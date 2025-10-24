from sqlmodel import Field, SQLModel, Relationship, select

class test(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)