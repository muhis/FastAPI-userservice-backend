from app import app, app_init
from httpx import AsyncClient
from models import UserDB, UserIn, UserEdit
import pytest


@pytest.mark.asyncio
async def test_root():
    await app_init()
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/")
    assert response.status_code == 200
    assert response.json() == {"name": "user-service"}


@pytest.fixture
async def clear_db_on_tear_down():
    """
    Remove all documents in the database.
    """
    await app_init()
    all_objects = await UserDB.find_all().to_list()
    try:
        yield all_objects
    except Exception:
        # Below is suboptimal way to mock db.
        await UserDB.delete_all({})
        raise
    await UserDB.delete_all({})

async def create_users(number):
    users = [UserDB(name=str(index), email=f'{index}@example.com' ) for index in range(number)]
    await UserDB.insert_many(users)
    return await UserDB.find_all().to_list()


@pytest.mark.asyncio
async def test_get_users(clear_db_on_tear_down):
    db_users = await create_users(10)
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/v1/users/")
    assert (
        [UserDB(**payload_user) for payload_user in response.json()] ==
        db_users
    )


@pytest.mark.asyncio
async def test_get_user(clear_db_on_tear_down):
    db_users = await create_users(1)
    db_user = db_users[0]
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get(f"/v1/users/{db_user.id}")
    assert (
        UserDB(**response.json()) ==
        db_user
    )


@pytest.mark.asyncio
async def test_create_user(clear_db_on_tear_down):
    user = UserIn(name='Mohammed', email="email@example.com")
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(f"/v1/users/", json=user.dict())
    assert response.status_code == 201
    assert (
        response.json() ==
        dict(**user.dict(), id=response.json()['id'])
    )

@pytest.mark.asyncio
async def test_update_user(clear_db_on_tear_down):
    user_db = await UserDB(name='Mohammed', email="incorrect_email@email.com").save()
    user = UserEdit(email="email@example.com")
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.put(f"/v1/users/{user_db.id}", json=user.dict())
    assert response.status_code == 200
    assert (response.json()['email'] == user.email)
    fresh_user_db = await UserDB.get(user_db.id)
    assert fresh_user_db.email == 'email@example.com'

@pytest.mark.asyncio
async def test_delete_user(clear_db_on_tear_down):
    user_db_list = await create_users(1)
    user_db = user_db_list[0]
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.delete(f"/v1/users/{user_db.id}")
    assert response.status_code == 204
    fresh_user_db = await UserDB.get(user_db.id)
    assert fresh_user_db is None
