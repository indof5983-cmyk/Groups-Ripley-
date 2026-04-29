import telebot

BOT_TOKEN = "8797454630:AAFq3ASZTAq7RYqZdVBXWl7HQ6eRCDjbUMo"
bot = telebot.TeleBot(BOT_TOKEN)

user_state = {}

@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📩 Reply System")
    bot.send_message(message.chat.id, "Welcome brother 😎\nChoose option:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "📩 Reply System")
def reply_option(message):
    user_state[message.chat.id] = "waiting_forward"
    bot.send_message(message.chat.id, "📥 Forward the message you want to reply to:")

@bot.message_handler(func=lambda message: user_state.get(message.chat.id) == "waiting_forward")
def get_forward(message):
    if message.forward_from or message.forward_from_chat:
        user_state[message.chat.id] = {
            "step": "waiting_reply",
            "target_id": message.forward_from.id if message.forward_from else message.forward_from_chat.id
        }
        bot.send_message(message.chat.id, "✍️ Now send your reply message:")
    else:
        bot.send_message(message.chat.id, "⚠️ Please forward a valid message!")

@bot.message_handler(func=lambda message: isinstance(user_state.get(message.chat.id), dict))
def send_reply(message):
    data = user_state.get(message.chat.id)

    if data["step"] == "waiting_reply":
        target_id = data["target_id"]
        try:
            bot.send_message(target_id, message.text)
            bot.send_message(message.chat.id, "✅ Reply sent successfully!")
        except:
            bot.send_message(message.chat.id, "❌ Failed to send reply!")

        user_state.pop(message.chat.id)

bot.polling()