import os
from itertools import count

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="SimpleBank API")

# In-memory storage: data resets when the app restarts.
# That is fine for a DevOps demo, and a known limitation we will document.
_accounts: dict[int, dict] = {}
_ids = count(1)


class AccountCreate(BaseModel):
    owner: str = Field(min_length=1, max_length=100)


class DepositRequest(BaseModel):
    amount_paise: int = Field(gt=0)  # money as whole paise, never floats


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/version")
def version():
    # Set by the pipeline at deploy time, so we can prove which commit is live.
    return {
        "env": os.getenv("APP_ENV", "local"),
        "git_sha": os.getenv("GIT_SHA", "local"),
    }


@app.post("/accounts", status_code=201)
def create_account(body: AccountCreate):
    account_id = next(_ids)
    _accounts[account_id] = {"id": account_id, "owner": body.owner, "balance_paise": 0}
    return _accounts[account_id]


@app.get("/accounts/{account_id}")
def get_account(account_id: int):
    account = _accounts.get(account_id)
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    return account


@app.post("/accounts/{account_id}/deposit")
def deposit(account_id: int, body: DepositRequest):
    account = _accounts.get(account_id)
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    account["balance_paise"] += body.amount_paise
    return account
