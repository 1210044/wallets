from sqlalchemy import Column, Integer, Float

from src.models import Base


class Wallet(Base):
    __tablename__ = "wallets"

    uuid = Column(Integer, primary_key=True, index=True)
    balance = Column(Float, default=0)