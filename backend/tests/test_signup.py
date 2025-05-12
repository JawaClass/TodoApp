from fastapi import FastAPI
from fastapi.testclient import TestClient
import asyncio
from backend.app import app
import pytest
from httpx import ASGITransport, AsyncClient
from datetime import datetime
from fastapi import status
 

client = AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    )
 

async def test_signup_user():
    email = f"fabian_{datetime.now().timestamp()}@gmail.com"
    async with client as ac:
        response = await ac.post("/signup/user", json={
        "email": email,
        "password": "1234"
    })
       
    assert response.status_code == status.HTTP_200_OK 


async def test_duplicate_signup():
    email = f"fabian_{datetime.now().timestamp()}@gmail.com"
    json_param = {
            "email": email,
            "password": "1234"
         }
    async with client as ac:
        response = await ac.post("/signup/user", json=json_param)
        assert response.status_code == status.HTTP_200_OK
        response = await ac.post("/signup/user", json=json_param)
        assert response.status_code == status.HTTP_409_CONFLICT
 