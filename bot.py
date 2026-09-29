import os
import uuid
from datetime import datetime, timedelta

from xray_api import add_vless_user

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

TOKEN = os.getenv("BOT_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton(
                "➕ إنشاء حساب VLESS",
                callback_data="create_vless"
            )
        ]
    ]

    await update.message.reply_text(
        "👋 مرحباً بك\n\n"
        "🤖 بوت إدارة VLESS\n\n"
        "اختر العملية التي تريدها:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def create_vless(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [
            InlineKeyboardButton("📅 يوم واحد", callback_data="days_1"),
            InlineKeyboardButton("📅 7 أيام", callback_data="days_7"),
        ],
        [
            InlineKeyboardButton("📅 30 يوم", callback_data="days_30"),
        ]
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

    user_uuid = str(uuid.uuid4())
    expiry = datetime.now() + timedelta(days=days)

    email = f"tg_{query.from_user.id}_{user_uuid[:8]}"

    success = add_vless_user(user_uuid, email)

    if not success:
        await query.edit_message_text(
            "❌ حدث خطأ أثناء إضافة الحساب إلى خادم Xray."
        )
        return

    await query.edit_message_text(
        "✅ تم إنشاء حساب VLESS\n\n"
        f"🆔 UUID:\n"
        f"`{user_uuid}`\n\n"
        f"⏳ المدة: {days} يوم\n"
        f"📅 الانتهاء: "
        f"{expiry.strftime('%Y-%m-%d %H:%M')}\n\n"
        "✅ تم إضافة الحساب إلى خادم Xray.",
        parse_mode="Markdown"
    )


async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        "/start - تشغيل البوت\n"
        "/help - المساعدة"
    )


def main():
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN غير موجود")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))

    app.add_handler(
        CallbackQueryHandler(
            create_vless,
            pattern="^create_vless$"
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            generate_account,
            pattern="^days_(1|7|30)$"
        )
    )

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()