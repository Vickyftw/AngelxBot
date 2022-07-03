import html
import importlib
import json
import re
import time
import traceback
from sys import argv
from typing import Optional

from telegram import (
    Chat,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    ParseMode,
    Update,
    User,
)
from telegram.error import (
    BadRequest,
    ChatMigrated,
    NetworkError,
    TelegramError,
    TimedOut,
    Unauthorized,
)
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    Filters,
    MessageHandler,
)
from telegram.ext.dispatcher import DispatcherHandlerStop, run_async
from telegram.utils.helpers import escape_markdown

from Angel import (
    ALLOW_EXCL,
    BL_CHATS,
    CERT_PATH,
    DONATION_LINK,
    LOGGER,
    OWNER_ID,
    PORT,
    SUPPORT_CHAT,
    TOKEN,
    URL,
    WEBHOOK,
    WHITELIST_CHATS,
    StartTime,
    dispatcher,
    pbot,
    telethn,
    updater,
)

# needed to dynamically load modules
# NOTE: Module order is not guaranteed, specify that in the config file!
from Angel.modules import ALL_MODULES
from Angel.modules.helper_funcs.alternate import typing_action
from Angel.modules.helper_funcs.chat_status import is_user_admin
from Angel.modules.helper_funcs.misc import paginate_modules
from Angel.modules.helper_funcs.readable_time import get_readable_time

PM_START_TEXT = """
👋 ʜᴇʏ ᴛʜᴇʀᴇ, ᴍʏ ɴᴀᴍᴇ ɪs 🍃 ⏤͟͞🇲ɪss𖧷➺🇦ɴɢᴇʟ ✘ 「🇮🇳」. 
➥ɪ'ᴍ ᴀ ᴘᴏᴡᴇʀꜰᴜʟʟ ɢʀᴏᴜᴘ ᴍᴀɴᴀɢᴇʀ ʙᴏᴛ🏄‍♀️ ᴡɪᴛʜ ᴄᴏᴏʟ ᴍᴏᴅᴜʟᴇs. ꜰᴇᴇʟ ꜰʀᴇᴇ ᴛᴏ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘs!  🍓
"""

buttons = [
    [
        InlineKeyboardButton(
            text="ᴀɴɢᴇʟ ɴᴇᴡs🛰♂️", url="https://t.me/angelxupdates"
        ),
        InlineKeyboardButton(
            text="ᴍᴏɪ ʜᴇᴀᴠᴇɴ 🏝", url="https://t.me/NatsukiSupport_Official"
        ),
    ],
    [
        InlineKeyboardButton(
            text="sᴏᴜʀᴄᴇ 🆓", url="https://github.com/Vickyftw/Miss-Angel-Group-Manager"
        ),
        InlineKeyboardButton(
            text="🔻 ʜᴇʟᴘ ᴍᴇɴᴜ 🔻", callback_data="help_back"
        ),
    ],
    [
        InlineKeyboardButton(
            text="❄️ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴘ ʙᴀʙᴇ ❄️",
            url="t.me/AngelxRobot?startgroup=true",
        ),
    ],
]

ANGEL_IMG = "https://telegra.ph/file/60ee9c876eb643440e29a.png"

HELP_STRINGS = f"""
*Main Commands :* [❤️‍🩹](https://telegra.ph/file/60ee9c876eb643440e29a.png)

ᴀɴɢᴇʟ ✘ ʀᴏʙᴏ   ᴇxᴄʟᴜsɪᴠᴇ ꜰᴇᴀᴛᴜʀᴇs
» ᴄʜᴇᴄᴋᴏᴜᴛ ᴀʟʟ ᴛʜᴇ ᴄᴏᴍᴍᴀɴᴅs
» ᴀʟʟ ᴏꜰ ᴍʏ ᴄᴏᴍᴍᴀɴᴅs ᴄᴀɴ ʙᴇ ᴜsᴇᴅ ᴡɪᴛʜ / ᴏʀ !
» ɪꜰ ʏᴏᴜ ɢᴏᴛ ᴀɴʏ ɪssᴜᴇ ᴏʀ ʙᴜɢ ɪɴ ᴀɴʏ ᴄᴏᴍᴍᴀɴᴅ ᴘʟᴇᴀsᴇ ʀᴇᴘᴏʀᴛ ɪᴛ ᴛᴏ @angelsupports

ㅤㅤㅤㅤㅤㅤ 𐎓✗ ᴍᴀɪɴ ᴄᴏᴍᴍᴀɴᴅꜱ

➲ /start : ꜱᴛᴀʀᴛꜱ ᴍᴇ | ᴀᴄᴄᴏʀᴅɪɴɢ ᴛᴏ ᴍᴇ ʏᴏᴜ'ᴠᴇ ᴀʟʀᴇᴀᴅʏ ᴅᴏɴᴇ ɪᴛ .
➲ /donate : sᴜᴘᴘᴏʀᴛ ᴍᴇ ʙʏ ᴅᴏɴᴀᴛɪɴɢ ꜰᴏʀ ᴍʏ ʜᴀʀᴅᴡᴏʀᴋ .
➲ /help  : ᴀᴠᴀɪʟᴀʙʟᴇ ᴄᴏᴍᴍᴀɴᴅꜱ ꜱᴇᴄᴛɪᴏɴ.
  ‣ ɪɴ ᴘᴍ : ᴡɪʟʟ ꜱᴇɴᴅ ʏᴏᴜ ʜᴇʟᴘ  ꜰᴏʀ ᴀʟʟ ꜱᴜᴘᴘᴏʀᴛᴇᴅ ᴍᴏᴅᴜʟᴇꜱ.
  ‣ ɪɴ ɢʀᴏᴜᴘ : ᴡɪʟʟ ʀᴇᴅɪʀᴇᴄᴛ ʏᴏᴜ ᴛᴏ ᴘᴍ, ᴡɪᴛʜ ᴀʟʟ ᴛʜᴀᴛ ʜᴇʟᴘ  ᴍᴏᴅᴜʟᴇꜱ.
""".format(
    dispatcher.bot.first_name,
    "" if not ALLOW_EXCL else "\nAll commands can either be used with / or !.\n",
)


DONATE_STRING = """Heya, glad to hear you want to donate!
You can donate to the original writer's of the Base code,
Support them  [ᴠɪᴄᴋʏ ✗  ꜰᴛᴡ](t.me/IM_V1CKY)"""

IMPORTED = {}
MIGRATEABLE = []
HELPABLE = {}
STATS = []
USER_INFO = []
USER_BOOK = []
DATA_IMPORT = []
DATA_EXPORT = []

CHAT_SETTINGS = {}
USER_SETTINGS = {}

GDPR = []

