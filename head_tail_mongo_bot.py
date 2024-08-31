from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pymongo import MongoClient
import random

# Replace these with your actual credentials
API_ID = "25064357"
API_HASH = "cda9f1b3f9da4c0c93d1f5c23ccb19e2"
BOT_TOKEN = "7329929698:AAGD5Ccwm0qExCq9_6GVHDp2E7iidLH-McU"

# MongoDB connection setup
MONGO_URI = "mongodb+srv://tanjiro1564:tanjiro1564@cluster0.pp5yz4e.mongodb.net/?retryWrites=true&w=majority"  # Replace with your MongoDB URI
mongo_client = MongoClient(MONGO_URI)
db = mongo_client["HeadTailGameDB"]
users_collection = db["users"]

# Initialize the Pyrogram Client
app = Client("head_tail_mongo_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Function to initialize user in the database
def initialize_user(user_id, username):
    if not users_collection.find_one({"user_id": user_id}):
        users_collection.insert_one({"user_id": user_id, "username": username, "points": 0})

# /startht command handler
@app.on_message(filters.command("startht") & filters.group)
async def start_ht(client, message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name

    # Initialize user in the database if not exists
    initialize_user(user_id, username)

    # Create the buttons
    buttons = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Your Scorecard", callback_data="your_scorecard")],
            [InlineKeyboardButton("Leaderboard", callback_data="leaderboard")],
            [InlineKeyboardButton("My Master", url="http://t.me//sung_jinwo4")]
        ]
    )

    await message.reply_text(
        "Welcome to the Head or Tail Game! Choose an option below:",
        reply_markup=buttons
    )

# Callback query handler for buttons
@app.on_callback_query()
async def button_click(client, callback_query):
    user_id = callback_query.from_user.id

    if callback_query.data == "your_scorecard":
        user_data = users_collection.find_one({"user_id": user_id})
        points = user_data['points'] if user_data else 0
        await callback_query.message.edit_text(f"Your current score: {points} points.")

    elif callback_query.data == "leaderboard":
        leaderboard = users_collection.find().sort("points", -1).limit(10)
        leaderboard_text = "🏆 Leaderboard 🏆\n\n"
        for i, user in enumerate(leaderboard):
            leaderboard_text += f"{i + 1}. @{user['username']} - {user['points']} points\n"
        await callback_query.message.edit_text(leaderboard_text)

# /go command handler
@app.on_message(filters.command("go") & filters.group)
async def go_game(client, message: Message):
    # Create the buttons for Head or Tail
    buttons = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Head", callback_data="choose_head")],
            [InlineKeyboardButton("Tail", callback_data="choose_tail")]
        ]
    )

    await message.reply_text(
        "Thanks for starting... Now choose:",
        reply_markup=buttons
    )

# Handle Head or Tail choice
@app.on_callback_query(filters.regex("^choose_"))
async def choose_head_tail(client, callback_query):
    user_id = callback_query.from_user.id
    username = callback_query.from_user.username or callback_query.from_user.first_name

    # Initialize user in the database if not exists
    initialize_user(user_id, username)

    # Determine the result of the game
    user_choice = callback_query.data.split("_")[1]  # "head" or "tail"
    result = random.choice(["head", "tail"])

    if user_choice == result:
        users_collection.update_one({"user_id": user_id}, {"$inc": {"points": 1}})
        await callback_query.message.edit_text(f"Congratulations! You chose {user_choice.capitalize()} and won! 🎉")
    else:
        await callback_query.message.edit_text(f"Sorry! You chose {user_choice.capitalize()}, but it was {result.capitalize()}. Better luck next time!")

# Run the bot
if __name__ == "__main__":
    print("Bot is starting...")
    app.run()

