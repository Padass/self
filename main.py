import discord
from discord.ext import commands
import requests
import os
import asyncio
import time
from dotenv import load_dotenv

# Load biến môi trường từ file .env
load_dotenv()

# Đọc từ environment variables (ưu tiên) hoặc fallback về config.py
USER_TOKEN = os.getenv('USER_TOKEN')
CHANNEL_ID_NGUON_STR = os.getenv('CHANNEL_ID_NGUON')
CHANNEL_ID_DICH_STR = os.getenv('CHANNEL_ID_DICH')
ALLOWED_USER_ID_STR = os.getenv('ALLOWED_USER_ID')

CHANNEL_ID_NGUON = int(CHANNEL_ID_NGUON_STR) if CHANNEL_ID_NGUON_STR else None
CHANNEL_ID_DICH = int(CHANNEL_ID_DICH_STR) if CHANNEL_ID_DICH_STR else None
ALLOWED_USER_ID = int(ALLOWED_USER_ID_STR) if ALLOWED_USER_ID_STR else None

# Fallback về config.py nếu không có trong .env
if not USER_TOKEN or not CHANNEL_ID_NGUON or not CHANNEL_ID_DICH:
    try:
        from config import USER_TOKEN as CFG_TOKEN, CHANNEL_ID_NGUON as CFG_NGUON, CHANNEL_ID_DICH as CFG_DICH
        USER_TOKEN = USER_TOKEN or CFG_TOKEN
        CHANNEL_ID_NGUON = CHANNEL_ID_NGUON or CFG_NGUON
        CHANNEL_ID_DICH = CHANNEL_ID_DICH or CFG_DICH
        try:
            from config import ALLOWED_USER_ID as CFG_ALLOWED_USER_ID
            ALLOWED_USER_ID = ALLOWED_USER_ID or CFG_ALLOWED_USER_ID
        except ImportError:
            pass
    except ImportError:
        pass

# Kiểm tra token và channel IDs
if not USER_TOKEN:
    raise ValueError("USER_TOKEN không được tìm thấy! Vui lòng tạo file .env hoặc config.py")
if not CHANNEL_ID_NGUON or not CHANNEL_ID_DICH:
    raise ValueError("CHANNEL_ID_NGUON và CHANNEL_ID_DICH không được tìm thấy! Vui lòng tạo file .env hoặc config.py") 

# Địa chỉ API Endpoint TÙY CHỈNH để gửi tin nhắn

API_URL_GUI_TIN = 'https://discord.com/api/v9/channels/{channel_id}/messages' 

# Headers cần thiết cho yêu cầu HTTP (Gửi tin nhắn)
# Lưu ý: Với user token (self-bot), không cần prefix "Bot "
HEADERS = {
    'Authorization': USER_TOKEN,
    'Content-Type': 'application/json'
}

# BẢN ĐỒ ÁNH XẠ TỪ KHÓA VÀ PHẢN HỒI
KEYWORD_RESPONSES = {
    "dưa hấu": "**Dưa hấu** đang bán trong Shop!!\n|| <@&1443099046448332821> ||",
    "bí ngô": "**Bí ngô** đang bán trong Shop!!\n|| <@&1443099046448332821> ||",
    "xoài": "**Xoài** đang bán trong Shop!!\n|| <@&1443099046448332821> ||",
    "táo đường": "**Táo đường** đang bán trong Shop!!\n|| <@&1443099046448332821> ||",
    "đậu": "**Đậu** đang bán trong Shop!!\n|| <@&1443099046448332821> ||",
    "khế": "**Khế** đang bán trong Shop!!\n|| <@&1443099046448332821> ||",
    "vòi xanh": "**Vòi Xanh** đang bán trong Shop!!\n|| <@&1443098706265243648> ||",
    "vòi đỏ": "**Vòi Đỏ** đang bán trong Shop!!\n|| <@&1443098706265243648> ||",
    "đơn hàng": "**Đơn hàng** đã được làm mới!!\n|| <@&1443098706265243648> ||",
    "ánh trăng": "**Ánh Trăng** xuất hiện!! có thể xuất hiện biến thể **[ Ánh Trăng ]**\n|| <@&1443097923431694377> ||",
    "cực quang": "**Cực Quang** xuất hiện!! có thể xuất hiện biến thể **[ Cực Quang ]**\n|| <@&1443097923431694377> ||",       
    "bão": "**Bão** xuất hiện!! có thể xuất hiện biến thể **[ Nhiễm Điện ]**\n|| <@&1443097923431694377> ||",
    "mưa": "**Mưa** xuất hiện!! có thể xuất hiện biến thể **[ Ẩm ướt ]**\n|| <@&1443097923431694377> ||",   
    "sương mù": "**Sương Mù** xuất hiện!! có thể xuất hiện biến thể **[ Ẩm ướt ]**\n|| <@&1443097923431694377> ||",
    "sương sớm": "**Sương Sớm** xuất hiện!! có thể xuất hiện biến thể **[ Sương]**\n|| <@&1443097923431694377> ||",
     "tuyết": "**Tuyết** xuất hiện!! có thể xuất hiện biến thể **[ Khí lạnh ]**\n|| <@&1443097923431694377> ||",
    "nắng nóng": "**Nắng Nóng** xuất hiện!! có thể xuất hiện biến thể **[ Khô ]**\n|| <@&1443097923431694377> ||",
    "gió cát": "**Gió Cát** xuất hiện!! có thể xuất hiện biến thể **[ Cát ]**\n|| <@&1443097923431694377> ||",
    "ảo ảnh": "**Ảo Ảnh** xuất hiện!! có thể xuất hiện biến thể **[ Ảo Ảnh ]**\n|| <@&1443097923431694377> ||",
    "gio": "**Gió** xuất hiện!! có thể xuất hiện biến thể **[ Gió ]**\n|| <@&1443097923431694377> ||",
}