for module_name in ALL_MODULES:
    imported_module = importlib.import_module("Angel.modules." + module_name)
    if not hasattr(imported_module, "__mod_name__"):
        imported_module.__mod_name__ = imported_module.__name__

    if not imported_module.__mod_name__.lower() in IMPORTED:
        IMPORTED[imported_module.__mod_name__.lower()] = imported_module
    else:
        raise Exception("Can't have two modules with the same name! Please change one")

    if hasattr(imported_module, "__help__") and imported_module.__help__:
        HELPABLE[imported_module.__mod_name__.lower()] = imported_module

    # Chats to migrate on chat_migrated events
    if hasattr(imported_module, "__migrate__"):
        MIGRATEABLE.append(imported_module)

    if hasattr(imported_module, "__stats__"):
        STATS.append(imported_module)

    if hasattr(imported_module, "__gdpr__"):
        GDPR.append(imported_module)

    if hasattr(imported_module, "__user_info__"):
        USER_INFO.append(imported_module)

    if hasattr(imported_module, "__user_book__"):
        USER_BOOK.append(imported_module)

    if hasattr(imported_module, "__import_data__"):
        DATA_IMPORT.append(imported_module)

    if hasattr(imported_module, "__export_data__"):
        DATA_EXPORT.append(imported_module)

    if hasattr(imported_module, "__chat_settings__"):
        CHAT_SETTINGS[imported_module.__mod_name__.lower()] = imported_module

    if hasattr(imported_module, "__user_settings__"):
        USER_SETTINGS[imported_module.__mod_name__.lower()] = imported_module


# do not async
def send_help(chat_id, text, keyboard=None):
    if not keyboard:
        keyboard = InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help"))
    dispatcher.bot.send_message(
        chat_id=chat_id, text=text, parse_mode=ParseMode.MARKDOWN, reply_markup=keyboard
    )


@run_async
def test(update, context):
    try:
        print(update)
    except:
        pass
    update.effective_message.reply_text(
        "Hola tester! _I_ *have* `markdown`", parse_mode=ParseMode.MARKDOWN
    )
    update.effective_message.reply_text("This person edited a message")
    print(update.effective_message)


@run_async
def start(update: Update, context: CallbackContext):
    args = context.args
    uptime = get_readable_time((time.time() - StartTime))
    if update.effective_chat.type == "private":
        if len(args) >= 1:
            if args[0].lower() == "help":
                send_help(update.effective_chat.id, HELP_STRINGS)
            elif args[0].lower().startswith("ghelp_"):
                mod = args[0].lower().split("_", 1)[1]
                if not HELPABLE.get(mod, False):
                    return
                send_help(
                    update.effective_chat.id,
                    HELPABLE[mod].__help__,
                    InlineKeyboardMarkup(
                        [[InlineKeyboardButton(text="˹ʙᴀᴄᴋ ˼", callback_data="help_back")]]
                    ),
                )

            elif args[0].lower().startswith("stngs_"):
                match = re.match("stngs_(.*)", args[0].lower())
                chat = dispatcher.bot.getChat(match.group(1))

                if is_user_admin(chat, update.effective_user.id):
                    send_settings(match.group(1), update.effective_user.id, False)
                else:
                    send_settings(match.group(1), update.effective_user.id, True)

            elif args[0][1:].isdigit() and "rules" in IMPORTED:
                IMPORTED["rules"].send_rules(update, args[0], from_pm=True)

        else:
            update.effective_user.first_name
            update.effective_message.reply_text(
                PM_START_TEXT,
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=ParseMode.MARKDOWN,
                timeout=60,
            )
    else:
        update.effective_message.reply_text(
            "ɪ'ᴍ ᴀᴡᴀᴋᴇ ᴀʟʀᴇᴀᴅʏ! 🍂⚡️\n<b>➥ʜᴀᴠᴇɴ'ᴛ sʟᴇᴘᴛ sɪɴᴄᴇ 🥴:</b> <code>{}</code>".format(
                uptime
            ),
            parse_mode=ParseMode.HTML,
        )


def error_handler(update, context):
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    LOGGER.error(msg="Exception while handling an update:", exc_info=context.error)

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(
        None, context.error, context.error.__traceback__
    )
    tb = "".join(tb_list)

    # Build the message with some markup and additional information about what happened.
    message = (
        "An exception was raised while handling an update\n"
        "<pre>update = {}</pre>\n\n"
        "<pre>{}</pre>"
    ).format(
        html.escape(json.dumps(update.to_dict(), indent=2, ensure_ascii=False)),
        html.escape(tb),
    )

    if len(message) >= 4096:
        message = message[:4096]
    # Finally, send the message
    context.bot.send_message(chat_id=OWNER_ID, text=message, parse_mode=ParseMode.HTML)


# for test purposes
def error_callback(update: Update, context: CallbackContext):
    error = context.error
    try:
        raise error
    except Unauthorized:
        print("no nono1")
        print(error)
        # remove update.message.chat_id from conversation list
    except BadRequest:
        print("no nono2")
        print("BadRequest caught")
        print(error)

        # handle malformed requests - read more below!
    except TimedOut:
        print("no nono3")
        # handle slow connection problems
    except NetworkError:
        print("no nono4")
        # handle other connection problems
    except ChatMigrated as err:
        print("no nono5")
        print(err)
        # the chat_id of a group has changed, use e.new_chat_id instead
    except TelegramError:
        print(error)
        # handle all other telegram related errors


@run_async
def help_button(update, context):
    query = update.callback_query
    mod_match = re.match(r"help_module\((.+?)\)", query.data)
    prev_match = re.match(r"help_prev\((.+?)\)", query.data)
    next_match = re.match(r"help_next\((.+?)\)", query.data)
    back_match = re.match(r"help_back", query.data)
    try:
        if mod_match:
            module = mod_match.group(1)
            text = (
                "*⚊❮❮❮❮ ｢  ʜᴇʟᴘ  ꜰᴏʀ  {}  ᴍᴏᴅᴜʟᴇ 」❯❯❯❯⚊*\n".format(
                    HELPABLE[module].__mod_name__
                )
                + HELPABLE[module].__help__
            )
            query.message.edit_text(
                text=text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(text="Back", callback_data="help_back")]]
                ),
            )

        elif prev_match:
            curr_page = int(prev_match.group(1))
            query.message.edit_text(
                HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(curr_page - 1, HELPABLE, "help")
                ),
            )

        elif next_match:
            next_page = int(next_match.group(1))
            query.message.edit_text(
                HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(next_page + 1, HELPABLE, "help")
                ),
            )

        elif back_match:
            query.message.edit_text(
                text=HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, HELPABLE, "help")
                ),
            )

        # ensure no spinny white circle
        context.bot.answer_callback_query(query.id)
        # query.message.delete()
    except Exception as excp:
        if excp.message == "Message is not modified":
            pass
        elif excp.message == "Query_id_invalid":
            pass
        elif excp.message == "Message can't be deleted":
            pass
        else:
            query.message.edit_text(excp.message)
            LOGGER.exception("Exception in help buttons. %s", str(query.data))


