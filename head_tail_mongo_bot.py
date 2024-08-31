import random
import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Replace these with your actual credentials
API_ID = "25064357"
API_HASH = "cda9f1b3f9da4c0c93d1f5c23ccb19e2"
BOT_TOKEN = "7329929698:AAGD5Ccwm0qExCq9_6GVHDp2E7iidLH-McU"
MONGO_URI = "mongodb+srv://tanjiro1564:tanjiro1564@cluster0.pp5yz4e.mongodb.net/?retryWrites=true&w=majority"  

# Initialize the Pyrogram Client
app = Client("head_tail_game_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Initialize the MongoDB client
mongo_client = MongoClient(MONGO_URI)
db = mongo_client["head_tail_game"]
users_collection = db["users"]

# Function to get user score
def get_user_score(user_id):
    user = users_collection.find_one({"user_id": user_id})
    return user["score"] if user else 0

# Function to update user score
def update_user_score(user_id, username, points):
    users_collection.update_one({"user_id": user_id}, {"$set": {"username": username}, "$inc": {"score": points}}, upsert=True)

# Function to get leaderboard
def get_leaderboard():
    return list(users_collection.find().sort("score", -1).limit(10))

# Command: /startht
@app.on_message(filters.command("startht") & filters.group)
async def start_ht(client, message):
    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Your Scorecard", callback_data="scorecard")],
            [InlineKeyboardButton("Leaderboard", callback_data="leaderboard")],
            [InlineKeyboardButton("My Master", url="http://t.me/sung_jinwo4")],
        ]
    )
    await message.reply_text("Choose an option:", reply_markup=keyboard)

# Command: /go
@app.on_message(filters.command("go") & filters.group)
async def start_game(client, message):
    user_id = message.from_user.id
    username = message.from_user.username

    # Ensure user is in the database
    update_user_score(user_id, username, 0)

    # Send the game start message with options for Head or Tail
    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Head", callback_data="choose_head")],
            [InlineKeyboardButton("Tail", callback_data="choose_tail")],
        ]
    )
    await message.reply_text("Thanks for starting... Now choose:", reply_markup=keyboard)

# Callback for choosing Head or Tail
@app.on_callback_query(filters.regex(r"^choose_"))
async def choose_option(client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    username = callback_query.from_user.username
    choice = callback_query.data.split("_")[1]  # 'head' or 'tail'
    
    # Randomly decide the outcome
    result = random.choice(["head", "tail"])

    # Determine if the user won
    if choice == result:
        update_user_score(user_id, username, 10)
        await callback_query.message.reply_text(f"Congratulations! It's {result}. You won 10 points!")
    else:
        await callback_query.message.reply_text(f"Sorry, it's {result}. Better luck next time!")

    # Acknowledge the callback
    await callback_query.answer()

# Callback for displaying user scorecard
@app.on_callback_query(filters.regex(r"^scorecard$"))
async def show_scorecard(client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    score = get_user_score(user_id)
    await callback_query.message.reply_text(f"Your current score is: {score} points.")
    await callback_query.answer()

# Callback for displaying leaderboard
@app.on_callback_query(filters.regex(r"^leaderboard$"))
async def show_leaderboard(client, callback_query: CallbackQuery):
    leaderboard = get_leaderboard()
    response = "🏆 Leaderboard 🏆\n\n"
    for i, user in enumerate(leaderboard):
        response += f"{i + 1}. @{user['username']}: {user['score']} points\n"
    await callback_query.message.reply_text(response)
    await callback_query.answer()

# Run the bot
if __name__ == "__main__":
    print("Bot is starting...")
    app.run()

