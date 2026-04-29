import telebot, sqlite3
from datetime import datetime

BOT_TOKEN = "8797454630:AAFq3ASZTAq7RYqZdVBXWl7HQ6eRCDjbUMo"
ADMIN_ID = 6009432844

bot = telebot.TeleBot(BOT_TOKEN)

conn = sqlite3.connect('db.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS s(u_id INT PRIMARY KEY, t_id INT, step TEXT, group_id INT)')
conn.commit()

def g_state(uid):
    r = c.execute('SELECT t_id, step, group_id FROM s WHERE u_id=?', (uid,)).fetchone()
    return {'t_id': r[0], 'step': r[1], 'group_id': r[2]} if r else None

def s_state(uid, tid=None, step=None, gid=None):
    if tid is None and step is None and gid is None:
        c.execute('DELETE FROM s WHERE u_id=?', (uid,))
    else:
        c.execute('INSERT OR REPLACE INTO s VALUES (?,?,?,?)', (uid, tid, step, gid))
    conn.commit()

@bot.message_handler(commands=['start'])
def start(m):
    if m.chat.id != ADMIN_ID:
        bot.send_message(m.chat.id, '⛔ শুধু মালিক ব্যবহার করতে পারবেন')
        return
    
    mk = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    mk.add('📩 গ্রুপে রিপ্লাই', '📊 স্ট্যাটাস')
    bot.send_message(m.chat.id, f'Welcome Boss 👑\nবট যেই গ্রুপে আছে সেখানেই রিপ্লাই যাবে', reply_markup=mk)

@bot.message_handler(func=lambda m: m.text == '📩 গ্রুপে রিপ্লাই')
def reply(m):
    if m.chat.id != ADMIN_ID: return
    s_state(m.chat.id, step='fw')
    bot.send_message(m.chat.id, '📥 যে ইউজারকে মেনশন করে রিপ্লাই দিতে চান তার মেসেজ ফরওয়ার্ড করুন:\n\nবট যেই গ্রুপে আছে সেখানেই রিপ্লাই পাঠানো হবে')

@bot.message_handler(func=lambda m: m.text == '📊 স্ট্যাটাস')
def stats(m):
    if m.chat.id != ADMIN_ID: return
    bot.send_message(m.chat.id, f'✅ বট চালু আছে\n📢 বট যেসব গ্রুপে আছে:')
    # বট যেসব গ্রুপে আছে দেখাবে
    for chat in bot.get_chat_member:
        pass

@bot.message_handler(func=lambda m: True)
def handle(m):
    if m.chat.id != ADMIN_ID: return
    
    s = g_state(m.chat.id)
    if not s: return
    
    if s['step'] == 'fw':
        if m.forward_from or m.forward_from_chat:
            tid = m.forward_from.id if m.forward_from else m.forward_from_chat.id
            username = m.forward_from.username if m.forward_from else None
            
            # বট কোন গ্রুপে মেসেজ পেয়েছে সেটা সেভ করা
            group_id = m.chat.id if m.chat.type in ['group', 'supergroup'] else None
            
            s_state(m.chat.id, tid, 'reply', group_id)
            
            if username:
                bot.send_message(m.chat.id, f'✍️ @{username} (আইডি: {tid}) কে রিপ্লাই লিখুন:\n(এই গ্রুপেই মেসেজ যাবে)')
            else:
                bot.send_message(m.chat.id, f'✍️ আইডি: {tid} এই ইউজারকে রিপ্লাই লিখুন:')
        else:
            bot.send_message(m.chat.id, '⚠️ একটি ফরওয়ার্ডেড মেসেজ পাঠান!\n\nগ্রুপ থেকে যেকোনো ইউজারের মেসেজ ফরওয়ার্ড করুন')
    
    elif s['step'] == 'reply':
        tid = s['t_id']
        group_id = s['group_id']
        
        # ইউজারনেম বের করা
        username = None
        try:
            chat = bot.get_chat(tid)
            username = chat.username
        except:
            pass
        
        # যেই গ্রুপ থেকে ফরওয়ার্ড করেছিল সেখানেই মেসেজ পাঠানো
        if group_id:
            try:
                if username:
                    bot.send_message(group_id, f'@{username}\n📩 রিপ্লাই: {m.text}')
                else:
                    bot.send_message(group_id, f'ইউজার আইডি: {tid}\n📩 রিপ্লাই: {m.text}')
                
                bot.send_message(m.chat.id, f'✅ গ্রুপে রিপ্লাই পাঠানো হয়েছে!')
            except Exception as e:
                bot.send_message(m.chat.id, f'❌ গ্রুপে পাঠানো ব্যর্থ!\nনিশ্চিত করুন বটটি ঐ গ্রুপে আছে কিনা')
        else:
            bot.send_message(m.chat.id, f'❌ গ্রুপ আইডি পাওয়া যায়নি!\nগ্রুপ থেকে মেসেজ ফরওয়ার্ড করুন')
        
        s_state(m.chat.id)

print('✅ বট চালু আছে')
print('📌 বটকে যেকোনো গ্রুপে এড করুন')
print('📌 গ্রুপ থেকে যেকোনো ইউজারের মেসেজ ফরওয়ার্ড করুন')
print('📌 আপনার রিপ্লাই সেই গ্রুপেই যাবে')
bot.infinity_polling()