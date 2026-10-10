import os
import re
import uuid
from datetime import datetime, timedelta
from urllib.parse import urlparse, unquote, quote

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from xray_api import add_vless_user


TOKEN = os.getenv("BOT_TOKEN")

LAB_URL = "https://www.cloudskillsboost.google/focuses/20774?parent=catalog"

PUBLIC_HOST = os.getenv("PUBLIC_HOST")

WS_PATH = os.getenv(
    "WS_PATH",
    "Télégram/@MOHAMaaaaal/@VLessVMessTroja"
)


START_TEXT = f"""آلُـۜسـۨۚ(✋)ــِۖلُأمٌ ؏ـليۜـ(💜)ـكـۜم وݛحـٍّْـٍّْ⁽😘₎ـٍّْمهہ الًـًٍۖـٍـٍۖ(☝)ٍۖـًٍٍٍّـًٍلۖهًٍۖۂ وبـۗـۗـۗـۗـۗـۗركۧۧــۧۧۧۧۧـۗـۗ(ۗ😇)ـۗـۗاتهۂ

ملاحظة: رابط المختبر تحتاجه، إما أن تحفظه أو ترسل /start.

ه‌‌َـَْـُذآ رابط المختبر:
المدة: 4:30 ساعات
{LAB_URL}

﷽
۝ إِنَّ اللَّهَ وَمَلائِكَتَهُ يُصَلُّونَ عَلَى
النَّبِيِّ يَا أَيُّهَا الَّذِينَ آمَنُوا صَلُّوا
عَلَيْهِ وَسَلِّمُوا تَسْلِيمًا ۝ ﷺ♥

_._._._._._._._._._._._._._._._._._._._._._._._._._._._._._._._._._._._._._._._._._._

𝙒𝙚𝙡𝙘𝙤𝙢𝙚 𝙢𝙮 𝙛𝙧𝙞𝙚𝙣𝙙𝙨, 𝙩𝙝𝙞𝙨 𝙞𝙨 𝙖 𝙂𝙤𝙤𝙜𝙡𝙚𝘾𝙡𝙤𝙪𝙙 𝙘𝙤𝙙𝙚𝙨 𝙜𝙚𝙣𝙚𝙧𝙖𝙩𝙤𝙧
"""


def extract_project_id(text: str):
    text = unquote(text)

    match = re.search(
        r"[?&]project=(qwiklabs-[a-z0-9-]+)",
        text,
        re.IGNORECASE,
    )

    if match:
        return match.group(1)

    return None


def is_google_url(text: str):
    try:
        parsed = urlparse(text)
        host = (parsed.hostname or "").lower()

        return (
            parsed.scheme in ("https", "http")
            and host in {
                "skills.google",
                "www.skills.google",
                "cloudskillsboost.google",
                "www.cloudskillsboost.google",
                "console.cloud.google.com",
            }
        )
    except Exception:
        return False


def make_vless_link(user_uuid: str, days: int):
    if not PUBLIC_HOST:
        return None

    host = PUBLIC_HOST.strip().removeprefix("https://").removeprefix("http://").rstrip("/")
    encoded_path = quote("/" + WS_PATH.strip("/"), safe="")

    return (
        f"vless://{user_uuid}@{host}:443"
        f"?encryption=none"
        f"&security=tls"
        f"&type=ws"
        f"&host={host}"
        f"&path={encoded_path}"
        f"#VLESS-{days}DAY"
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton(
                "📎 إرسال رابط المختبر",
                callback_data="send_lab",
            )
        ],
        [
            InlineKeyboardButton(
                "📊 حالة الخدمة",
                callback_data="status",
            )
        ],
    ]

    await update.effective_message.reply_text(
        START_TEXT,
        reply_markup=InlineKeyboardMarkup(keyboard),
        disable_web_page_preview=True,
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text(
        "🎥 شرح استخدام البوت\n\n"
        "1️⃣ أرسل رابط Google Skills Boost.\n"
        "2️⃣ سيحاول البوت استخراج Project ID.\n"
        "3️⃣ إذا كان الرابط مناسبًا والخادم مهيأ، سيحاول إنشاء حساب VLESS.\n\n"
        "⚠️ لا ترسل كلمة مرور أو توكن."
    )


async def send_lab(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        "📎 أرسل رابط Google Skills Boost.\n\n"
        "سيحاول البوت استخراج Project ID من الرابط."
    )


async def receive_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    text = (message.text or "").strip()

    if not is_google_url(text):
        await message.reply_text(
            "❌ أرسل رابط Google Skills Boost أو Google Cloud صالحًا."
        )
        return

    project_id = extract_project_id(text)

    if not project_id:
        await message.reply_text(
            "⚠️ لم أجد Project ID بصيغة qwiklabs- في الرابط."
        )
        return

    context.user_data["project_id"] = project_id

    await message.reply_text("⏳ جاري محاولة إنشاء حساب VLESS...")

    user_uuid = str(uuid.uuid4())
    email = f"tg_{update.effective_user.id}_{user_uuid[:8]}"

    try:
        result = add_vless_user(user_uuid, email)
    except Exception:
        await message.reply_text(
            "❌ حدث خطأ أثناء الاتصال بخادم Xray. "
            "تحقق من إعدادات الخادم وسجلات التشغيل."
        )
        return

    if not result:
        await message.reply_text(
            "❌ لم يتمكن البوت من إضافة الحساب إلى خادم Xray."
        )
        return

    days = 1
    expiry = datetime.now() + timedelta(days=days)

    vless_link = make_vless_link(user_uuid, days)

    if not vless_link:
        await message.reply_text(
            "⚠️ تمت إضافة الحساب، لكن PUBLIC_HOST غير مضبوط. "
            "اضبط عنوان الخادم قبل إنشاء رابط الاتصال."
        )
        return

    await message.reply_text(
        "✅ تمت إضافة حساب VLESS إلى Xray.\n\n"
        f"☁️ Project ID:\n{project_id}\n\n"
        f"🆔 UUID:\n{user_uuid}\n\n"
        f"⏳ المدة المعروضة: {days} يوم\n"
        f"📅 الوقت المحسوب للانتهاء: "
        f"{expiry.strftime('%Y-%m-%d %H:%M')}\n\n"
        "رابط الاتصال:\n"
        f"{vless_link}",
        disable_web_page_preview=True,
    )


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    if query:
        await query.answer()
        await query.edit_message_text(
            "📊 البوت متصل بتيليجرام.\n"
            "هذه الرسالة لا تؤكد أن اتصال Xray يعمل."
        )
    else:
        await update.effective_message.reply_text(
            "📊 البوت متصل بتيليجرام.\n"
            "هذه الرسالة لا تؤكد أن اتصال Xray يعمل."
        )


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.effective_message.reply_text("✅ تم إلغاء العملية.")


def main():
    if not TOKEN:
        raise RuntimeError("متغير BOT_TOKEN غير مضبوط.")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("cancel", cancel))
    app.add_handler(CommandHandler("status", status))

    app.add_handler(
        CallbackQueryHandler(send_lab, pattern="^send_lab$")
    )
    app.add_handler(
        CallbackQueryHandler(status, pattern="^status$")
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            receive_link,
        )
    )

    print("Telegram bot is starting...")
    app.run_polling()


if __name__ == "__main__":
    main()