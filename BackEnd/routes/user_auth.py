from fastapi import APIRouter
from components.user_auth import UserAuth
from db.client import users_collection

router = APIRouter()

@router.post("/register")
async def register_user(user: UserAuth):
    found_user = await users_collection.find_one({"email": user.email})
    if found_user:
        return {"success": False, "message": "Email already registered. Please use a different email."}

    await users_collection.insert_one(user.model_dump())
    return {"success": True, "message": "Registration successful!"}

@router.post("/login")
async def login(user: UserAuth):
    print(user)
    found_user = await users_collection.find_one({"email": user.email})

    if not found_user or found_user["password"] != user.password:
        return {"success": False, "message": "Invalid email or password."}

    return {"success": True, "user_id": str(found_user["_id"])}