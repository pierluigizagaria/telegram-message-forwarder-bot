import logging
import re

from pyrogram import filters

from bot import app, monitored_chats, rules_map
from pyrogram.types import Message
from pyrogram.enums import ParseMode, MessageMediaType
from pyrogram import Client, idle

logging.info("Bot Started")


@app.on_message(filters.chat(monitored_chats) & filters.incoming)
def work(_: Client, message: Message):
    message_content = (
        (message.caption or message.text).markdown
        if (message.caption or message.text)
        else ""
    )

    for rule in rules_map.get(message.chat.id):
        message_copy = message_content

        if chat_filters := rule.get("filter"):
            if not any(
                (not filter.get("regex") or re.search(
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

        if rule.get("replace"):
            for old, new in rule["replace"].items():
                message_copy = re.sub(old, new, message_content)

        try:
            for chat in rule["to"]:
                topic_id = int(str(chat).split("_")[1]) if len(
                    str(chat).split("_")) > 1 else None
                chat_id = chat if topic_id is None else chat.split("_")[0]
                if message.caption:
                    message.copy(
                        chat_id, caption=message_copy, reply_to_message_id=topic_id, parse_mode=ParseMode.MARKDOWN
                    )
                elif message.text:
                    app.send_message(chat_id, message_copy, reply_to_message_id=topic_id,
                                     parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            logging.error(
                f"Error while sending message from {
                    message.chat.id} to {chat_id}: {e}"
            )


async def run_and_tap_chats():
    await app.start()
    if not (await app.get_me()).is_bot:
        # Tap all chats to populate internal peer ids.
        async for _ in app.get_dialogs():
            pass
    await idle()
    await app.stop()

app.run(run_and_tap_chats())