# =========================================================
#             🛠️ CÁC HÀM XỬ LÝ
# =========================================================

client = discord.Client()

# Biến để theo dõi số lần retry
retry_count = 0
max_retries = 5

def gui_tin_nhan_qua_http(channel_id, content):
    """Gửi tin nhắn đến API Endpoint tùy chỉnh với retry logic."""
    url = API_URL_GUI_TIN.format(channel_id=channel_id)
    data = {'content': content}
    
    for attempt in range(3):  # Thử tối đa 3 lần
        try:
            response = requests.post(url, headers=HEADERS, json=data, timeout=10)
            if response.status_code == 200:
                print(f"✅ Gửi thành công tin nhắn tới kênh {channel_id}.")
                return
            elif response.status_code == 429:  # Rate limit
                print(f"⚠️ Rate limit! Đợi 5 giây...")
                time.sleep(5)
                continue
            else:
                print(f"❌ Lỗi gửi tin {response.status_code}: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Lỗi kết nối HTTP (lần {attempt + 1}): {e}")
            if attempt < 2:  # Không phải lần cuối
                print(f"Đợi {2 ** attempt} giây trước khi thử lại...")
                time.sleep(2 ** attempt)
    
    print("❌ Không thể gửi tin nhắn sau 3 lần thử!")

# =========================================================
#             🤖 LOGIC SELF-BOT
# =========================================================

@client.event
async def on_ready():
    global retry_count
    retry_count = 0  # Reset retry count khi kết nối thành công
    print(f'✅ Tài khoản tự động đã đăng nhập với tên: {client.user} (Self-Bot Activated)')
    print(f'📡 Đang theo dõi kênh nguồn: {CHANNEL_ID_NGUON}')
    print(f'📤 Sẽ gửi tin đến kênh đích: {CHANNEL_ID_DICH}')

@client.event
async def on_disconnect():
    print("⚠️ Mất kết nối với Discord!")

@client.event
async def on_resumed():
    print("🔄 Đã khôi phục kết nối với Discord!")

@client.event
async def on_message(message):
    # Debug: In thông tin tin nhắn nhận được
    print(f"📨 Nhận tin nhắn từ {message.author} trong kênh {message.channel.id}: {message.content[:50]}")
    
    # Tránh lặp vô hạn và chỉ xử lý kênh nguồn
    if message.author.id == client.user.id:
        print("⏭️ Bỏ qua: Tin nhắn từ chính bot")
        return
    
    if message.channel.id != CHANNEL_ID_NGUON:
        print(f"⏭️ Bỏ qua: Không phải kênh nguồn (nhận: {message.channel.id}, mong đợi: {CHANNEL_ID_NGUON})")
        return
    
    # Kiểm tra người gửi (nếu có cấu hình ALLOWED_USER_ID)
    if ALLOWED_USER_ID and message.author.id != ALLOWED_USER_ID:
        print(f"⏭️ Bỏ qua: Người gửi không hợp lệ (nhận: {message.author.id}, mong đợi: {ALLOWED_USER_ID})")
        return

    print(f"✅ Xử lý tin nhắn từ kênh nguồn: {message.content}")
    
    raw_content = message.content 
    content_lower = raw_content.lower() 

    # --- 1. KIỂM TRA TỪ KHÓA VÀ PHẢN HỒI ---
    keyword_found = False
    for keyword, response_message in KEYWORD_RESPONSES.items():
        if keyword in content_lower:
            keyword_found = True
            print(f"🔥 Phát hiện từ khóa '{keyword}'. Đang gửi phản hồi...")
            
            # Gửi tin nhắn phản hồi đến kênh đích
            gui_tin_nhan_qua_http(CHANNEL_ID_DICH, response_message)
            
            # Thoát khỏi vòng lặp kiểm tra từ khóa ngay lập tức
            break 
    
    if not keyword_found:
        print(f"🔍 Không tìm thấy từ khóa nào trong: {content_lower}")
        
# =========================================================
#             ▶️ KHỞI CHẠY BOT VỚI AUTO-RETRY
# =========================================================

async def run_bot_with_retry():
    """Chạy bot với auto-retry khi bị disconnect."""
    global retry_count
    
    while retry_count < max_retries:
        try:
            print(f"🚀 Đang khởi động Self-Bot... (Lần thử: {retry_count + 1})")
            await client.start(USER_TOKEN)
        except discord.errors.LoginFailure:
            print("❌ LỖI: Đăng nhập thất bại! Kiểm tra lại USER_TOKEN.")
            break
        except discord.ConnectionClosed:
            retry_count += 1
            if retry_count < max_retries:
                wait_time = min(60, 2 ** retry_count)  # Exponential backoff, tối đa 60s
                print(f"🔄 Kết nối bị đóng. Thử lại sau {wait_time} giây... ({retry_count}/{max_retries})")
                await asyncio.sleep(wait_time)
            else:
                print("❌ Đã thử quá nhiều lần. Dừng bot.")
                break
        except Exception as e:
            retry_count += 1
            if retry_count < max_retries:
                wait_time = min(60, 2 ** retry_count)
                print(f"❌ LỖI: {e}")
                print(f"🔄 Thử lại sau {wait_time} giây... ({retry_count}/{max_retries})")
                await asyncio.sleep(wait_time)
            else:
                print("❌ Đã thử quá nhiều lần. Dừng bot.")
                break

if __name__ == "__main__":
    try:
        asyncio.run(run_bot_with_retry())
    except KeyboardInterrupt:
        print("\n👋 Bot đã được dừng bởi người dùng.")
