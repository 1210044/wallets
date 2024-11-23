import pytest, asyncio, pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from src.main import app
from src.db import get_db
from src.models import Base
from src.wallet.models import Wallet


TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope='session')
async def async_db_engine():
    engine = create_async_engine(TEST_DATABASE_URL, future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()


@pytest_asyncio.fixture(scope='session')
async def async_db(async_db_engine):
    async_session = sessionmaker(
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
        bind=async_db_engine,
        class_=AsyncSession,
    )

    async with async_session() as session:
        await session.begin()

        yield session

        await session.rollback()


@pytest_asyncio.fixture(scope='session')
async def async_client(async_db: AsyncSession) -> AsyncClient:
    def override_get_db():
        yield async_db

    app.dependency_overrides[get_db] = override_get_db
    return AsyncClient(app=app, base_url="http://test-server")


@pytest_asyncio.fixture(scope='session')
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


pytestmark = pytest.mark.asyncio


async def test_get_or_create_wallet(async_client: AsyncClient, async_db: AsyncSession):
    wallet_uuid = 123
    balance = 0
    # test_wallet = Wallet(uuid=wallet_uuid, balance=balance)
    # async_db.add(test_wallet)
    # await async_db.commit()

    response = await async_client.get(f"/api/v1/wallets/{wallet_uuid}")

    assert response.status_code == 200
    assert response.json() == {"uuid": wallet_uuid, "balance": balance}


async def test_deposit_wallet_by_id(async_client: AsyncClient, async_db: AsyncSession):
    wallet_uuid = 123
    operation_data = {"amount": 1000.0, "operationType": "DEPOSIT"}

    response = await async_client.post(f"/api/v1/wallets/{wallet_uuid}/operation", json=operation_data)
    
    assert response.status_code == 200
    assert response.json() == {"uuid": wallet_uuid, "balance": 1000.0}


async def test_withdraw_wallet_by_id(async_client: AsyncClient, async_db: AsyncSession):
    wallet_uuid = 123
    operation_data = {"amount": 1000.0, "operationType": "WITHDRAW"}

    response = await async_client.post(f"/api/v1/wallets/{wallet_uuid}/operation", json=operation_data)
    
    assert response.status_code == 200
    assert response.json() == {"uuid": wallet_uuid, "balance": 0.0}