@run_async
def Angel_about_callback(update, context):
    query = update.callback_query
    if query.data == "aboutmanu_":
        query.message.edit_text(
            text=f"*ʜɪ ᴛʜᴇʀᴇ  ᴛʜᴇ ɴᴀᴍᴇ's {dispatcher.bot.first_name} \n\nᴀs ʏᴏᴜ ɪ'ᴍ ᴀ ɴᴇxᴛ ɢᴇɴᴇʀᴀᴛɪᴏɴᴀʟ ɢʀᴏᴜᴘ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ ʙᴏᴛ ᴅᴇᴠᴇʟᴏᴘᴇᴅ ʙʏ ᴀɴɢᴇʟ ᴜᴘᴅᴀᴛᴇs.* "
            f"\n\n➜ ᴊᴏɪɴ [AngelxNews](https://t.me/angelxupdates) ᴛᴏ ᴋᴇᴇᴘ ʏᴏᴜʀsᴇʟꜰ ᴜᴘᴅᴀᴛᴇᴅ ᴀʙᴏᴜᴛ {dispatcher.bot.first_name}"
            f"\n\n➜ ɪ ʜᴀᴠᴇ ᴛʜᴇ ɴᴏʀᴍᴀʟ ɢʀᴏᴜᴘ ᴍᴀɴᴀɢɪɴɢ ꜰᴜɴᴄᴛɪᴏɴs ʟɪᴋᴇ ꜰʟᴏᴏᴅ ᴄᴏɴᴛʀᴏʟ, ᴀ ᴡᴀʀɴɪɴɢ sʏsᴛᴇᴍ ᴇᴛᴄ ʙᴜᴛ ɪ ᴍᴀɪɴʟʏ ʜᴀᴠᴇ ᴛʜᴇ ᴀᴅᴠᴀɴᴄᴇᴅ ᴀɴᴅ ʜᴀɴᴅʏ ᴀɴᴛɪsᴘᴀᴍ sʏsᴛᴇᴍ ᴀɴᴅ ᴛʜᴇ sɪʙʏʟ ʙᴀɴɴɪɴɢ sʏsᴛᴇᴍ ᴡʜɪᴄʜ sᴀꜰᴇɢᴀᴜʀᴅs ᴀɴᴅ ʜᴇʟᴘs ʏᴏᴜʀ ɢʀᴏᴜᴘ ꜰʀᴏᴍ sᴘᴀᴍᴍᴇʀs."
            f"\n\n➜ ɪ ᴄᴀɴ ᴍᴀɴᴀɢᴇ ʏᴏᴜʀ ɢʀᴏᴜᴘs sᴍᴏᴏᴛʜʟʏ, ᴡɪᴛʜ sᴏᴍᴇ sᴘᴇᴄɪᴀʟ ꜰᴇᴀᴛᴜʀᴇs"
            f"\n\n➜ ʏᴏᴜ ᴄᴀɴ ᴋɴᴏᴡ ᴍᴏʀᴇ ᴀʙᴏᴜᴛ ᴍᴇ ʙʏ ᴄʟɪᴄᴋɪɴɢ ᴛʜᴇ ʙᴇʟᴏᴡ ʙᴜᴛᴛᴏɴs",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="ʜᴏᴡ ᴛᴏ ᴜsᴇ ᴍᴇ 👩🏼‍💻", callback_data="aboutmanu_howto"
                        ),
                        InlineKeyboardButton(
                            text="📕ᴛᴇʀᴍs ᴀɴᴅ ᴄᴏɴᴅɪᴛɪᴏɴs ", callback_data="aboutmanu_tac"
                        ),
                    ],
                    [InlineKeyboardButton(text="ʜᴇʟᴘ ❔", callback_data="help_back")],
                    [InlineKeyboardButton(text="˹ʙᴀᴄᴋ ˼", callback_data="aboutmanu_back")],
                ]
            ),
        )
    elif query.data == "aboutmanu_back":
        query.message.edit_text(
            PM_START_TEXT,
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=ParseMode.MARKDOWN,
            timeout=60,
        )

    elif query.data == "aboutmanu_howto":
        query.message.edit_text(
            text=f"* ｢ ʙᴀsɪᴄ ʜᴇʟᴘ ☘️」*"
            f"\nʏᴏᴜ ᴄᴀɴ ᴀʟsᴏ ᴀᴅᴅ {dispatcher.bot.first_name} ᴛᴏ ʏᴏᴜʀ ᴄʜᴀᴛs ʙʏ ᴄʟɪᴄᴋɪɴɢ [Here](http://t.me/{dispatcher.bot.username}?startgroup=true) ᴀɴᴅ sᴇʟᴇᴄᴛɪɴɢ ᴄʜᴀᴛ ✓. \n"
            f"\n\nʏᴏᴜ ᴄᴀɴ ɢᴇᴛ sᴜᴘᴘᴏʀᴛ 🦩 {dispatcher.bot.first_name} ʙʏ ᴊᴏɪɴɪɴɢ 🐾[ANGEL SUPPORT](https://t.me/angelsupports).\n"
            f"",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="Admins", callback_data="aboutmanu_permis"
                        ),
                        InlineKeyboardButton(text="Help", callback_data="help_back"),
                    ],
                    [InlineKeyboardButton(text="˹ʙᴀᴄᴋ ˼", callback_data="aboutmanu_")],
                ]
            ),
        )
    elif query.data == "aboutmanu_credit":
        query.message.edit_text(
            text=f"*{dispatcher.bot.first_name} ɪs ᴛʜᴇ ʀᴇᴅɪsɪɢɴᴇᴅ ᴠᴇʀsɪᴏɴ ♻️ ᴏꜰ ᴅᴀɪsʏ ᴀɴᴅ ɴᴀʀᴜᴛᴏ ꜰᴏʀ ᴛʜᴇ ʙᴇsᴛ ᴘᴇʀꜰᴏʀᴍᴀɴᴄᴇ 🚀.*"
            f"\n\nʙᴀsᴇᴅ ᴏɴ [Sɪʟᴇɴᴛ「🇮🇳」Bᴏᴛs](https://t.me/SILENT_BOTS)."
            f"\n\n{dispatcher.bot.first_name}'s sᴏᴜʀᴄᴇ ᴄᴏᴅᴇ ᴡᴀs ᴡʀɪᴛᴛᴇɴ ʙʏ ᴠɪᴄᴋʏ 🥀🍂✨"
            f"\n\nɪꜰ ᴀɴʏ ǫᴜᴇsᴛɪᴏɴ ᴀʙᴏᴜᴛ  {dispatcher.bot.first_name}, \nʟᴇᴛ ᴜs ᴋɴᴏᴡ ᴀᴛ 👂 @{SUPPORT_CHAT}.",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="˹ʙᴀᴄᴋ ˼", callback_data="aboutmanu_tac")]]
            ),
        )

    elif query.data == "aboutmanu_permis":
        query.message.edit_text(
            text=f"<b> ｢ ᴀᴅᴍɪɴ ᴘᴇʀᴍɪssɪᴏɴs 」</b>"
            f"\nᴛᴏ ᴀᴠᴏɪᴅ sʟᴏᴡɪɴɢ ᴅᴏᴡɴ, {dispatcher.bot.first_name} ᴄᴀᴄʜᴇs ᴀᴅᴍɪɴ ʀɪɢʜᴛs ꜰᴏʀ ᴇᴀᴄʜ ᴜsᴇʀ. ᴛʜɪs ᴄᴀᴄʜᴇ ʟᴀsᴛs ᴀʙᴏᴜᴛ 10 ᴍɪɴᴜᴛᴇs; ᴛʜɪs ᴍᴀʏ ᴄʜᴀɴɢᴇ ɪɴ ᴛʜᴇ ꜰᴜᴛᴜʀᴇ. ᴛʜɪs ᴍᴇᴀɴs ᴛʜᴀᴛ ɪꜰ ʏᴏᴜ ᴘʀᴏᴍᴏᴛᴇ ᴀ ᴜsᴇʀ ᴍᴀɴᴜᴀʟʟʏ (ᴡɪᴛʜᴏᴜᴛ ᴜsɪɴɢ ᴛʜᴇ /ᴘʀᴏᴍᴏᴛᴇ ᴄᴏᴍᴍᴀɴᴅ), {dispatcher.bot.first_name} ᴡɪʟʟ ᴏɴʟʏ ꜰɪɴᴅ ᴏᴜᴛ ~10 ᴍɪɴᴜᴛᴇs ʟᴀᴛᴇʀ."
            f"\n\nɪꜰ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴜᴘᴅᴀᴛᴇ ᴛʜᴇᴍ ɪᴍᴍᴇᴅɪᴀᴛᴇʟʏ, ʏᴏᴜ ᴄᴀɴ ᴜsᴇ ᴛʜᴇ /ᴀᴅᴍɪɴᴄᴀᴄʜᴇ ᴄᴏᴍᴍᴀɴᴅ,ᴛʜᴛᴀ'ʟʟ ꜰᴏʀᴄᴇ{dispatcher.bot.first_name} ᴛᴏ ᴄʜᴇᴄᴋ ᴡʜᴏ ᴛʜᴇ ᴀᴅᴍɪɴs ᴀʀᴇ ᴀɢᴀɪɴ ᴀɴᴅ ᴛʜᴇɪʀ ᴘᴇʀᴍɪssɪᴏɴs"
            f"\n\nɪꜰ ʏᴏᴜ ᴀʀᴇ ɢᴇᴛᴛɪɴɢ ᴀ ᴍᴇssᴀɢᴇ sᴀʏɪɴɢ:"
            f"\n<Code>ʏᴏᴜ ᴍᴜsᴛ ʙᴇ ᴛʜɪs ᴄʜᴀᴛ ᴀᴅᴍɪɴɪsᴛʀᴀᴛᴏʀ ᴛᴏ ᴘᴇʀꜰᴏʀᴍ ᴛʜɪs ᴀᴄᴛɪᴏɴ!</code>"
            f"\nᴛʜɪꜱ ʜᴀꜱ ɴᴏᴛʜɪɴɢ ᴛᴏ ᴅᴏ ᴡɪᴛʜ {dispatcher.bot.first_name}'ꜱ ʀɪɢʜᴛꜱ; ᴛʜɪꜱ ɪꜱ ᴀʟʟ ᴀʙᴏᴜᴛ ʏᴏᴜʀ ᴘᴇʀᴍɪꜱꜱɪᴏɴꜱ ᴀꜱ ᴀɴ ᴀᴅᴍɪɴ. {dispatcher.bot.first_name} ʀᴇꜱᴘᴇᴄᴛꜱ ᴀᴅᴍɪɴ ᴘᴇʀᴍɪꜱꜱɪᴏɴꜱ; ɪꜰ ʏᴏᴜ ᴅᴏ ɴᴏᴛ ʜᴀᴠᴇ ᴛʜᴇ ʙᴀɴ ᴜꜱᴇʀꜱ ᴘᴇʀᴍɪꜱꜱɪᴏɴ ᴀꜱ ᴀ ᴛᴇʟᴇɢʀᴀᴍ ᴀᴅᴍɪɴ, ʏᴏᴜ ᴡᴏɴ'ᴛ ʙᴇ ᴀʙʟᴇ ᴛᴏ ʙᴀɴ ᴜꜱᴇʀꜱ ᴡɪᴛʜ {dispatcher.bot.first_name}.ꜱɪᴍɪʟᴀʀʟʏ, ᴛᴏ ᴄʜᴀɴɢᴇ {dispatcher.bot.first_name} ꜱᴇᴛᴛɪɴɢꜱ, ʏᴏᴜ ɴᴇᴇᴅ ᴛᴏ ʜᴀᴠᴇ ᴛʜᴇ ᴄʜᴀɴɢᴇ ɢʀᴏᴜᴘ ɪɴꜰᴏ ᴘᴇʀᴍɪꜱꜱɪᴏɴ."
            f"\n\nᴛʜᴇ ᴍᴇꜱꜱᴀɢᴇ ᴠᴇʀʏ ᴄʟᴇᴀʀʟʏ ꜱᴀʏꜱ ᴛʜᴀᴛ ʏᴏᴜ ɴᴇᴇᴅ ᴛʜᴇꜱᴇ ʀɪɢʜᴛꜱ- <i>not {dispatcher.bot.first_name}.</i>",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="˹ʙᴀᴄᴋ ˼", callback_data="aboutmanu_howto")]]
            ),
        )
    elif query.data == "aboutmanu_spamprot":
        query.message.edit_text(
            text="* ｢ᴀɴᴛɪ-ꜱᴘᴀᴍ ꜱᴇᴛᴛɪɴɢꜱ 💬」*"
            "\n- /antispam <on/off/yes/no>: ᴄʜᴀɴɢᴇ ᴀɴᴛɪꜱᴘᴀᴍ ꜱᴇᴄᴜʀɪᴛʏ ꜱᴇᴛᴛɪɴɢꜱ ɪɴ ᴛʜᴇ ɢʀᴏᴜᴘ, ᴏʀ ʀᴇᴛᴜʀɴ ʏᴏᴜʀ ᴄᴜʀʀᴇɴᴛ ꜱᴇᴛᴛɪɴɢꜱ(when no arguments)."
            "\n_ᴛʜɪꜱ ʜᴇʟᴘꜱ ᴘʀᴏᴛᴇᴄᴛ ʏᴏᴜ ᴀɴᴅ ʏᴏᴜʀ ɢʀᴏᴜᴘꜱ ʙʏ ʀᴇᴍᴏᴠɪɴɢ ꜱᴘᴀᴍ ꜰʟᴏᴏᴅᴇʀꜱ ᴀꜱ Qᴜɪᴄᴋʟʏ ᴀꜱ ᴘᴏꜱꜱɪʙʟᴇ._"
            "\n\n- /setflood <int/'no'/'off'>: ᴇɴᴀʙʟᴇꜱ ᴏʀ ᴅɪꜱᴀʙʟᴇꜱ ꜰʟᴏᴏᴅ ᴄᴏɴᴛʀᴏʟ"
            "\n- /setfloodmode <ban/kick/mute/tban/tmute> <value>:ᴀᴄᴛɪᴏɴ ᴛᴏ ᴘᴇʀꜰᴏʀᴍ ᴡʜᴇɴ ᴜꜱᴇʀ ʜᴀᴠᴇ ᴇxᴄᴇᴇᴅᴇᴅ ꜰʟᴏᴏᴅ ʟɪᴍɪᴛ. ban/kick/mute/tmute/tban"
            "\n_Antiflood ᴀʟʟᴏᴡꜱ ʏᴏᴜ ᴛᴏ ᴛᴀᴋᴇ ᴀᴄᴛɪᴏɴ ᴏɴ ᴜꜱᴇʀꜱ ᴛʜᴀᴛ ꜱᴇɴᴅ ᴍᴏʀᴇ ᴛʜᴀɴ x ᴍᴇꜱꜱᴀɢᴇꜱ ɪɴ ᴀ ʀᴏᴡ. ᴇxᴄᴇᴇᴅɪɴɢ ᴛʜᴇ ꜱᴇᴛ ꜰʟᴏᴏᴅ ᴡɪʟʟ ʀᴇꜱᴜʟᴛ ɪɴ ʀᴇꜱᴛʀɪᴄᴛɪɴɢ ᴛʜᴀᴛ ᴜꜱᴇʀ._"
            "\n\n- /addblacklist <triggers>: ᴀᴅᴅ ᴀ ᴛʀɪɢɢᴇʀ ᴛᴏ ᴛʜᴇ ʙʟᴀᴄᴋʟɪꜱᴛ. ᴇᴀᴄʜ ʟɪɴᴇ ɪꜱ ᴄᴏɴꜱɪᴅᴇʀᴇᴅ ᴏɴᴇ ᴛʀɪɢɢᴇʀ, ꜱᴏ ᴜꜱɪɴɢ ᴅɪꜰꜰᴇʀᴇɴᴛ ʟɪɴᴇꜱ ᴡɪʟʟ ᴀʟʟᴏᴡ ʏᴏᴜ ᴛᴏ ᴀᴅᴅ ᴍᴜʟᴛɪᴘʟᴇ ᴛʀɪɢɢᴇʀꜱ."
            "\n- /blacklistmode <off/del/warn/ban/kick/mute/tban/tmute>: ᴀᴄᴛɪᴏɴ ᴛᴏ ᴘᴇʀꜰᴏʀᴍ ᴡʜᴇɴ ꜱᴏᴍᴇᴏɴᴇ ꜱᴇɴᴅꜱ ʙʟᴀᴄᴋʟɪꜱᴛᴇᴅ ᴡᴏʀᴅꜱ."
            "\n_ʙʟᴀᴄᴋʟɪꜱᴛꜱ ᴀʀᴇ ᴜꜱᴇᴅ ᴛᴏ ꜱᴛᴏᴘ ᴄᴇʀᴛᴀɪɴ ᴛʀɪɢɢᴇʀꜱ ꜰʀᴏᴍ ʙᴇɪɴɢ ꜱᴀɪᴅ ɪɴ ᴀ ɢʀᴏᴜᴘ. ᴀɴʏ ᴛɪᴍᴇ ᴛʜᴇ ᴛʀɪɢɢᴇʀ ɪꜱ ᴍᴇɴᴛɪᴏɴᴇᴅ, ᴛʜᴇ ᴍᴇꜱꜱᴀɢᴇ ᴡɪʟʟ ɪᴍᴍᴇᴅɪᴀᴛᴇʟʏ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ. ᴀ ɢᴏᴏᴅ ᴄᴏᴍʙᴏ ɪꜱ ꜱᴏᴍᴇᴛɪᴍᴇꜱ ᴛᴏ ᴘᴀɪʀ ᴛʜɪꜱ ᴜᴘ ᴡɪᴛʜ ᴡᴀʀɴ ꜰɪʟᴛᴇʀꜱ!_"
            "\n\n- /reports <on/off>: ᴄʜᴀɴɢᴇ ʀᴇᴘᴏʀᴛ ꜱᴇᴛᴛɪɴɢ, ᴏʀ ᴠɪᴇᴡ ᴄᴜʀʀᴇɴᴛ ꜱᴛᴀᴛᴜꜱ."
            "\n • ɪꜰ ᴅᴏɴᴇ ɪɴ ᴘᴍ, ᴛᴏɢɢʟᴇꜱ ʏᴏᴜʀ ꜱᴛᴀᴛᴜꜱ."
            "\n • ɪꜰ ɪɴ ᴄʜᴀᴛ, ᴛᴏɢɢʟᴇꜱ ᴛʜᴀᴛ ᴄʜᴀᴛ'ꜱ ꜱᴛᴀᴛᴜꜱ."
            "\n_ɪꜰ ꜱᴏᴍᴇᴏɴᴇ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ ᴛʜɪɴᴋꜱ ꜱᴏᴍᴇᴏɴᴇ ɴᴇᴇᴅꜱ ʀᴇᴘᴏʀᴛɪɴɢ, ᴛʜᴇʏ ɴᴏᴡ ʜᴀᴠᴇ ᴀɴ ᴇᴀꜱʏ ᴡᴀʏ ᴛᴏ ᴄᴀʟʟ ᴀʟʟ ᴀᴅᴍɪɴꜱ._"
            "\n\n- /lock <type>: ʟᴏᴄᴋ ɪᴛᴇᴍꜱ ᴏꜰ ᴀ ᴄᴇʀᴛᴀɪɴ ᴛʏᴘᴇ (not available in private)"
            "\n- /locktypes: ʟɪꜱᴛꜱ ᴀʟʟ ᴘᴏꜱꜱɪʙʟᴇ ʟᴏᴄᴋᴛʏᴘᴇꜱ"
            "\n_ᴛʜᴇ ʟᴏᴄᴋꜱ ᴍᴏᴅᴜʟᴇ ᴀʟʟᴏᴡꜱ ʏᴏᴜ ᴛᴏ ʟᴏᴄᴋ ᴀᴡᴀʏ ꜱᴏᴍᴇ ᴄᴏᴍᴍᴏɴ ɪᴛᴇᴍꜱ ɪɴ ᴛʜᴇ ᴛᴇʟᴇɢʀᴀᴍ ᴡᴏʀʟᴅ; ᴛʜᴇ ʙᴏᴛ ᴡɪʟʟ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ ᴅᴇʟᴇᴛᴇ ᴛʜᴇᴍ!_"
            '\n\n- /addwarn <keyword> <reply message>: ꜱᴇᴛꜱ ᴀ ᴡᴀʀɴɪɴɢ ꜰɪʟᴛᴇʀ ᴏɴ ᴀ ᴄᴇʀᴛᴀɪɴ ᴋᴇʏᴡᴏʀᴅ. ɪꜰ ʏᴏᴜ ᴡᴀɴᴛ ʏᴏᴜʀ ᴋᴇʏᴡᴏʀᴅ ᴛᴏ ʙᴇ ᴀ ꜱᴇɴᴛᴇɴᴄᴇ, ᴇɴᴄᴏᴍᴘᴀꜱꜱ ɪᴛ ᴡɪᴛʜ Qᴜᴏᴛᴇꜱ, ᴀꜱ ꜱᴜᴄʜ: /addwarn "ᴠᴇʀʏ ᴀɴɢʀʏ" ᴛʜɪꜱ ɪꜱ ᴀɴ ᴀɴɢʀʏ ᴜꜱᴇʀ. '
            "\n- /warn <userhandle>: ᴡᴀʀɴꜱ ᴀ ᴜꜱᴇʀ. ᴀꜰᴛᴇʀ 3 ᴡᴀʀɴꜱ, ᴛʜᴇ ᴜꜱᴇʀ ᴡɪʟʟ ʙᴇ ʙᴀɴɴᴇᴅ ꜰʀᴏᴍ ᴛʜᴇ ɢʀᴏᴜᴘ. ᴄᴀɴ ᴀʟꜱᴏ ʙᴇ ᴜꜱᴇᴅ ᴀꜱ ᴀ ʀᴇᴘʟʏ."
            "\n- /strongwarn <on/yes/off/no>: ɪꜰ ꜱᴇᴛ ᴛᴏ ᴏɴ, ᴇxᴄᴇᴇᴅɪɴɢ ᴛʜᴇ ᴡᴀʀɴ ʟɪᴍɪᴛ ᴡɪʟʟ ʀᴇꜱᴜʟᴛ ɪɴ ᴀ ʙᴀɴ. ᴇʟꜱᴇ, ᴡɪʟʟ ᴊᴜꜱᴛ ᴋɪᴄᴋ."
            "\n_ɪꜰ ʏᴏᴜ'ʀᴇ ʟᴏᴏᴋɪɴɢ ꜰᴏʀ ᴀ ᴡᴀʏ ᴛᴏ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ ᴡᴀʀɴ ᴜꜱᴇʀꜱ ᴡʜᴇɴ ᴛʜᴇʏ ꜱᴀʏ ᴄᴇʀᴛᴀɪɴ ᴛʜɪɴɢꜱ, ᴜꜱᴇ ᴛʜᴇ /addwarm ᴄᴏᴍᴍᴀɴᴅ._"
            "\n\n- /welcomemute <off/soft/strong>: ᴀʟʟ ᴜꜱᴇʀꜱ ᴛʜᴀᴛ ᴊᴏɪɴ, ɢᴇᴛ ᴍᴜᴛᴇᴅ"
            "\n_ ᴀ ʙᴜᴛᴛᴏɴ ɢᴇᴛꜱ ᴀᴅᴅᴇᴅ ᴛᴏ ᴛʜᴇ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇꜱꜱᴀɢᴇ ꜰᴏʀ ᴛʜᴇᴍ ᴛᴏ ᴜɴᴍᴜᴛᴇ ᴛʜᴇᴍꜱᴇʟᴠᴇꜱ. ᴛʜɪꜱ ᴘʀᴏᴠᴇꜱ ᴛʜᴇʏ ᴀʀᴇɴ'ᴛ ᴀ ʙᴏᴛ! ꜱᴏꜰᴛ - ʀᴇꜱᴛʀɪᴄᴛꜱ ᴜꜱᴇʀꜱ ᴀʙɪʟɪᴛʏ ᴛᴏ ᴘᴏꜱᴛ ᴍᴇᴅɪᴀ ꜰᴏʀ 24 ʜᴏᴜʀꜱ. ꜱᴛʀᴏɴɢ - ᴍᴜᴛᴇꜱ ᴏɴ ᴊᴏɪɴ ᴜɴᴛɪʟ ᴛʜᴇʏ ᴘʀᴏᴠᴇ ᴛʜᴇʏ'ʀᴇ ɴᴏᴛ ʙᴏᴛꜱ._",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="˹ʙᴀᴄᴋ ˼", callback_data="aboutmanu_howto")]]
            ),
        )
    elif query.data == "aboutmanu_tac":
        query.message.edit_text(
            text=f"<b> ｢ ᴛᴇʀᴍꜱ ᴀɴᴅ ᴄᴏɴᴅɪᴛɪᴏɴꜱ 」</b>\n"
            f"\n<i>ᴛᴏ ᴜꜱᴇ ᴛʜɪꜱ ʙᴏᴛ, ʏᴏᴜ ɴᴇᴇᴅ ᴛᴏ ʀᴇᴀᴅ ᴛᴇʀᴍꜱ ᴀɴᴅ ᴄᴏɴᴅɪᴛɪᴏɴꜱ ᴄᴀʀᴇꜰᴜʟʟʏ.</i>\n"
            f"\n✪ᴡᴇ ᴀʟᴡᴀʏꜱ ʀᴇꜱᴘᴇᴄᴛ ʏᴏᴜʀ ᴘʀɪᴠᴀᴄʏ \n  ᴡᴇ ɴᴇᴠᴇʀ ʟᴏɢ ɪɴᴛᴏ ʙᴏᴛ'ꜱ ᴀᴘɪ ᴀɴᴅ ꜱᴘʏɪɴɢ ᴏɴ ʏᴏᴜ \n  ᴡᴇ ᴜꜱᴇ ᴀ ᴇɴᴄʀɪᴘᴛᴇᴅ ᴅᴀᴛᴀʙᴀꜱᴇ \n  ʙᴏᴛ ᴡɪʟʟ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ ꜱᴛᴏᴘꜱ ɪꜰ ꜱᴏᴍᴇᴏɴᴇ ʟᴏɢɢᴇᴅ ɪɴ ᴡɪᴛʜ ᴀᴘɪ."
            f"\n✪ ᴀʟᴡᴀʏꜱ ᴛʀʏ ᴛᴏ ᴋᴇᴇᴘ ᴄʀᴇᴅɪᴛꜱ, ꜱᴏ \n  ᴛʜɪꜱ ʜᴀʀᴅᴡᴏʀᴋ ɪꜱ ᴅᴏɴᴇ ʙʏ ᴛᴇᴀᴍ ꜱɪʟᴇɴᴛ ꜱᴘᴇɴᴅɪɴɢ ᴍᴀɴʏ ꜱʟᴇᴇᴘʟᴇꜱꜱ ɴɪɢʜᴛꜱ.. ꜱᴏ, ʀᴇꜱᴘᴇᴄᴛ ɪᴛ."
            f"\n✪ ꜱᴏᴍᴇ ᴍᴏᴅᴜʟᴇꜱ ɪɴ ᴛʜɪꜱ ʙᴏᴛ ɪꜱ ᴏᴡɴᴇᴅ ʙʏ ᴅɪꜰꜰᴇʀᴇɴᴛ ᴀᴜᴛʜᴏʀꜱ, ꜱᴏ, \n  ᴀʟʟ ᴄʀᴇᴅɪᴛꜱ ɢᴏᴇꜱ ᴛᴏ ᴛʜᴇᴍ \n  Also for <b>Paul Larson for Marie</b>."
            f"\n✪ ɪꜰ ʏᴏᴜ ɴᴇᴇᴅ ᴛᴏ ᴀꜱᴋ ᴀɴʏᴛʜɪɴɢ ᴀʙᴏᴜᴛ\n  ᴛʜɪꜱ ʙᴏᴛ, ɢᴏ @{SUPPORT_CHAT}."
            f"\n✪ ɪꜰ ʏᴏᴜ ᴀꜱᴋɪɴɢ ɴᴏɴꜱᴇɴꜱᴇ ɪɴ ꜱᴜᴘᴘᴏʀᴛ \n  ᴄʜᴀᴛ, ʏᴏᴜ ᴡɪʟʟ ɢᴇᴛ ᴡᴀʀɴᴇᴅ/ʙᴀɴɴᴇᴅ."
            f"\n✪ ᴀʟʟ ᴀᴘɪ'ꜱ ᴡᴇ ᴜꜱᴇᴅ ᴏᴡɴᴇᴅ ʙʏ ᴏʀɪɢɪɴɴᴀʟ ᴀᴜᴛʜᴏʀꜱ \n  Some api's we use Free version \n  ᴘʟᴇᴀꜱᴇ ᴅᴏɴ'ᴛ ᴏᴠᴇʀᴜꜱᴇ ᴀɪ ᴄʜᴀᴛ."
            f"\n✪ ᴡᴇ ᴅᴏɴ'ᴛ ᴘʀᴏᴠɪᴅᴇ ᴀɴʏ ꜱᴜᴘᴘᴏʀᴛ ᴛᴏ ꜰᴏʀᴋꜱ,\n  ꜱᴏ ᴛʜᴇꜱᴇ ᴛᴇʀᴍꜱ ᴀɴᴅ ᴄᴏɴᴅɪᴛɪᴏɴꜱ ɴᴏᴛ ᴀᴘᴘʟɪᴇᴅ ᴛᴏ ꜰᴏʀᴋꜱ \n  ɪꜰ ʏᴏᴜ ᴀʀᴇ ᴜꜱɪɴɢ ᴀ ꜰᴏʀᴋ ᴏꜰ ᴛʜᴇ ᴀɴɢᴇʟ ʙᴏᴛ ᴡᴇ ᴀʀᴇ ɴᴏᴛ ʀᴇꜱᴘᴏꜱɪʙʟᴇ ꜰᴏʀ ᴀɴʏᴛʜɪɴɢ."
            f"\n\nꜰᴏʀ ᴀɴʏ ᴋɪɴᴅ ᴏꜰ ʜᴇʟᴘ, ʀᴇʟᴀᴛᴇᴅ ᴛᴏ ᴛʜɪꜱ ʙᴏᴛ, Join @{SUPPORT_CHAT}."
            f"\n\n<i>ᴛᴇʀᴍꜱ & ᴄᴏɴᴅɪᴛɪᴏɴꜱ ᴡɪʟʟ ʙᴇ ᴄʜᴀɴɢᴇᴅ ᴀɴʏᴛɪᴍᴇ</i>\n",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="Credits", callback_data="aboutmanu_credit"
                        ),
                        InlineKeyboardButton(text="˹ʙᴀᴄᴋ ˼", callback_data="aboutmanu_"),
                    ]
                ]
            ),
        )


