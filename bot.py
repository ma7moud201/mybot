from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)
import os

# ================== إعدادات ==================
TOKEN = os.getenv("TOKEN")   # ⬅️ مهم جداً
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

# ================== أدوات ==================
def get_users():
    if not os.path.exists(USERS_FILE):
        return []
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return sorted(set(u.strip() for u in f if u.strip()))

def is_approved(user_id: int) -> bool:
    return user_id == ADMIN_ID or str(user_id) in get_users()

def approve_user(user_id: int):
    if user_id == ADMIN_ID:
        return
    if str(user_id) not in get_users():
        with open(USERS_FILE, "a", encoding="utf-8") as f:
            f.write(f"{user_id}\n")

def remove_user(user_id: str):
    users = [u for u in get_users() if u != user_id]
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        for u in users:
            f.write(u + "\n")

# ================== كيبورد ==================
start_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
start_keyboard.add("ابدأ")

subjects_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
for s in subjects:
    subjects_keyboard.add(s)
subjects_keyboard.add("🔙 رجوع")

admin_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
admin_keyboard.add("ابدأ")
admin_keyboard.add("📊 إحصائية المستخدمين", "❌ حذف مستخدم")

# ================== START ==================
@dp.message_handler(commands=["start"])
async def start(message: types.Message):

    if message.from_user.id == ADMIN_ID:
        await message.answer("👑 لوحة تحكم الأدمن", reply_markup=admin_keyboard)
        return

    if not is_approved(message.from_user.id):
        kb = InlineKeyboardMarkup()
        kb.add(
            InlineKeyboardButton("✅ موافق", callback_data=f"approve_{message.from_user.id}"),
            InlineKeyboardButton("❌ رفض", callback_data=f"reject_{message.from_user.id}")
        )

        await bot.send_message(
            ADMIN_ID,
            f"📥 طلب دخول جديد\n\n"
            f"👤 الاسم: {message.from_user.full_name}\n"
            f"🆔 ID: {message.from_user.id}",
            reply_markup=kb
        )
        await message.answer("⏳ تم إرسال طلبك، انتظر الموافقة.")
        return

    await message.answer("نورت 👋", reply_markup=start_keyboard)

# ================== موافقة / رفض ==================
@dp.callback_query_handler(lambda c: c.data.startswith("approve_"))
async def approve(call: types.CallbackQuery):
    user_id = int(call.data.split("_")[1])
    approve_user(user_id)
    await bot.send_message(user_id, "✅ تمت الموافقة! أرسل /start")
    await call.message.edit_text("✅ تمت الموافقة")

@dp.callback_query_handler(lambda c: c.data.startswith("reject_"))
async def reject(call: types.CallbackQuery):
    user_id = int(call.data.split("_")[1])
    await bot.send_message(user_id, "❌ تم رفض طلبك.")
    await call.message.edit_text("❌ تم الرفض")

# ================== مواد ==================
@dp.message_handler(lambda m: m.text == "ابدأ")
async def show_subjects(message: types.Message):
    await message.answer("اختر المادة 📚", reply_markup=subjects_keyboard)

@dp.message_handler(lambda m: m.text == "🔙 رجوع")
async def back(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("لوحة الأدمن 👇", reply_markup=admin_keyboard)
    else:
        await message.answer("القائمة الرئيسية 👇", reply_markup=start_keyboard)

@dp.message_handler(lambda m: m.text in subjects)
async def send_files(message: types.Message):
    folder = os.path.join(SUBJECTS_DIR, message.text)

    if not os.path.exists(folder) or not os.listdir(folder):
        await message.answer("📭 لا يوجد ملفات.", reply_markup=subjects_keyboard)
        return

    for file in os.listdir(folder):
        path = os.path.join(folder, file)
        with open(path, "rb") as f:
            if file.lower().endswith(".pdf"):
                await message.answer_document(f)
            else:
                await message.answer_photo(f)

    await message.answer("⬅️ رجوع", reply_markup=subjects_keyboard)

# ================== إحصائيات ==================
@dp.message_handler(lambda m: m.from_user.id == ADMIN_ID and m.text == "📊 إحصائية المستخدمين")
async def stats(message: types.Message):
    users = get_users()
    text = f"👥 عدد المستخدمين: {len(users)}\n\n"
    for u in users:
        try:
            chat = await bot.get_chat(int(u))
            text += f"👤 {chat.full_name}\n🆔 {u}\n\n"
        except:
            text += f"🆔 {u}\n\n"
    await message.answer(text, reply_markup=admin_keyboard)

# ================== حذف مستخدم ==================
@dp.message_handler(lambda m: m.from_user.id == ADMIN_ID and m.text == "❌ حذف مستخدم")
async def ask_remove(message: types.Message):
    await message.answer("🆔 أرسل ID المستخدم للحذف:")

@dp.message_handler(lambda m: m.from_user.id == ADMIN_ID and m.text.isdigit())
async def confirm_remove(message: types.Message):
    user_id = message.text

    if user_id not in get_users():
        await message.answer("❌ المستخدم غير موجود", reply_markup=admin_keyboard)
        return

    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("✅ نعم احذف", callback_data=f"confirm_delete_{user_id}"),
        InlineKeyboardButton("❌ إلغاء", callback_data="cancel_delete")
    )

    await message.answer(f"⚠️ تأكيد حذف المستخدم\n🆔 {user_id}", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data.startswith("confirm_delete_"))
async def delete_confirmed(call: types.CallbackQuery):
    user_id = call.data.split("_")[-1]
    remove_user(user_id)
    await call.message.edit_text("✅ تم حذف المستخدم")
    await bot.send_message(ADMIN_ID, "لوحة الأدمن 👇", reply_markup=admin_keyboard)

@dp.callback_query_handler(lambda c: c.data == "cancel_delete")
async def delete_canceled(call: types.CallbackQuery):
    await call.message.edit_text("❌ تم إلغاء الحذف")
    await bot.send_message(ADMIN_ID, "لوحة الأدمن 👇", reply_markup=admin_keyboard)

# ================== تشغيل ==================
if __name__ == "__main__":
    executor.start_polling(dp)
