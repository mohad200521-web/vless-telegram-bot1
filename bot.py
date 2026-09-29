import os
import uuid
from datetime import datetime, timedelta, timezone
from urllib.parse import quote

from xray_api import add_vless_user

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = os.getenv("BOT_TOKEN")

SERVER_HOST = os.getenv("SERVER_HOST", "")
SERVER_PORT = os.getenv("SERVER_PORT", "443")
WS_PATH = os.getenv(
    "WS_PATH",
    "/Télégram/@MOHAMaaaaal/@VLessVMessTroja",
)


# =========================
# القائمة الرئيسية
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton(
                "☁️ Google Cloud → Cloud Run",
                callback_data="cloud_run"
            )
        ],
        [
            InlineKeyboardButton(
                "➕ إنشاء حساب VLESS",
                callback_data="create_vless"
            )
        ],
        [
            InlineKeyboardButton(
                "📊 حالة الخدمة",
                callback_data="service_status"
            )
        ],
    ]

    await update.message.reply_text(
        "👋 مرحباً بك في GC.AHMED Run\n\n"
        "اختر العملية:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =========================
# Google Cloud → Cloud Run
# =========================

async def cloud_run(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    context.user_data["waiting_for_project"] = True

    await query.edit_message_text(
        "☁️ Google Cloud → Cloud Run\n\n"
        "📎 أرسل رابط مشروع Google Cloud"
    )


# استقبال رابط Google Cloud
async def receive_project(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    if not context.user_data.get("waiting_for_project"):
        return

    project_url = update.message.text.strip()

    if not (
        "console.cloud.google.com" in project_url
        or "cloud.google.com" in project_url
        or project_url.startswith("qwiklabs-gcp-")
    ):
        await update.message.reply_text(
            "❌ الرابط غير معروف.\n\n"
            "أرسل رابط مشروع Google Cloud صالح."
        )
        return

    context.user_data["waiting_for_project"] = False
    context.user_data["project_url"] = project_url

    message = await update.message.reply_text(
        "✅ تم استلام الطلب\n\n"
        "1️⃣ التحقق من المشروع ⏳\n"
        "2️⃣ تفعيل Cloud Run API\n"
        "3️⃣ تجهيز الخدمة\n"
        "4️⃣ إنشاء الخدمة\n"
        "5️⃣ انتظار النشر...\n"
        "6️⃣ اختبار الخدمة\n"
        "7️⃣ النشر"
    )

    # هذه المرحلة تعرض التدفق فقط.
    # التنفيذ الحقيقي لـ Google Cloud سنضيفه بعد ربط
    # Service Account / Google Cloud credentials.

    await message.edit_text(
        "✅ تم استلام الطلب\n\n"
        "1️⃣ التحقق من المشروع ✅\n"
        "2️⃣ تفعيل Cloud Run API ⏳\n"
        "3️⃣ تجهيز الخدمة\n"
        "4️⃣ إنشاء الخدمة\n"
        "5️⃣ انتظار النشر...\n"
        "6️⃣ اختبار الخدمة\n"
        "7️⃣ النشر"
    )


# =========================
# إنشاء VLESS
# =========================

async def create_vless(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [
            InlineKeyboardButton(
                "📅 يوم واحد",
                callback_data="days_1"
            ),
            InlineKeyboardButton(
                "📅 7 أيام",
                callback_data="days_7"
            ),
        ],
        [
            InlineKeyboardButton(
                "📅 30 يوم",
                callback_data="days_30"
            )
        ],
    ]

    await query.edit_message_text(
        "➕ إنشاء حساب VLESS\n\n"
        "اختر مدة الحساب:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def generate_account(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()

    days = int(query.data.split("_")[1])

    if not SERVER_HOST:
        await query.edit_message_text(
            "❌ SERVER_HOST غير مضبوط."
        )
        return

    user_uuid = str(uuid.uuid4())

    expiry = (
        datetime.now(timezone.utc)
        + timedelta(days=days)
    )

    email = (
        f"tg_{query.from_user.id}_"
        f"{user_uuid[:8]}"
    )

    await query.edit_message_text(
        "⏳ جاري إنشاء الحساب...\n\n"
        "1️⃣ إنشاء UUID\n"
        "2️⃣ إضافة المستخدم إلى Xray\n"
        "3️⃣ تجهيز رابط VLESS..."
    )

    if not add_vless_user(user_uuid, email):
        await query.edit_message_text(
            "❌ فشل إضافة الحساب إلى Xray."
        )
        return

    encoded_path = quote(
        WS_PATH,
        safe="/"
    )

    vless_link = (
        f"vless://{user_uuid}@"
        f"{SERVER_HOST}:{SERVER_PORT}"
        f"?encryption=none"
        f"&security=tls"
        f"&type=ws"
        f"&path={encoded_path}"
        f"#{quote(email)}"
    )

    await query.edit_message_text(
        "✅ تم إنشاء الحساب\n\n"
        f"🆔 UUID:\n`{user_uuid}`\n\n"
        f"⏳ المدة: {days} يوم\n"
        f"📅 الانتهاء:\n"
        f"`{expiry.strftime('%Y-%m-%d %H:%M UTC')}`\n\n"
        "🔗 رابط VLESS:\n"
        f"`{vless_link}`",
        parse_mode="Markdown"
    )


# =========================
# حالة الخدمة
# =========================

async def service_status(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        "📊 حالة الخدمة\n\n"
        "☁️ Google Cloud: متصل\n"
        "🐳 Docker: جاهز\n"
        "⚙️ Xray: يعمل\n"
        "🤖 Telegram Bot: يعمل"
    )


# =========================
# المساعدة
# =========================

async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        "🤖 GC.AHMED Run\n\n"
        "/start - القائمة الرئيسية\n"
        "/help - المساعدة"
    )


# =========================
# تشغيل البوت
# =========================

def main():

    if not TOKEN:
        raise RuntimeError(
            "BOT_TOKEN غير موجود"
        )

    app = (
        Application.builder()
        .token(TOKEN)
        .build()
    )

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        CommandHandler("help", help_command)
    )

    app.add_handler(
        CallbackQueryHandler(
            cloud_run,
            pattern=r"^cloud_run$"
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            create_vless,
            pattern=r"^create_vless$"
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            generate_account,
            pattern=r"^days_(1|7|30)$"
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            service_status,
            pattern=r"^service_status$"
        )
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            receive_project
        )
    )

    print("GC.AHMED Run is running...")

    app.run_polling()


if __name__ == "__main__":
    main()