@run_async
@typing_action
def get_help(update, context):
    chat = update.effective_chat  # type: Optional[Chat]
    args = update.effective_message.text.split(None, 1)

    # ONLY send help in PM
    if chat.type != chat.PRIVATE:
        if len(args) >= 2 and any(args[1].lower() == x for x in HELPABLE):
            module = args[1].lower()
            update.effective_message.reply_text(
                f"Contact me in PM to get help of {module.capitalize()}",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="Help",
                                url="t.me/{}?start=ghelp_{}".format(
                                    context.bot.username, module
                                ),
                            )
                        ]
                    ]
                ),
            )
            return
        update.effective_message.reply_text(
            "ᴄᴏɴᴛᴀᴄᴛ ᴍᴇ ɪɴ ᴘᴍ ᴛᴏ ɢᴇᴛ ᴛʜᴇ ʟɪꜱᴛ ᴏꜰ ᴘᴏꜱꜱɪʙʟᴇ ᴄᴏᴍᴍᴀɴᴅꜱ.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="Help",
                            url="t.me/{}?start=help".format(context.bot.username),
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="Support Chat",
                            url="https://t.me/{}".format(SUPPORT_CHAT),
                        )
                    ],
                ]
            ),
        )
        return

    elif len(args) >= 2 and any(args[1].lower() == x for x in HELPABLE):
        module = args[1].lower()
        text = (
            "Here is the available help for the *{}* module:\n".format(
                HELPABLE[module].__mod_name__
            )
            + HELPABLE[module].__help__
        )
        send_help(
            chat.id,
            text,
            InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="˹ʙᴀᴄᴋ ˼", callback_data="help_back")]]
            ),
        )

    else:
        send_help(chat.id, HELP_STRINGS)


