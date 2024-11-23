from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_db
from src.wallet.schemas import OperationRequest, WalletResponse
from src.wallet.crud import create_or_get_wallet, process_operation


router = APIRouter(prefix='/wallets')


@router.post("/{wallet_uuid}/operation", response_model=WalletResponse)
async def perform_operation(wallet_uuid: int, operation: OperationRequest, db: AsyncSession = Depends(get_db)):
    try:
        wallet = await process_operation(db, wallet_uuid, operation)
        return WalletResponse(uuid=wallet.uuid, balance=wallet.balance)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{wallet_uuid}", response_model=WalletResponse)
async def get_wallet_balance(wallet_uuid: int, db: AsyncSession = Depends(get_db)):
    wallet = await create_or_get_wallet(db, wallet_uuid)
    if wallet is None:
        raise HTTPException(status_code=404, detail="Wallet not found")
    return WalletResponse(uuid=wallet.uuid, balance=wallet.balance)