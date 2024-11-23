from fastapi import FastAPI

from src.wallet.router import router as wallets_router


app = FastAPI()

app.include_router(wallets_router, prefix='/api/v1')