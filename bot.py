import os
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

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "👋 مرحباً بك\n\n"
        "🤖 بوت إدارة VLESS\n\n"
        "اختر العملية التي تريدها:",
        reply_markup=reply_markup
    )


async def create_vless(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        "➕ إنشاء حساب VLESS\n\n"
        "⚠️ الزر يعمل بنجاح.\n\n"
        "لكن لم يتم ربط خادم Xray/VLESS بعد.\n"
        "سيتم إضافة إنشاء الحساب الحقيقي في الخطوة التالية."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        CallbackQueryHandler(create_vless, pattern="^create_vless$")
    )

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()