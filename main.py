import telebot
import re

BOT_TOKEN = "8797454630:AAFq3ASZTAq7RYqZdVBXWl7HQ6eRCDjbUMo"
ADMIN_ID = 6009432844

bot = telebot.TeleBot(BOT_TOKEN)

# অপেক্ষারত ডাটা স্টোর করার জন্য
user_link = {}

@bot.message_handler(commands=['start'])
def start(m):
    if m.chat.id != ADMIN_ID:
        bot.send_message(m.chat.id, "⛔ শুধু মালিক।")
        return
    bot.send_message(m.chat.id, "✅ বট চালু আছে।\n\nশুধু গ্রুপ পোস্টের লিংক পাঠান।")

@bot.message_handler(func=lambda m: m.chat.id == ADMIN_ID and 't.me/' in m.text)
def get_link(m):
    link = m.text.strip()
    
    # লিংক থেকে গ্রুপের ইউজারনেম বের করা
    match = re.search(r"t\.me/([^/]+)/(\d+)", link)
    if match:
        group_username = match.group(1)
        post_id = match.group(2)
        
        # ইউজারের ডাটা সেভ করুন
        user_link[m.chat.id] = {"group": f"@{group_username}", "post_id": post_id}
        bot.send_message(m.chat.id, "✍️ এই পোস্টের নিচে কী জবাব দিতে চান? (আপনার মেসেস লিখুন)")
    else:
        bot.send_message(m.chat.id, "❌ ভুল লিংক। সঠিক গ্রুপ পোস্টের লিংক দিন।")

@bot.message_handler(func=lambda m: m.chat.id == ADMIN_ID and m.chat.id in user_link)
def send_reply(m):
    data = user_link[m.chat.id]
    group = data["group"]
    post_id = data["post_id"]
    reply_text = m.text
    
    try:
        # লিংক ব্যবহার করে নির্দিষ্ট পোস্টে রিপ্লাই দেওয়া
        bot.send_message(group, f"➡️ [জবাব](https://t.me/{group[1:]}/{post_id})\n\n{reply_text}", parse_mode="Markdown")
        bot.send_message(m.chat.id, f"✅ সফল! আপনার জবাব **{group}** গ্রুপে দেওয়া হয়েছে।")
        # সেশন মুছে দিন
        del user_link[m.chat.id]
    except Exception as e:
        bot.send_message(m.chat.id, f"❌ ব্যর্থ! কারণ: {str(e)}")

# ইউজার যদি অন্য কোনো এলোমেলো মেসেজ দেয়
@bot.message_handler(func=lambda m: m.chat.id == ADMIN_ID)
def fallback(m):
    if m.chat.id in user_link:
        # আগের ধাপে রিপ্লাই এর জন্য অপেক্ষা করছি, উপরের ফাংশন handle করবে
        pass
    else:
        bot.send_message(m.chat.id, "🔗 দয়া করে একটি গ্রুপ পোস্টের লিংক পাঠান (যেমন: https://t.me/your_group/123)")

print("✅ বট চালু আছে। এখন শুধু পোস্টের লিংক দিন।")
bot.infinity_polling()