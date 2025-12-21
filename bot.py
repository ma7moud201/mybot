from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# ================== الإعدادات ==================
TOKEN = os.environ.get("8283739227:AAH5TuALFuTeqHI422jzJm-81orkIVR2NLY")   # التوكن من Render Environment Variables
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

# ================== دوال المستخدمين ==================
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
    users = [u for u in get_users() if u != str(user_id)]
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        for u in users:
            f.write(u + "\n")

# ================== الكيبورد ==================
start_kb = ReplyKeyboardMarkup(resize_keyboard=True)
start_kb.add("ابدأ")

subjects_kb = ReplyKeyboardMarkup(resize_keyboard=True)
for s in subjects:
    subjects_kb.add(s)
subjects_kb.add("🔙 رجوع")

admin_kb = ReplyKeyboardMarkup(resize_keyboard=True)
admin_kb.add("ابدأ")
admin_kb.add("📊 إحصائية المستخدمين", "❌ حذف مستخدم")

# ================== /start ==================
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
            f"📥 طلب دخول جديد\n\n👤 {message.from_user.full_name}\n🆔 {message.from_user.id}",
            reply_markup=kb
        )

        await message.answer("⏳ تم إرسال طلبك، بانتظار موافقة الأدمن")
        return

    await message.answer("أهلاً 👋", reply_markup=start_kb)

# ================== موافقة ==================
@dp.callback_query_handler(lambda c: c.data.startswith("approve_"))
async def approve(call: types.CallbackQuery):

    if call.from_user.id != ADMIN_ID:
        await call.answer("❌ هذا الزر للأدمن فقط", show_alert=True)
        return

    uid = int(call.data.split("_")[1])
    approve_user(uid)

    await bot.send_message(uid, "✅ تمت الموافقة، أرسل /start")

    try:
        await call.message.edit_text("✅ تمت الموافقة")
    except:
        pass

# ================== رفض ==================
@dp.callback_query_handler(lambda c: c.data.startswith("reject_"))
async def reject(call: types.CallbackQuery):

    if call.from_user.id != ADMIN_ID:
        await call.answer("❌ هذا الزر للأدمن فقط", show_alert=True)
        return

    uid = int(call.data.s
