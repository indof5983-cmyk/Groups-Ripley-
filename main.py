import telebot

BOT_TOKEN = "8797454630:AAFq3ASZTAq7RYqZdVBXWl7HQ6eRCDjbUMo"
ADMIN_ID = 6009432844

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start(m):
    if m.chat.id != ADMIN_ID:
        bot.send_message(m.chat.id, '⛔ শুধু মালিক')
        return
    mk = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    mk.add('📩 রিপ্লাই')
    bot.send_message(m.chat.id, 'Welcome Boss', reply_markup=mk)

@bot.message_handler(func=lambda m: m.text == '📩 রিপ্লাই')
def step1(m):
    bot.send_message(m.chat.id, '📥 গ্রুপ থেকে যে ইউজারকে রিপ্লাই দিতে চান তার মেসেজ ফরওয়ার্ড করুন:')
    bot.register_next_step_handler(m, get_forward)

def get_forward(m):
    if m.forward_from or m.forward_from_chat:
        tid = m.forward_from.id if m.forward_from else m.forward_from_chat.id
        username = m.forward_from.username if m.forward_from else None
        gid = m.forward_from_chat.id if m.forward_from_chat else None
        
        if not gid:
            bot.send_message(m.chat.id, '❌ গ্রুপ থেকে ফরওয়ার্ড করুন! ব্যক্তিগত চ্যাট থেকে না।')
            return
        
        bot.send_message(m.chat.id, f'✍️ রিপ্লাই লিখুন:')
        bot.register_next_step_handler(m, send_reply, tid, username, gid)
    else:
        bot.send_message(m.chat.id, '❌ গ্রুপের মেসেজ ফরওয়ার্ড করুন!')
        bot.register_next_step_handler(m, get_forward)

def send_reply(m, tid, username, gid):
    try:
        if username:
            bot.send_message(gid, f'@{username}\n📩 {m.text}')
        else:
            bot.send_message(gid, f'ইউজার {tid}\n📩 {m.text}')
        bot.send_message(m.chat.id, '✅ পাঠানো হয়েছে!')
    except:
        bot.send_message(m.chat.id, '❌ ব্যর্থ! বট কি গ্রুপে অ্যাডমিন?')

print('✅ চালু...')
bot.infinity_polling()