def send_settings(chat_id, user_id, user=False):
    if user:
        if USER_SETTINGS:
            settings = "\n\n".join(
                "*{}*:\n{}".format(mod.__mod_name__, mod.__user_settings__(user_id))
                for mod in USER_SETTINGS.values()
            )
            dispatcher.bot.send_message(
                user_id,
                "These are your current settings:" + "\n\n" + settings,
                parse_mode=ParseMode.MARKDOWN,
            )

        else:
            dispatcher.bot.send_message(
                user_id,
                "Seems like there aren't any user specific settings available :'(",
                parse_mode=ParseMode.MARKDOWN,
            )

    else:
        if CHAT_SETTINGS:
            chat_name = dispatcher.bot.getChat(chat_id).title
            dispatcher.bot.send_message(
                user_id,
                text="Which module would you like to check {}'s settings for?".format(
                    chat_name
                ),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, CHAT_SETTINGS, "stngs", chat=chat_id)
                ),
            )
        else:
            dispatcher.bot.send_message(
                user_id,
                "Seems like there aren't any chat settings available :'(\nSend this "
                "in a group chat you're admin in to find its current settings!",
                parse_mode=ParseMode.MARKDOWN,
            )


@run_async
def settings_button(update, context):
    query = update.callback_query
    user = update.effective_user
    mod_match = re.match(r"stngs_module\((.+?),(.+?)\)", query.data)
    prev_match = re.match(r"stngs_prev\((.+?),(.+?)\)", query.data)
    next_match = re.match(r"stngs_next\((.+?),(.+?)\)", query.data)
    back_match = re.match(r"stngs_back\((.+?)\)", query.data)
    try:
        if mod_match:
            chat_id = mod_match.group(1)
            module = mod_match.group(2)
            chat = context.bot.get_chat(chat_id)
            text = "*{}* has the following settings for the *{}* module:\n\n".format(
                escape_markdown(chat.title), CHAT_SETTINGS[module].__mod_name__
            ) + CHAT_SETTINGS[module].__chat_settings__(chat_id, user.id)
            query.message.edit_text(
                text=text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="Back",
                                callback_data="stngs_back({})".format(chat_id),
                            )
                        ]
                    ]
                ),
            )

        elif prev_match:
            chat_id = prev_match.group(1)
            curr_page = int(prev_match.group(2))
            chat = context.bot.get_chat(chat_id)
            query.message.edit_text(
                "Hi there! There are quite a few settings for *{}* - go ahead and pick what "
                "you're interested in.".format(chat.title),
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(
                        curr_page - 1, CHAT_SETTINGS, "stngs", chat=chat_id
                    )
                ),
            )

        elif next_match:
            chat_id = next_match.group(1)
            next_page = int(next_match.group(2))
            chat = context.bot.get_chat(chat_id)
            query.message.edit_text(
                "Hi there! There are quite a few settings for *{}* - go ahead and pick what "
                "you're interested in.".format(chat.title),
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(
                        next_page + 1, CHAT_SETTINGS, "stngs", chat=chat_id
                    )
                ),
            )

        elif back_match:
            chat_id = back_match.group(1)
            chat = context.bot.get_chat(chat_id)
            query.message.edit_text(
                text="Hi there! There are quite a few settings for *{}* - go ahead and pick what "
                "you're interested in.".format(escape_markdown(chat.title)),
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, CHAT_SETTINGS, "stngs", chat=chat_id)
                ),
            )

        # ensure no spinny white circle
        context.bot.answer_callback_query(query.id)
        # query.message.delete()
    except Exception as excp:
        if excp.message == "Message is not modified":
            pass
        elif excp.message == "Query_id_invalid":
            pass
        elif excp.message == "Message can't be deleted":
            pass
        else:
            query.message.edit_text(excp.message)
            LOGGER.exception("Exception in settings buttons. %s", str(query.data))


