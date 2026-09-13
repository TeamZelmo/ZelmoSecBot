"""
Force-Subscribe Telegram Bot
-----------------------------
Kaam:
1. Group me jab koi UNVERIFIED user message kare:
      - uska message DELETE ho jata hai
      - use group me MUTE (restrict) kar diya jata hai
      - group me sirf ek chhota sa message aata hai: "{user}, aap verified
        nahi ho" + ek "✅ Verify Karein" button jo user ko BOT KE DM
        (private chat) me le jata hai
2. DM me bot sabhi required channels ki join-links bhejta hai, saath me
   ek "✅ Maine Join Kar Liya" button
3. Jab user DM me sab join karke us button ko dabata hai:
      - bot dobara membership check karta hai
      - agar sab join ho gaye → us group me user ko UNMUTE kar diya jata hai
      - agar kuch baaki hai → DM me bata diya jata hai kaunse channels baaki hain

Zaroori: Bot ko GROUP me aur SABHI CHANNELS me ADMIN banana hoga
(taaki wo membership check kar sake, message delete kar sake, aur mute/unmute kar sake).
Bot ka Privacy Mode BotFather me OFF hona chahiye (taaki wo group ke sabhi
messages dekh sake), aur DM start hone ke liye user ne kabhi na kabhi bot ko
block na kiya ho.
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


def build_group_verify_keyboard(group_id: int):
    """Group me dikhne wala button — dabate hi bot ke DM me le jata hai."""
    deep_link = f"https://t.me/{config.BOT_USERNAME}?start=verify_{group_id}"
    buttons = [[InlineKeyboardButton(text="✅ Verify Karein", url=deep_link)]]
    return InlineKeyboardMarkup(buttons)


def build_dm_join_keyboard(not_joined_channels, group_id: int):
    """DM me dikhne wale channel-join buttons + check button."""
    buttons = [
        [InlineKeyboardButton(text=f"📢 Join {ch['title']}", url=ch["link"])]
        for ch in not_joined_channels
    ]
    buttons.append(
        [InlineKeyboardButton(text="✅ Maine Join Kar Liya", callback_data=f"check_join:{group_id}")]
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

        # 3) Group me sirf ek chhota warning + "Verify Karein" button
        #    (jo user ko bot ke DM me le jayega)
        text = (
            f"👋 {user.mention_html()}, main tum verified nahi ho।\n"
            f"Neeche button dabakar verify karein।"
        )
        await context.bot.send_message(
            chat_id=chat.id,
            text=text,
            parse_mode="HTML",
            reply_markup=build_group_verify_keyboard(chat.id),
        )


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /start command handler.
    - Normal /start -> intro message
    - /start verify_<group_id> (deep link se) -> DM me channel list bhejo
    """
    args = context.args
    user = update.effective_user

    if args and args[0].startswith("verify_"):
        try:
            group_id = int(args[0].split("verify_", 1)[1])
        except (ValueError, IndexError):
            await update.message.reply_text("⚠️ Invalid verification link.")
            return

        not_joined = await get_not_joined_channels(context, user.id)

        if not not_joined:
            # User pehle se hi sab channels me joined hai -> turant unmute
            try:
                await unmute_user(context, group_id, user.id)
            except Exception as e:
                logger.warning(f"Unmute fail: {e}")
            await update.message.reply_text(
                "✅ Aap pehle se hi sabhi channels me joined hain! "
                "Ab aap group me message bhej sakte hain."
            )
            return

        text = (
            "🔒 Group me message bhejne ke liye pehle neeche diye gaye "
            "sabhi channels join karein।\n\n"
            "Sab join karne ke baad <b>'✅ Maine Join Kar Liya'</b> button dabayein।"
        )
        await update.message.reply_text(
            text,
            parse_mode="HTML",
            reply_markup=build_dm_join_keyboard(not_joined, group_id),
        )
        return

    # Normal /start (bina kisi deep link ke)
    await update.message.reply_text(
        "Namaste! Yeh Force-Subscribe bot hai. Mujhe group me admin banayein "
        "aur sabhi required channels me bhi admin banayein taaki main kaam kar sakoon."
    )


async def handle_check_join_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Jab user DM me '✅ Maine Join Kar Liya' button dabata hai."""
    query = update.callback_query
    user = query.from_user

    # callback_data format: "check_join:<group_id>"
    try:
        group_id = int(query.data.split(":", 1)[1])
    except (IndexError, ValueError):
        await query.answer("⚠️ Kuch galat ho gaya, dobara koshish karein।", show_alert=True)
        return

    await query.answer()  # loading spinner hatane ke liye

    not_joined = await get_not_joined_channels(context, user.id)

    if not_joined:
        await query.answer(
            "❌ Aap abhi bhi kuch channels me join nahi hain. Pehle sab join karein।",
            show_alert=True,
        )
        # Buttons ko refresh kar do (updated list ke saath)
        try:
            await query.edit_message_reply_markup(
                reply_markup=build_dm_join_keyboard(not_joined, group_id)
            )
        except Exception:
            pass
        return

    # Sab channels join ho chuke hain -> group me unmute
    try:
        await unmute_user(context, group_id, user.id)
    except Exception as e:
        logger.warning(f"Unmute fail: {e}")

    try:
        await query.edit_message_text(
            text="✅ Shabash! Aap sabhi channels me joined hain। "
                 "Ab aap group me message bhej sakte hain।",
        )
    except Exception:
        await context.bot.send_message(
            chat_id=user.id,
            text="✅ Ab aap group me message bhej sakte hain।",
        )

    # Optional: group me bhi ek chhota confirmation bhej sakte hain
    try:
        await context.bot.send_message(
            chat_id=group_id,
            text=f"✅ {user.mention_html()} ab verified hain aur message bhej sakte hain।",
            parse_mode="HTML",
        )
    except Exception:
        pass


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
