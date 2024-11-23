from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.wallet.models import Wallet
from src.wallet.schemas import OperationRequest, OperationType


async def create_or_get_wallet(db: AsyncSession, wallet_uuid: int):
    wallet = await get_wallet(db, wallet_uuid)

    if wallet is None:
        wallet = Wallet(uuid=wallet_uuid, balance=0)
        db.add(wallet)
        await db.commit()
    return wallet


async def get_wallet(db: AsyncSession, wallet_uuid: int, block_entry: bool = False):
    stmt = select(Wallet)\
        .where(Wallet.uuid == wallet_uuid)
    
    if block_entry:
        stmt.with_for_update()
    
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def process_operation(db: AsyncSession, wallet_uuid: int, operation: OperationRequest):
    async with db.begin():
        wallet = await get_wallet(db, wallet_uuid, block_entry=True)
        if wallet is None:
            raise ValueError("Wallet not found")

        if operation.operationType == OperationType.WITHDRAW and wallet.balance < operation.amount:
            raise ValueError("Insufficient funds")

        if operation.operationType == OperationType.DEPOSIT:
            wallet.balance += operation.amount
        elif operation.operationType == OperationType.WITHDRAW:
            wallet.balance -= operation.amount
        db.add(wallet)

    return wallet