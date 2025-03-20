import os
import yt_dlp
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Import credentials from info.py
from info import API_ID, API_HASH, BOT_TOKEN, START_IMG

bot = Client("yt_downloader", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# --- BUTTONS ---
def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("ℹ️ Help", callback_data="help"), InlineKeyboardButton("⬇️ Download", callback_data="download")],
        [InlineKeyboardButton("ℹ️ About", callback_data="about")]
    ])

def back_close_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back", callback_data="back"), InlineKeyboardButton("❌ Close", callback_data="close")]
    ])

def about_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back", callback_data="back"), InlineKeyboardButton("❌ Close", callback_data="close")],
        [InlineKeyboardButton("🌐 Hosted on Koyeb", url="https://www.koyeb.com/")]
    ])

def format_buttons(video_id):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎵 Audio", callback_data=f"audio|{video_id}"), InlineKeyboardButton("📹 Video", callback_data=f"video|{video_id}")]
    ])

def quality_buttons(video_id, mode):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔹 720p", callback_data=f"{mode}|720|{video_id}"), InlineKeyboardButton("🔹 360p", callback_data=f"{mode}|360|{video_id}")],
        [InlineKeyboardButton("🔹 144p", callback_data=f"{mode}|144|{video_id}")]
    ])

@bot.on_message(filters.command("start"))
def start(client, message):
    message.reply_photo(START_IMG, caption="I am a YouTube Video & Playlist Downloader Bot! Send me a link and I'll fetch it for you.", reply_markup=main_menu())

@bot.on_message(filters.text & filters.private)
def process_link(client, message):
    url = message.text
    ydl_opts = {"quiet": True}
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
    
    video_id = info.get("id")
    title = info.get("title")
    
    message.reply_text(f"🎬 **Title:** {title}\n🎞 **Choose Format:**", reply_markup=format_buttons(video_id))

@bot.on_callback_query()
def callback_handler(client, callback_query):
    data = callback_query.data
    user_id = callback_query.from_user.id

    if data.startswith("audio|") or data.startswith("video|"):
        mode, video_id = data.split("|")
        callback_query.message.edit_text("📌 Choose quality:", reply_markup=quality_buttons(video_id, mode))
    
    elif data.startswith("video|") or data.startswith("audio|"):
        mode, quality, video_id = data.split("|")
        callback_query.message.edit_text(f"📥 Downloading {mode.upper()} in {quality}p...")

        url = f"https://www.youtube.com/watch?v={video_id}"
        ydl_opts = {"format": f"bestaudio/best" if mode == "audio" else f"bestvideo[height<={quality}]+bestaudio"}

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            file_path = ydl.download([url])

        callback_query.message.reply_document(file_path, caption="✅ Download Complete!")

bot.run()
