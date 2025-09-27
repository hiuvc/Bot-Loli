import os
import json
import asyncio
from datetime import datetime
import requests
from colorama import init, Fore
import discord
from discord.ext import commands, tasks
from uptime import save_start_time, get_last_uptime
# Gọi keep_alive từ file riêng
from keep_alive import keep_alive
# Khi bot khởi động
last_uptime = get_last_uptime()
if last_uptime:
    hours, remainder = divmod(last_uptime.total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)
    print(
        f"⚠ Bot lần trước đã on được {int(hours)}h {int(minutes)}m {int(seconds)}s trước khi bị tắt."
    )

# Ghi lại thời gian start mới
save_start_time()
# ================= CONFIG =================
init(autoreset=True)
TOKEN = os.getenv("DISCORD_TOKEN")  # Set trong environment variable
CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID", "1420764782390149211"))
URL = "https://dashboard.kingdev.sbs/tool_ug.php?status"
MESSAGE_FILE = "stock_message.json"


# ================= HELPER =================
def load_message_id():
    if os.path.exists(MESSAGE_FILE):
        try:
            with open(MESSAGE_FILE, "r") as f:
                data = json.load(f)
                return int(data.get("message_id"))
        except:
            return None
    return None


def save_message_id(message_id):
    with open(MESSAGE_FILE, "w") as f:
        json.dump({"message_id": message_id}, f)


def get_stock_embed():
    try:
        response = requests.get(URL, timeout=30)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        return discord.Embed(title="📡 UGPHONE STOCK STATUS",
                             description=f"❌ Lỗi khi kết nối: {e}",
                             color=discord.Color.red())

    servers = data.get("servers", {})
    status = data.get("status", "unknown")
    last_updated = data.get("last_updated", "unknown")
    embed = discord.Embed(
        title="📡 UGPHONE STOCK STATUS",
        description=f"**Status:** {status}\n**Message:** Hiếu Đẹp Zai",
        color=discord.Color.green()
        if status == "success" else discord.Color.red())

    green = "🟢"
    red = "🔴"
    for server, stt in servers.items():
        icon = green if stt != "Out of Stock" else red
        embed.add_field(name=server, value=f"{icon} {stt}", inline=True)

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    embed.set_footer(
        text=f"Lần cập nhật cuối: {last_updated} • Tự động làm mới mỗi 5 phút")
    return embed


# ================= DISCORD BOT =================
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
stock_message = None


async def init_stock_message():
    global stock_message
    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        print(Fore.RED + "❌ Không tìm thấy channel. Kiểm tra CHANNEL_ID!")
        return

    message_id = load_message_id()
    if message_id:
        try:
            stock_message = await channel.fetch_message(message_id)
            print(Fore.YELLOW + "✔ Đã load message cũ, sẽ edit tiếp.")
        except:
            stock_message = None
            print(Fore.YELLOW + "⚠ Không tìm thấy message cũ, sẽ gửi mới.")

    if stock_message is None:
        embed = get_stock_embed()
        stock_message = await channel.send(embed=embed)
        save_message_id(stock_message.id)
        print(Fore.GREEN + f"✔ Gửi message stock mới: {stock_message.id}")


# ================= TASK LOOP =================
@tasks.loop(minutes=5)
async def update_stock():
    global stock_message
    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        print(Fore.RED + "❌ Không tìm thấy channel. Kiểm tra CHANNEL_ID!")
        return

    embed = get_stock_embed()
    try:
        if stock_message is None:
            stock_message = await channel.send(embed=embed)
            save_message_id(stock_message.id)
        else:
            await stock_message.edit(embed=embed)
        print(Fore.CYAN +
              f"♻ Updated stock at {datetime.now().strftime('%H:%M:%S')}")
    except Exception as e:
        print(Fore.RED + f"❌ Lỗi khi update message: {e}")


# ================= AUTO RECONNECT =================
async def run_bot():
    while True:
        try:
            await bot.start(TOKEN)
        except Exception as e:
            print(Fore.RED + f"Lỗi bot: {e}")
            await asyncio.sleep(5)  # Đợi 5 giây trước khi reconnect


# ================= EVENTS =================
@bot.event
async def on_ready():
    print(Fore.GREEN + f"Bot đã đăng nhập: {bot.user}")
    await init_stock_message()
    update_stock.start()


# ================= MAIN =================
if __name__ == "__main__":
    if not TOKEN:
        print(
            Fore.RED +
            "❌ Vui lòng thiết lập DISCORD_TOKEN trong environment variables!")
        exit(1)

    keep_alive()  # chạy Flask server
    asyncio.run(run_bot())  # chạy bot với auto reconnect
