"""
Force-Subscribe Telegram Bot
-----------------------------
Kaam:
1. Group me jab koi user message kare, bot check karta hai ki wo user
   config me diye gaye SABHI channels me joined hai ya nahi.
2. Agar joined NAHI hai:
      - user ka message DELETE ho jata hai
      - user ko group me MUTE (restrict) kar diya jata hai
      - use ek message aata hai jisme sabhi channels ke "Join" buttons
        aur ek "✅ Maine Join Kar Liya" button hota hai
3. Jab user sabhi channels join karke "✅ Maine Join Kar Liya" dabata hai:
      - bot dobara check karta hai
      - agar sab join ho gaye → user UNMUTE ho jata hai
      - agar abhi bhi kuch channel baaki hai → bot bata deta hai kaunse baaki hain

Zaroori: Bot ko GROUP me aur SABHI CHANNELS me ADMIN banana hoga
(taaki wo membership check kar sake, message delete kar sake, aur mute/unmute kar sake).
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatPermissions
from telegram.ext import (
    Application,
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    CallbackQueryHandler,
    CommandHandler,
    filters,
)

import config

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# ---------- HELPER FUNCTIONS ----------

async def get_not_joined_channels(context: ContextTypes.DEFAULT_TYPE, user_id: int):
    """Return list of channels (from config) jinme user NAHI joined hai."""
    not_joined = []
    for channel in config.CHANNELS:
        try:
            member = await context.bot.get_chat_member(chat_id=channel["id"], user_id=user_id)
            if member.status not in ("member", "administrator", "creator"):
                not_joined.append(channel)
        except Exception as e:
            # Agar bot us channel me admin nahi hai ya user kabhi wahan aaya hi nahi
            logger.warning(f"Channel {channel['id']} check fail for user {user_id}: {e}")
            not_joined.append(channel)
    return not_joined


def build_join_keyboard(not_joined_channels):
    buttons = [
        [InlineKeyboardButton(text=f"📢 Join {ch['title']}", url=ch["link"])]
        for ch in not_joined_channels
    ]
    buttons.append(
        [InlineKeyboardButton(text="✅ Maine Join Kar Liya", callback_data="check_join")]
    )
    return InlineKeyboardMarkup(buttons)


async def mute_user(context: ContextTypes.DEFAULT_TYPE, chat_id: int, user_id: int):
    await context.bot.restrict_chat_member(
        chat_id=chat_id,
        user_id=user_id,
        permissions=ChatPermissions(can_send_messages=False),
    )


async def unmute_user(context: ContextTypes.DEFAULT_TYPE, chat_id: int, user_id: int):
    await context.bot.restrict_chat_member(
        chat_id=chat_id,
        user_id=user_id,
        permissions=ChatPermissions(
            can_send_messages=True,
            can_send_audios=True,
            can_send_documents=True,
            can_send_photos=True,
            can_send_videos=True,
            can_send_video_notes=True,
            can_send_voice_notes=True,
            can_send_polls=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True,
            can_change_info=False,
            can_invite_users=True,
            can_pin_messages=False,
        ),
    )


# ---------- HANDLERS ----------

async def handle_group_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Har naye group message par membership check karta hai."""
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat

    if user is None or message is None:
        return

    # Group admins ko skip karna chahein to yahan check add kar sakte hain (optional)

    not_joined = await get_not_joined_channels(context, user.id)

    if not_joined:
        # 1) Message delete
        try:
            await message.delete()
        except Exception as e:
            logger.warning(f"Message delete fail: {e}")

        # 2) User ko mute karo
        try:
            await mute_user(context, chat.id, user.id)
        except Exception as e:
            logger.warning(f"Mute fail: {e}")

        # 3) Warning + join buttons bhejo
        text = (
            f"👋 {user.mention_html()}, aapka message isliye delete kar diya gaya "
            f"kyunki aap humare sabhi channels me join nahi hain.\n\n"
            f"Neeche diye gaye sabhi channels join karein, phir "
            f"<b>'✅ Maine Join Kar Liya'</b> button dabayein taaki aap dobara "
            f"message bhej sakein."
        )
        await context.bot.send_message(
            chat_id=chat.id,
            text=text,
            parse_mode="HTML",
            reply_markup=build_join_keyboard(not_joined),
        )


async def handle_check_join_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Jab user '✅ Maine Join Kar Liya' button dabata hai."""
    query = update.callback_query
    user = query.from_user
    chat = query.message.chat

    await query.answer()  # loading spinner hatane ke liye

    not_joined = await get_not_joined_channels(context, user.id)

    if not_joined:
        await query.answer(
            "❌ Aap abhi bhi kuch channels me join nahi hain. Pehle sab join karein.",
            show_alert=True,
        )
        # Buttons ko refresh kar do (updated list ke saath)
        try:
            await query.edit_message_reply_markup(reply_markup=build_join_keyboard(not_joined))
        except Exception:
            pass
        return

    # Sab channels join ho chuke hain -> unmute
    try:
        await unmute_user(context, chat.id, user.id)
    except Exception as e:
        logger.warning(f"Unmute fail: {e}")

    try:
        await query.edit_message_text(
            text=f"✅ Shabash {user.mention_html()}! Aap sabhi channels me joined hain. "
                 f"Ab aap group me message bhej sakte hain.",
            parse_mode="HTML",
        )
    except Exception:
        await context.bot.send_message(
            chat_id=chat.id,
            text=f"✅ {user.mention_html()} ab group me message bhej sakte hain.",
            parse_mode="HTML",
        )


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Namaste! Yeh Force-Subscribe bot hai. Mujhe group me admin banayein "
        "aur sabhi required channels me bhi admin banayein taaki main kaam kar sakoon."
    )


# ---------- MAIN ----------

def main():
    app: Application = ApplicationBuilder().token(config.BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))

    # Group ke andar text/media messages ke liye
    app.add_handler(
        MessageHandler(
            filters.ChatType.GROUPS & (~filters.STATUS_UPDATE),
            handle_group_message,
        )
    )

    app.add_handler(CallbackQueryHandler(handle_check_join_button, pattern="^check_join$"))

    logger.info("Bot start ho gaya hai...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