@run_async
def get_settings(update: Update, context: CallbackContext):
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    msg = update.effective_message  # type: Optional[Message]

    # ONLY send settings in PM
    if chat.type != chat.PRIVATE:
        if is_user_admin(chat, user.id):
            text = "Click here to get this chat's settings, as well as yours."
            msg.reply_text(
                text,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="Settings",
                                url="t.me/{}?start=stngs_{}".format(
                                    context.bot.username, chat.id
                                ),
                            )
                        ]
                    ]
                ),
            )
        else:
            text = "Click here to check your settings."

    else:
        send_settings(chat.id, user.id, True)


def migrate_chats(update, context):
    msg = update.effective_message  # type: Optional[Message]
    if msg.migrate_to_chat_id:
        old_chat = update.effective_chat.id
        new_chat = msg.migrate_to_chat_id
    elif msg.migrate_from_chat_id:
        old_chat = msg.migrate_from_chat_id
        new_chat = update.effective_chat.id
    else:
        return

    LOGGER.info("Migrating from %s, to %s", str(old_chat), str(new_chat))
    for mod in MIGRATEABLE:
        mod.__migrate__(old_chat, new_chat)

    LOGGER.info("Successfully migrated!")
    raise DispatcherHandlerStop


def is_chat_allowed(update, context):
    if len(WHITELIST_CHATS) != 0:
        chat_id = update.effective_message.chat_id
        if chat_id not in WHITELIST_CHATS:
            context.bot.send_message(
                chat_id=update.message.chat_id, text="Unallowed chat! Leaving..."
            )
            try:
                context.bot.leave_chat(chat_id)
            finally:
                raise DispatcherHandlerStop
    if len(BL_CHATS) != 0:
        chat_id = update.effective_message.chat_id
        if chat_id in BL_CHATS:
            context.bot.send_message(
                chat_id=update.message.chat_id, text="Unallowed chat! Leaving..."
            )
            try:
                context.bot.leave_chat(chat_id)
            finally:
                raise DispatcherHandlerStop
    if len(WHITELIST_CHATS) != 0 and len(BL_CHATS) != 0:
        chat_id = update.effective_message.chat_id
        if chat_id in BL_CHATS:
            context.bot.send_message(
                chat_id=update.message.chat_id, text="Unallowed chat, leaving"
            )
            try:
                context.bot.leave_chat(chat_id)
            finally:
                raise DispatcherHandlerStop
    else:
        pass


