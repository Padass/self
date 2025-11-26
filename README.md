# Self-Bot Discord Relay

Bot tự động phát hiện từ khóa trong tin nhắn và gửi phản hồi đến kênh đích.

## Tính năng

- Phát hiện từ khóa trong tin nhắn từ kênh nguồn
- Tự động gửi phản hồi đến kênh đích qua Discord API
- Hỗ trợ nhiều từ khóa tùy chỉnh

## Cài đặt

1. Cài đặt dependencies:
```bash
pip install -r requirements.txt
```

2. Tạo file cấu hình:
```bash
cp config.example.py config.py
```

3. Chỉnh sửa `config.py` và điền thông tin của bạn:
```python
USER_TOKEN = 'your_token_here'
CHANNEL_ID_NGUON = 123456789012345678
CHANNEL_ID_DICH = 987654321098765432
```

3. Chạy bot:
```bash
python relay.py
```

## Cấu hình

Chỉnh sửa `KEYWORD_RESPONSES` trong `relay.py` để thêm/sửa từ khóa và phản hồi.

## Lưu ý

- Không commit token lên GitHub
- Sử dụng user token (self-bot), không phải bot token
- Đảm bảo bot có quyền đọc tin nhắn trong kênh nguồn và gửi tin nhắn trong kênh đích

