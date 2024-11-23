from pydantic import BaseModel, Field
from enum import Enum


class OperationType(str, Enum):
    DEPOSIT = "DEPOSIT"
    WITHDRAW = "WITHDRAW"


class OperationRequest(BaseModel):
    operationType: OperationType
    amount: float = Field(gt=0)


class WalletResponse(BaseModel):
    uuid: int
    balance: float