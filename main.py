# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import os
import re
import sys
import time
import asyncio
import requests
import threading
import yt_dlp
from flask import Flask
from aiohttp import ClientSession
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait
from subprocess import getstatusoutput

from vars import API_ID, API_HASH, BOT_TOKEN
import core as helper


bot = Client(
    "bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# -------------------- Download Progress Function -------------------- #
async def download_video_with_progress(url, filename, message, bot):
    """
    वीडियो डाउनलोड करेगा और Telegram पर progress update देगा।
    """
    def progress_hook(d):
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', '0%')
            speed = d.get('_speed_str', '0 KiB/s')
            eta = d.get('_eta_str', 'N/A')
            text = f"📥 **Downloading...**\n\nProgress: {percent}\n⚡ Speed: {speed}\n⏳ ETA: {eta}"
            try:
                bot.loop.create_task(
                    bot.edit_message_text(
                        chat_id=message.chat.id,
                        message_id=message.id,
                        text=text
                    )
                )
            except:
                pass
        elif d['status'] == 'finished':
            bot.loop.create_task(
                bot.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=message.id,
                    text="✅ **Download complete!**"
                )
            )

    ydl_opts = {
        'outtmpl': filename,
        'progress_hooks': [progress_hook],
        'format': 'bestvideo+bestaudio/best',
        'noplaylist': True,
        'quiet': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

# -------------------- Bot Commands -------------------- #

@bot.on_message(filters.command(["start"]))
async def start(bot: Client, m: Message):
    await m.reply_text(
        f"<b>Hello {m.from_user.mention} 👋\n\n"
        "I Am A Bot For Download Links From Your **.TXT** File "
        "And Then Upload That File On Telegram.\n\n"
        "Use /upload to start and /stop to stop any ongoing task.</b>"
    )


@bot.on_message(filters.command("stop"))
async def restart_handler(_, m):
    await m.reply_text("**Stopped**🚦", True)
    os.execl(sys.executable, sys.executable, *sys.argv)


@bot.on_message(filters.command(["upload"]))
async def upload(bot: Client, m: Message):
    editable = await m.reply_text('📄 Send .TXT file containing video links ⚡️')
    input: Message = await bot.listen(editable.chat.id)
    x = await input.download()
    await input.delete(True)

    try:
        with open(x, "r") as f:
            content = f.read()
        content = content.split("\n")
        links = []
        for i in content:
            links.append(i.split("://", 1))
        os.remove(x)
    except:
        await m.reply_text("❌ Invalid file input.")
        os.remove(x)
        return

    await editable.edit(
        f"**Total Links Found:** `{len(links)}`\n\n"
        "**Send Starting Number (Default = 1):**"
    )
    input0: Message = await bot.listen(editable.chat.id)
    raw_text = input0.text
    await input0.delete(True)

    await editable.edit("**Now Please Send Me Your Batch Name:**")
    input1: Message = await bot.listen(editable.chat.id)
    raw_text0 = input1.text
    await input1.delete(True)

    await editable.edit("**Enter Resolution (144,240,360,480,720,1080):**")
    input2: Message = await bot.listen(editable.chat.id)
    raw_text2 = input2.text
    await input2.delete(True)

    await editable.edit("**Enter Caption for Uploaded Files:**")
    input3: Message = await bot.listen(editable.chat.id)
    raw_text3 = input3.text
    await input3.delete(True)

    MR = raw_text3

    await editable.edit("**Send Thumbnail URL or type 'no':**")
    input6 = await bot.listen(editable.chat.id)
    raw_text6 = input6.text
    await input6.delete(True)
    await editable.delete()

    thumb = None
    if raw_text6.startswith("http"):
        getstatusoutput(f"wget '{raw_text6}' -O 'thumb.jpg'")
        thumb = "thumb.jpg"

    count = int(raw_text) if len(links) > 1 else 1

    for i in range(count - 1, len(links)):
        try:
            V = links[i][1].replace("file/d/", "uc?export=download&id=")
            url = "https://" + V
            name1 = links[i][0].replace(":", "").replace("/", "").strip()
            name = f'{str(count).zfill(3)}) {name1[:60]}'

            cc = f'🎬 **Vid_ID:** {str(count).zfill(3)}. {name1}\n📁 **Batch:** {raw_text0}\n📝 {MR}'

            prog_msg = await m.reply_text("📥 Downloading started...")
            await download_video_with_progress(url, f"{name}.mp4", prog_msg, bot)

            await bot.send_video(
                chat_id=m.chat.id,
                video=open(f"{name}.mp4", "rb"),
                caption=cc,
                thumb=thumb if thumb else None
            )
            os.remove(f"{name}.mp4")
            count += 1
            time.sleep(1)

        except Exception as e:
            await m.reply_text(f"❌ Error: {e}")
            continue

    await m.reply_text("✅ **All Downloads Complete Boss! 😎**")


# -------------------- Render Flask Keepalive -------------------- #

app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Bot is running on Render Web Service!", 200


def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


def run_bot():
    bot.run()


if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    run_bot()
