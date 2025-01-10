def parse_chats(chats):
    """

    [[chats]]
    from = "123456789"
    to = "123456789"

    [[chats]]
    from = ["123456789", "123456789"]
    to = "123456789"

    [[chats]]
    from = "123456789"
    to = ["123456789", "123456789"]

    [[chats]]
    from = ["123456789", "123456789"]
    to = ["123456789", "123456789"]
    """

    # Set all from values to a list and, from => [to, replace] in dict
    monitored_chats = set()
    rules_map = {}

    for chat in chats:
        from_chats = chat["from"] if isinstance(chat["from"], list) else [
            chat["from"]]

        to_chats = chat["to"] if isinstance(chat["to"], list) else [
            chat["to"]]

        filter = chat.get("filter") if isinstance(chat.get("filter"), list) else [
            chat.get("filter")] if chat.get("filter") else None

        replace = chat.get("replace")

        for from_chat in from_chats:
            if from_chat not in rules_map:
                rules_map[from_chat] = [{
                    "to": to_chats,
                    "replace": replace,
                    "filter": filter,
                }]
            else:
                rules_map[from_chat].append(
                    {
                        "to": to_chats,
                        "replace": replace,
                        "filter": filter,
                    }
                )
            monitored_chats.add(from_chat)

    return list(monitored_chats), rules_map
