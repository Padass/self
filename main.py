import discord
from discord.ext import commands
import requests
import os
from dotenv import load_dotenv

# Load biến môi trường từ file .env
load_dotenv()

# Đọc từ environment variables (ưu tiên) hoặc fallback về config.py
USER_TOKEN = os.getenv('USER_TOKEN')
CHANNEL_ID_NGUON_STR = os.getenv('CHANNEL_ID_NGUON')
CHANNEL_ID_DICH_STR = os.getenv('CHANNEL_ID_DICH')

# Chuyển đổi channel IDs sang int nếu có
CHANNEL_ID_NGUON = None
CHANNEL_ID_DICH = None

if CHANNEL_ID_NGUON_STR:
    try:
        CHANNEL_ID_NGUON = int(CHANNEL_ID_NGUON_STR)
    except (ValueError, TypeError):
        print(f"⚠️ Cảnh báo: CHANNEL_ID_NGUON không hợp lệ: {CHANNEL_ID_NGUON_STR}")

if CHANNEL_ID_DICH_STR:
    try:
        CHANNEL_ID_DICH = int(CHANNEL_ID_DICH_STR)
    except (ValueError, TypeError):
        print(f"⚠️ Cảnh báo: CHANNEL_ID_DICH không hợp lệ: {CHANNEL_ID_DICH_STR}")

# Fallback về config.py nếu không có trong environment variables
if not USER_TOKEN or not CHANNEL_ID_NGUON or not CHANNEL_ID_DICH:
    try:
        from config import USER_TOKEN as CFG_TOKEN, CHANNEL_ID_NGUON as CFG_NGUON, CHANNEL_ID_DICH as CFG_DICH
        if not USER_TOKEN:
            USER_TOKEN = CFG_TOKEN
            print("ℹ️ Đã sử dụng USER_TOKEN từ config.py")
        if not CHANNEL_ID_NGUON:
            CHANNEL_ID_NGUON = CFG_NGUON
            print("ℹ️ Đã sử dụng CHANNEL_ID_NGUON từ config.py")
        if not CHANNEL_ID_DICH:
            CHANNEL_ID_DICH = CFG_DICH
            print("ℹ️ Đã sử dụng CHANNEL_ID_DICH từ config.py")
    except ImportError:
        print("ℹ️ Không tìm thấy config.py, chỉ sử dụng environment variables")

# Kiểm tra token và channel IDs
if not USER_TOKEN:
    raise ValueError("USER_TOKEN không được tìm thấy! Vui lòng thêm USER_TOKEN vào Environment Variables trên Railway hoặc tạo file config.py")
if not CHANNEL_ID_NGUON:
    raise ValueError("CHANNEL_ID_NGUON không được tìm thấy! Vui lòng thêm CHANNEL_ID_NGUON vào Environment Variables trên Railway hoặc tạo file config.py")
if not CHANNEL_ID_DICH:
    raise ValueError("CHANNEL_ID_DICH không được tìm thấy! Vui lòng thêm CHANNEL_ID_DICH vào Environment Variables trên Railway hoặc tạo file config.py") 

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
    "dưa hấu": "Dưa hấu đang bán trong Shop!!",
    "bí ngô": "Bí ngô đang bán trong Shop!!",
    "xoài": "Xoài đang bán trong Shop!!",
    "táo đường": "Táo đường đang bán trong Shop!!",
    "đậu": "Đậu đang bán trong Shop!!",
    "khế": "Khế đang bán trong Shop!!",
    "vòi xanh": "Vòi Xanh đang bán trong Shop!!",
    "vòi đỏ": "Vòi Đỏ đang bán trong Shop!!",
}

# =========================================================
#             🛠️ CÁC HÀM XỬ LÝ
# =========================================================

client = discord.Client()

def gui_tin_nhan_qua_http(channel_id, content):
    """Gửi tin nhắn đến API Endpoint tùy chỉnh."""
    url = API_URL_GUI_TIN.format(channel_id=channel_id)
    data = {'content': content}
    
    try:
        response = requests.post(url, headers=HEADERS, json=data)
        if response.status_code == 200:
            print(f"✅ Gửi thành công tin nhắn tới kênh {channel_id}.")
        else:
            print(f"❌ Lỗi gửi tin {response.status_code}: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Lỗi kết nối HTTP khi gửi tin: {e}")

# =========================================================
#             🤖 LOGIC SELF-BOT
# =========================================================

@client.event
async def on_ready():
    print(f'Tài khoản tự động đã đăng nhập với tên: {client.user} (Self-Bot Activated)')

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
#             ▶️ KHỞI CHẠY BOT
# =========================================================

try:
    print("Đang khởi động Self-Bot...")
    # Chạy client với Token của người dùng
    client.run(USER_TOKEN) 
except discord.errors.LoginFailure:
    print("LỖI: Đăng nhập thất bại! Vui lòng kiểm tra lại USER_TOKEN và API URL.")
except Exception as e:
    print(f"LỖI KHÔNG XÁC ĐỊNH: {e}")