@run_async
def donate(update: Update, context: CallbackContext):
    update.effective_message.from_user
    chat = update.effective_chat  # type: Optional[Chat]
    context.bot
    if chat.type == "private":
        update.effective_message.reply_text(
            DONATE_STRING, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True
        )
        update.effective_message.reply_text(
            "You can also donate to the person currently running me "
            "[here]({})".format(DONATION_LINK),
            parse_mode=ParseMode.MARKDOWN,
        )

    else:
        pass


def main():

    if SUPPORT_CHAT is not None and isinstance(SUPPORT_CHAT, str):
        try:
            dispatcher.bot.sendMessage(f"@{SUPPORT_CHAT}", "» ❤️‍🩹✨ɴᴏ ꜰᴇᴀʀ ᴡᴇɴ ᴀɴɢᴇʟ ɪs ʜᴇʀᴇ ✨👻 «")
        except Unauthorized:
            LOGGER.warning(
                "Bot isnt able to send message to support_chat, go and check!"
            )
        except BadRequest as e:
            LOGGER.warning(e.message)

    # test_handler = CommandHandler("test", test)
    start_handler = CommandHandler("start", start, pass_args=True)

    help_handler = CommandHandler("help", get_help)
    help_callback_handler = CallbackQueryHandler(help_button, pattern=r"help_")

    settings_handler = CommandHandler("settings", get_settings)
    settings_callback_handler = CallbackQueryHandler(settings_button, pattern=r"stngs_")

    about_callback_handler = CallbackQueryHandler(
        Angel_about_callback, pattern=r"aboutmanu_"
    )

    donate_handler = CommandHandler("donate", donate)

    migrate_handler = MessageHandler(Filters.status_update.migrate, migrate_chats)
    is_chat_allowed_handler = MessageHandler(Filters.group, is_chat_allowed)

    # dispatcher.add_handler(test_handler)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(about_callback_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(settings_handler)
    dispatcher.add_handler(help_callback_handler)
    dispatcher.add_handler(settings_callback_handler)
    dispatcher.add_handler(migrate_handler)
    dispatcher.add_handler(is_chat_allowed_handler)
    dispatcher.add_handler(donate_handler)

    dispatcher.add_error_handler(error_handler)

    if WEBHOOK:
        LOGGER.info("Using webhooks.")
        updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN)

        if CERT_PATH:
            updater.bot.set_webhook(url=URL + TOKEN, certificate=open(CERT_PATH, "rb"))
        else:
            updater.bot.set_webhook(url=URL + TOKEN)
            client.run_until_disconnected()

    else:
        LOGGER.info("Using long polling.")
        updater.start_polling(timeout=15, read_latency=4, clean=True)

    if len(argv) not in (1, 3, 4):
        telethn.disconnect()
    else:
        telethn.run_until_disconnected()

    updater.idle()


if __name__ == "__main__":
    LOGGER.info("Successfully loaded modules: " + str(ALL_MODULES))
    telethn.start(bot_token=TOKEN)
    pbot.start()
    main()
