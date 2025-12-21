from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
import os

TOKEN = "8283739227:AAH5TuALFuTeqHI422jzJm-81orkIVR2NLY"   # 🔴 حط توكنك هنا
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

def get_users():
    if not os.path.exists(USERS_FILE):
        return []
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return [u.strip() for u in f if u.strip()]

def is_approved(user_id):
    return user_id == ADMIN_ID or str(user_id) in get_users()

def approve_user(user_id):
    if str(user_id) not in get_users():
        with open(USERS_FILE, "a", encoding="utf-8") as f:
            f.write(str(user_id) + "\n")

def remove_user(user_id):
    users = [u for u in get_users() if u != user_id]
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        for u in users:
            f.write(u + "\n")

start_kb = ReplyKeyboardMarkup(resize_keyboard=True)
start_kb.add("ابدأ")

subjects_kb = ReplyKeyboardMarkup(resize_keyboard=True)
for s in subjects:
    subjects_kb.add(s)
subjects_kb.add("🔙 رجوع")

admin_kb = ReplyKeyboardMarkup(resize_keyboard=True)
admin_kb.add("ابدأ")
admin_kb.add("📊 إحصائية المستخدمين", "❌ حذف مستخدم")

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("👑 لوحة الأدمن", reply_markup=admin_kb)
        return

    if not is_approved(message.from_user.id):
        kb = InlineKeyboardMarkup()
        kb.add(
            InlineKeyboardButton("✅ موافق", callback_data=f"approve_{message.from_user.id}"),
            InlineKeyboardButton("❌ رفض", callback_data=f"reject_{message.from_user.id}")
        )
        await bot.send_message(
            ADMIN_ID,
            f"طلب دخول\n{message.from_user.full_name}\n{message.from_user.id}",
            reply_markup=kb
        )
        await message.answer("⏳ بانتظار الموافقة")
        return

    await message.answer("أهلاً 👋", reply_markup=start_kb)

@dp.callback_query_handler(lambda c: c.data.startswith("approve_"))
async def approve(call: types.CallbackQuery):
    uid = call.data.split("_")[1]
    approve_user(uid)
    await bot.send_message(uid, "✅ تمت الموافقة، أرسل /start")
    await call.message.edit_text("تمت الموافقة")

@dp.callback_query_handler(lambda c: c.data.startswith("reject_"))
async def reject(call: types.CallbackQuery):
    uid = call.data.split("_")[1]
    await bot.send_message(uid, "❌ تم الرفض")
    await call.message.edit_text("تم الرفض")

@dp.message_handler(lambda m: m.text == "ابدأ")
async def show_subjects(message: types.Message):
    await message.answer("اختر مادة 📚", reply_markup=subjects_kb)

@dp.message_handler(lambda m: m.text in subjects)
async def send_files(message: types.Message):
    folder = os.path.join(SUBJECTS_DIR, message.text)
    if not os.path.exists(folder):
        await message.answer("لا يوجد ملفات")
        return

    for file in os.listdir(folder):
        with open(os.path.join(folder, file), "rb") as f:
            await message.answer_document(f)

@dp.message_handler(lambda m: m.text == "📊 إحصائية المستخدمين" and m.from_user.id == ADMIN_ID)
async def stats(message: types.Message):
    users = get_users()
    await message.answer(f"عدد المستخدمين: {len(users)}", reply_markup=admin_kb)

@dp.message_handler(lambda m: m.text == "❌ حذف مستخدم" and m.from_user.id == ADMIN_ID)
async def ask_delete(message: types.Message):
    await message.answer("أرسل ID")

@dp.message_handler(lambda m: m.text.isdigit() and m.from_user.id == ADMIN_ID)
async def delete_user(message: types.Message):
    remove_user(message.text)
    await message.answer("تم الحذف", reply_markup=admin_kb)

if __name__ == "__main__":
    executor.start_polling(dp)
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import os

class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

def run_dummy_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), DummyHandler)
    server.serve_forever()

threading.Thread(target=run_dummy_server, daemon=True).start()
