from fastapi import APIRouter, HTTPException, Depends
from beanie import PydanticObjectId
from fastapi import Response
from starlette.status import HTTP_204_NO_CONTENT, HTTP_201_CREATED, HTTP_200_OK

from models import User, UserIn, UserDB, UserEdit
from typing import List

users_router = APIRouter()


async def get_db_user(user_id: PydanticObjectId) -> UserDB:
    user = await UserDB.get(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


async def get_user(user_id: PydanticObjectId) -> UserDB:
    db_user = await get_db_user(user_id=user_id)
    return User.from_db_user(db_user)


@users_router.post('/users/', response_model=User, status_code=HTTP_201_CREATED)
async def create_user(user_in: UserIn):
    user = UserDB(**user_in.dict())
    await user.create()
    return User.from_db_user(user)


@users_router.get("/users/{user_id}", response_model=User, status_code=HTTP_200_OK)
async def get_user_by_id(user: User = Depends(get_user)):
    return user


@users_router.get("/users/", response_model=List[User], status_code=HTTP_200_OK)
async def list_users():
    users = await UserDB.find_all().to_list()
    return [User.from_db_user(user) for user in users]


@users_router.put("/users/{user_id}", response_model=User, status_code=HTTP_200_OK)
async def update_user(user_in: UserEdit, user: UserDB = Depends(get_db_user)):
    for field_name, field_value in user_in.dict().items():
        if field_value:
            setattr(user, field_name, field_value)
    await user.save()
    return User(**user.dict())


@users_router.delete("/users/{user_id}", status_code=HTTP_204_NO_CONTENT, response_class=Response)
async def delete_user(user: UserDB = Depends(get_db_user)):
    await user.delete()
