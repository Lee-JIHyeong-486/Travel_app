from motor.motor_asyncio import AsyncIOMotorClient

client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client["travel_db"]

users_collection = db["users"] # collection for user registeration data
plans_collection = db["plans"] # collection for travel plan data
