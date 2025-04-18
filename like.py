import time
import requests
import telebot
from telebot.types import Message

API_TOKEN = "7724806489:AAEHgJhUHwpsaXSjJUIwiG5NkkyNC2FB9U8"  # <- Thay bằng token bot của bạn
bot = telebot.TeleBot(API_TOKEN)

# dict lưu user_id và thời gian cuối cùng gọi lệnh
user_last_like_time = {}

# thời gian chờ (giây)
LIKE_COOLDOWN = 5

@bot.message_handler(commands=['like'])
def like_handler(message: Message):
    user_id = message.from_user.id
    current_time = time.time()

    last_time = user_last_like_time.get(user_id, 0)
    time_diff = current_time - last_time

    if time_diff < LIKE_COOLDOWN:
        wait_time = int(LIKE_COOLDOWN - time_diff)
        bot.reply_to(message, f"<blockquote>⏳ Vui lòng chờ {wait_time} giây trước khi dùng lại lệnh này.</blockquote>", parse_mode="HTML")
        return

    user_last_like_time[user_id] = current_time  # cập nhật thời gian sử dụng

    command_parts = message.text.split()  
    if len(command_parts) != 2:  
        bot.reply_to(message, "<blockquote>like 1733997441</blockquote>", parse_mode="HTML")  
        return  

    idgame = command_parts[1]  
    urllike = f"https://dichvukey.site/likeff2.php?key=vlong&uid={idgame}"  

    def safe_get(data, key):
        value = data.get(key)
        return value if value not in [None, ""] else "Không xác định"

    def extract_number(text):
        if not text:
            return "Không xác định"
        for part in text.split():
            if part.isdigit():
                return part
        return "Không xác định"

    loading_msg = bot.reply_to(message, "<blockquote>⏳ Đang tiến hành buff like...</blockquote>", parse_mode="HTML")

    try:
        response = requests.get(urllike, timeout=15)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException:
        bot.edit_message_text("<blockquote>Server đang quá tải, vui lòng thử lại sau.</blockquote>",
                              chat_id=loading_msg.chat.id, message_id=loading_msg.message_id, parse_mode="HTML")
        return
    except ValueError:
        bot.edit_message_text("<blockquote>Phản hồi từ server không hợp lệ.</blockquote>",
                              chat_id=loading_msg.chat.id, message_id=loading_msg.message_id, parse_mode="HTML")
        return

    status_code = data.get("status")

    reply_text = (
        "<blockquote>"
        "BUFF LIKE THÀNH CÔNG✅\n"
        f"╭👤 Name: {safe_get(data, 'PlayerNickname')}\n"
        f"├🆔 UID : {safe_get(data, 'uid')}\n"
        f"├🌏 Region : vn\n"
        f"├📉 Like trước đó: {safe_get(data, 'likes_before')}\n"
        f"├📈 Like sau khi gửi: {safe_get(data, 'likes_after')}\n"
        f"╰👍 Like được gửi: {extract_number(data.get('likes_given'))}"
    )

    if status_code == 2:
        reply_text += "\n⚠️ Giới hạn like hôm nay, mai hãy thử lại sau."

    reply_text += "</blockquote>"

    bot.edit_message_text(reply_text, chat_id=loading_msg.chat.id, message_id=loading_msg.message_id, parse_mode="HTML")

# Khởi động bot
if __name__ == '__main__':
    print("Bot đang chạy...")
    bot.infinity_polling()
