import random
import logging
from time import sleep
import traceback
import re

from pyrogram import filters

from bot import app, monitored_chats, chats_map, sudo_users
from pyrogram.types import Message
from pyrogram.enums import ParseMode, MessageMediaType
from pyrogram import Client

logging.info("Bot Started")


@app.on_message(filters.chat(monitored_chats) & filters.incoming)
def work(_: Client, message: Message):
    chat = chats_map.get(message.chat.id)

    message_content = (
        (message.caption or message.text).markdown
        if (message.caption or message.text)
        else ""
    )

    if chat_filters := chat.get("filter"):
        if not any(
            (not filter.get("regex") or re.match(
                filter["regex"], message_content))
            and (
                not filter.get("media")
                or any(
                    (
                        message.media == MessageMediaType[media.upper()]
                        if media != "None"
                        else message.media == None
                    )
                    for media in (
                        [filter["media"]]
                        if isinstance(filter["media"], str)
                        else filter["media"]
                    )
                )
            )
            for filter in chat_filters
        ):
            return

    if chat.get("replace"):
        for old, new in chat["replace"].items():
            message_content = message_content.replace(old, new)

    try:
        for chat in chat["to"]:
            if message.caption:
                message.copy(
                    chat, caption=message_content, parse_mode=ParseMode.MARKDOWN
                )
            elif message.text:
                app.send_message(chat, message_content,
                                 parse_mode=ParseMode.MARKDOWN)
            else:
                message.copy(chat)
    except Exception as e:
        logging.error(
            f"Error while sending message from {
                message.chat.id} to {chat}: {e}"
        )


@app.on_message(filters.user(sudo_users) & filters.command(["fwd", "forward"]), group=1)
def forward(client: Client, message: Message):
    if len(message.command) > 1 and message.command[1].isdigit():
        chat_id = int(message.command[1])
        if chat_id:
            try:
                offset_id = 0
                limit = 0
                if len(message.command) > 2:
                    limit = int(message.command[2])
                if len(message.command) > 3:
                    offset_id = int(message.command[3])
                for msg in client.get_chat_history(
                    chat_id, limit=limit, offset_id=offset_id
                ):
                    msg.copy(message.chat.id)
                    sleep(random.randint(1, 5))
            except Exception as e:
                message.reply_text(f"Error:\n```{traceback.format_exc()}```")
        else:
            message.reply_text("Invalid Chat Identifier. Give me a chat id.")
    else:
        message.reply_text(
            "Invalid Command\nUse /fwd {chat_id} {limit} {first_message_id}"
        )


app.run()
