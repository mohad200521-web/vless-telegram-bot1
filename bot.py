# bot.py

import os
import re
from urllib.parse import urlparse, unquote

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = os.getenv("BOT_TOKEN")

LAB_URL = "https://www.cloudskillsboost.google/focuses/20774?parent=catalog"

START_TEXT = f"""آلُـۜسـۨۚ(✋)ــِۖلُأمٌ ؏ـليۜـ(💜)ـكـۜم وݛحـٍّْـٍّْ⁽😘₎ـٍّْمهہ الًـًٍۖـٍـٍۖ(☝)ٍۖـًٍٍٍّـًٍلۖهًٍۖۂ وبـۗـۗـۗـۗـۗـۗركۧۧــۧۧۧۧۧـۗـۗ(ۗ😇)ـۗـۗاتهۂ

ملاحظة : رابط المختبر تحتاجه لهذا يا اما تحفظه او ترسل /start

ه‌‌َـَْـُذآ رابط المختبر :
4:30 ساعات
[] ° {LAB_URL}

﷽
۝ إِنَّ اللَّهَ وَمَلائِكَتَهُ يُصَلُّونَ عَلَى
النَّبِيِّ يَا أَيُّهَا الَّذِينَ آمَنُوا صَلُّوا
عَلَيْهِ وَسَلِّمُوا تَسْلِيمًا ۝ ﷺ♥

_._._._._._._._._._._._._._._._._._._._._._._._._._._._._._._._._._._._._._._._._._._

𝙒𝙚𝙡𝙘𝙤𝙢𝙚 𝙢𝙮 𝙛𝙧𝙞𝙚𝙣𝙙𝙨 , 𝙩𝙝𝙞𝙨 𝙞𝙨 𝙖 𝙂𝙤𝙤𝙜𝙡𝙚𝘾𝙡𝙤𝙪𝙙 𝙘𝙤𝙙𝙚𝙨 𝙜𝙚𝙣𝙚𝙧𝙖𝙩𝙤𝙧

, 𝙮𝙤𝙪 𝙣𝙚𝙚𝙙 𝙩𝙤 𝙨𝙚𝙣𝙙 ( /help ) 𝙘𝙤𝙢𝙢𝙖𝙣𝙙 , 𝙩𝙤 𝙜𝙚𝙩 2 𝙫𝙞𝙙𝙚𝙤𝙨 𝙩𝙝𝙖𝙩 𝙚𝙭𝙥𝙡𝙖𝙞𝙣s 𝙚𝙫𝙚𝙧𝙮𝙩𝙝𝙞𝙣𝙜

𝙏𝙝𝙞𝙨 𝙞𝙨 𝙩𝙝𝙚 𝙡𝙖𝙗𝙤𝙧𝙖𝙩𝙤𝙧𝙮 𝙡𝙞𝙣𝙠 :
4:30 𝙝𝙤𝙪𝙧𝙨
[] ° {LAB_URL}
@MOHAMaaaaal"""


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
        host = urlparse(text).netloc.lower()

        return host in {
            "skills.google",
            "www.skills.google",
            "cloudskillsboost.google",
            "www.cloudskillsboost.google",
            "console.cloud.google.com",
        }

    except Exception:
        return False


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [
            InlineKeyboardButton(
                "📎 إرسال رابط المختبر",
                
        [
            
        [
            InlineKeyboardButton(
                "📊 حالة الخدمة",
                callback_data="status"
            )
        ],
    ]

    await update.message.reply_text(
        START_TEXT,
        reply_markup=InlineKeyboardMarkup(keyboard),
        disable_web_page_preview=True,
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "🎥 شرح استخدام البوت\n\n"
        "أرسل رابط Google Skills Boost إلى البوت.\n\n"
        "⚠️ لا ترسل كلمة مرور أو رمز تسجيل دخول أو token."
    )


async def send_lab(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        "📎 أرسل رابط Google Skills Boost.\n\n"
        "سيتم استخراج Project ID فقط."
    )


async def receive_link(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text.strip()

    if not is_google_url(text):
        await update.message.reply_text(
            "❌ أرسل رابط Google Skills Boost أو Google Cloud صالحًا."
        )
        return

    project_id = extract_project_id(text)

    if not project_id:
        await update.message.reply_text(
            "⚠️ لم أجد Project ID في الرابط."
        )
        return

    context.user_data["project_id"] = project_id

    keyboard = [
        [
            InlineKeyboardButton(
                "➕ إنشاء VLESS",
                callback_data="create_vless"
            )
        ],
        [
            InlineKeyboardButton(
                "📊 حالة الخدمة",
                callback_data="status"
            )
        ],
    ]

    await update.message.reply_text(
        "✅ تم استلام الرابط\n\n"
        f"☁️ Project ID:\n{project_id}\n\n"
        "🔐 تم استخدام Project ID فقط.",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def create_vless(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    project_id = context.user_data.get("project_id")

    if not project_id:
        await query.edit_message_text(
            "❌ أرسل رابط المختبر أولًا."
        )
        return

    await query.edit_message_text(
        "⚙️ تجهيز الخدمة...\n\n"
        f"☁️ Project ID:\n{project_id}\n\n"
        "⏳ يحتاج النشر الفعلي إلى Google Cloud credentials "
        "مصرح بها للمشروع."
    )


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    project_id = context.user_data.get("project_id")

    if not project_id:
        await query.edit_message_text(
            "📊 لا يوجد مشروع مرتبط."
        )
        return

    await query.edit_message_text(
        "📊 حالة الخدمة\n\n"
        f"☁️ Project ID:\n{project_id}\n\n"
        "🟡 تم استلام المشروع\n"
        "⚪ لم يتم النشر الفعلي بعد"
    )


def main():

    if not TOKEN:
        raise RuntimeError("BOT_TOKEN غير موجود")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))

    app.add_handler(
        CallbackQueryHandler(
            send_lab,
            pattern="^send_lab$"
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            create_vless,
            pattern="^create_vless$"
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            status,
            pattern="^status$"
        )
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            receive_link
        )
    )

    print("Bot is running...")

    app.run_polling()


if __name__ == "__main__":
    main()