import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

# ================== إعدادات ==================
TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise RuntimeError("TOKEN not found")

ADMIN_ID = 1188982651

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SUBJECTS_DIR = os.path.join(BASE_DIR, "subjects")
USERS_FILE = os.path.join(BASE_DIR, "users.txt")

subjects = [
    "أساسيات التمريض عملي",
    "أساسيات التمريض نظري",
    "الأحياء الدقيقة",
    "التخدير والإنعاش عملي 1",
    "التخدير والإنعاش نظري 1",
    "التشريح 1 عملي",
    "التشريح 1 نظري",
    "المصطلحات الطبية",
    "فيزيولوجيا 1",
    "معدات التخدير عملي",
    "معدات التخدير نظري",
    "مهارات التواصل"
]

# ================== أدوات المستخدمين ==================
def get_users():
    if not os.path.exists(USERS_FILE):
        return []
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return [u.strip() for u in f if u.strip()]

def approve_user(uid):
    if str(uid) not in get_users():
        with open(USERS_FILE, "a", encoding="utf-8") as f:
            f.write(str(uid) + "\n")

def remove_user(uid):
    users = [u for u in get_users() if u != str(uid)]
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(users))

def is_approved(uid):
    return uid == ADMIN_ID or str(uid) in get_users()

# ================== الكيبورد ==================
start_kb = ReplyKeyboardMarkup(resize_keyboard=True)
start_kb.add("ابدأ")

subjects_kb = ReplyKeyboardMarkup(resize_keyboard=True)
for s in subjects:
    subjects_kb.add(s)
subjects_kb.add("🔙 رجوع")

admin_kb = ReplyKeyboardMarkup(resize_keyboard=True)
admin_kb.add("ابدأ")
admin_kb.add("📊 إحصائيات", "❌ حذف مستخدم")

# ================== START ==================
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("👑 لوحة الأدمن", reply_markup=admin_kb)
        return

    if not is_approved(message.from_user.id):
        kb = InlineKeyboardMarkup()
        kb.add(
            InlineKeyboardButton("✅ موافقة", callback_data=f"approve_{message.from_user.id}"),
            InlineKeyboardButton("❌ رفض", callback_data=f"reject_{message.from_user.id}")
        )
        await bot.send_message(
            ADMIN_ID,
            f"طلب دخول جديد\n👤 {message.from_user.full_name}\n🆔 {message.from_user.id}",
            reply_markup=kb
        )
        await message.answer("⏳ بانتظار الموافقة")
        return

    await message.answer("أهلاً 👋", reply_markup=start_kb)

# ================== موافقة ==================
@dp.callback_query_handler(lambda c: c.data.startswith("approve_"))
async def approve(call: types.CallbackQuery):
    uid = int(call.data.split("_")[1])
    approve_user(uid)
    await bot.send_message(uid, "✅ تمت الموافقة، أرسل /start")
    await call.message.edit_text("✅ تمت الموافقة")

@dp.callback_query_handler(lambda c: c.data.startswith("reject_"))
async def reject(call: types.CallbackQuery):
    uid = int(call.data.split("_")[1])
    await bot.send_message(uid, "❌ تم رفض طلبك")
    await call.message.edit_text("❌ تم الرفض")

# ================== عرض المواد ==================
@dp.message_handler(lambda m: m.text == "ابدأ")
async def show_subjects(message: types.Message):
    await message.answer("اختر المادة 📚", reply_markup=subjects_kb)

# ================== إرسال ملفات المادة (المهم) ==================
@dp.message_handler(lambda m: m.text in subjects)
async def send_subject_files(message: types.Message):
    folder = os.path.join(SUBJECTS_DIR, message.text)

    if not os.path.exists(folder):
        await message.answer("❌ لا يوجد ملفات لهذه المادة")
        return

    files = os.listdir(folder)
    if not files:
        await message.answer("📂 المجلد فارغ")
        return

    for file in files:
        path = os.path.join(folder, file)
        with open(path, "rb") as f:
            await message.answer_document(f)

# ================== زر الرجوع ==================
@dp.message_handler(lambda m: m.text == "🔙 رجوع")
async def back(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("👑 لوحة الأدمن", reply_markup=admin_kb)
    else:
        await message.answer("🏠 القائمة الرئيسية", reply_markup=start_kb)

# ================== إحصائيات ==================
@dp.message_handler(lambda m: m.from_user.id == ADMIN_ID and m.text == "📊 إحصائيات")
async def stats(message: types.Message):
    users = get_users()
    text = f"👥 العدد: {len(users)}\n\n"

    for u in users:
        try:
            chat = await bot.get_chat(int(u))
            text += f"👤 {chat.full_name}\n🆔 {u}\n\n"
        except:
            text += f"🆔 {u}\n\n"

    await message.answer(text, reply_markup=admin_kb)

# ================== حذف مستخدم ==================
@dp.message_handler(lambda m: m.from_user.id == ADMIN_ID and m.text == "❌ حذف مستخدم")
async def ask_id(message: types.Message):
    await message.answer("أرسل ID المستخدم")

@dp.message_handler(lambda m: m.from_user.id == ADMIN_ID and m.text.isdigit())
async def delete_user_handler(message: types.Message):
    remove_user(message.text)
    await message.answer("✅ تم الحذف", reply_markup=admin_kb)

# ================== سيرفر Render ==================
class Dummy(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

def run_server():
    port = int(os.environ.get("PORT", 10000))
    HTTPServer(("0.0.0.0", port), Dummy).serve_forever()

threading.Thread(target=run_server, daemon=True).start()

# ================== تشغيل ==================
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
