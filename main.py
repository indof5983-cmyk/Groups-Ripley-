import telebot, sqlite3
from datetime import datetime

BOT_TOKEN = "8797454630:AAFq3ASZTAq7RYqZdVBXWl7HQ6eRCDjbUMo"
ADMIN_ID = 6009432844  # আপনার টেলিগ্রাম আইডি দিন

bot = telebot.TeleBot(BOT_TOKEN)

conn = sqlite3.connect('db.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS s(u_id INT PRIMARY KEY, t_id INT, step TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS r(id INTEGER PRIMARY KEY AUTOINCREMENT, f_id INT, t_id INT, msg TEXT, time TEXT)')
conn.commit()

def g_state(uid):
    r = c.execute('SELECT t_id, step FROM s WHERE u_id=?', (uid,)).fetchone()
    return {'t_id': r[0], 'step': r[1]} if r else None

def s_state(uid, tid=None, step=None):
    if tid is None and step is None:
        c.execute('DELETE FROM s WHERE u_id=?', (uid,))
    else:
        c.execute('INSERT OR REPLACE INTO s VALUES (?,?,?)', (uid, tid, step))
    conn.commit()

@bot.message_handler(commands=['start'])
def start(m):
    if m.chat.id != ADMIN_ID:
        bot.send_message(m.chat.id, '⛔ এই বট শুধু মালিকের জন্য!')
        return
    
    mk = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    mk.add('📩 Reply', '📊 Stats')
    bot.send_message(m.chat.id, f'Welcome Boss 👑\nআপনি রিপ্লাই দিতে পারবেন', reply_markup=mk)

@bot.message_handler(func=lambda m: m.text == '📩 Reply')
def reply(m):
    if m.chat.id != ADMIN_ID: return
    s_state(m.chat.id, step='fw')
    bot.send_message(m.chat.id, '📥 যে ইউজারকে রিপ্লাই দিতে চান তার যেকোনো মেসেজ ফরওয়ার্ড করুন:')

@bot.message_handler(func=lambda m: m.text == '📊 Stats')
def stats(m):
    if m.chat.id != ADMIN_ID: return
    s = c.execute('SELECT COUNT(*) FROM r WHERE f_id=?', (m.chat.id,)).fetchone()[0]
    f = c.execute('SELECT COUNT(*) FROM r WHERE f_id=? AND msg="FAILED"', (m.chat.id,)).fetchone()[0]
    bot.send_message(m.chat.id, f'📊 আপনার রিপ্লাই স্ট্যাটাস:\n✅ সফল: {s-f}\n❌ ব্যর্থ: {f}')

@bot.message_handler(func=lambda m: True)
def handle(m):
    if m.chat.id != ADMIN_ID: return
    
    s = g_state(m.chat.id)
    if not s: return
    
    if s['step'] == 'fw':
        if m.forward_from or m.forward_from_chat:
            tid = m.forward_from.id if m.forward_from else m.forward_from_chat.id
            if tid == m.chat.id:
                bot.send_message(m.chat.id, '❌ নিজেকে রিপ্লাই দিতে পারবেন না')
                s_state(m.chat.id)
                return
            s_state(m.chat.id, tid, 'reply')
            bot.send_message(m.chat.id, f'✍️ {tid} এই আইডিতে আপনার রিপ্লাই লিখুন:')
        else:
            bot.send_message(m.chat.id, '⚠️ দয়া করে একটি ফরওয়ার্ডেড মেসেজ পাঠান!')
    
    elif s['step'] == 'reply':
        try:
            bot.send_message(s['t_id'], f'📩 রিপ্লাই: {m.text}')
            bot.send_message(m.chat.id, f'✅ রিপ্লাই পাঠানো হয়েছে!')
            c.execute('INSERT INTO r (f_id,t_id,msg,time) VALUES (?,?,?,?)', (m.chat.id, s['t_id'], m.text, datetime.now()))
            conn.commit()
        except Exception as e:
            bot.send_message(m.chat.id, f'❌ ব্যর্থ! ইউজার বট স্টার্ট করেনি বা ব্লক করেছে।\nআইডি: {s["t_id"]}')
            c.execute('INSERT INTO r (f_id,t_id,msg,time) VALUES (?,?,?,?)', (m.chat.id, s['t_id'], 'FAILED', datetime.now()))
            conn.commit()
        s_state(m.chat.id)

print('✅ বট চালু আছে - শুধু মালিক ব্যবহার করতে পারবেন')
bot.infinity_polling()