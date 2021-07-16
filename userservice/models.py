
from beanie import Document
from pydantic import BaseModel, EmailStr
from pydantic.fields import Field
from beanie import PydanticObjectId
from typing import Optional



class UserIn(BaseModel):
    name: str
    email: EmailStr

    class Config:
        validate_assignment = True


class UserDB(UserIn, Document):
    id: Optional[PydanticObjectId] = Field(None, alias="_id")
    class Collection:
        name = "users"


class User(BaseModel):
    name: str
    id: PydanticObjectId
    email: EmailStr

    @classmethod
    def from_db_user(cls, db_user):
        return cls(
            id=db_user.id,
            name=db_user.name,
            email=db_user.email
        )


class UserEdit(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None

    class Config:
        validate_assignment = True

class ServerHealth(BaseModel):
    name: str