import os
from typing import Dict, Any, Tuple, List
import json

SOURCE_PATH = "./source/"
NOT_CHANNEL_PATH = (
    "channels.json",
    "integration_logs.json",
    "users.json",
)


def get_username(user: Dict[str, Any]) -> str:
    return user["profile"]["display_name"] + " @" + user["profile"]["real_name"]


def source_init(source: str) -> Tuple[str, List[str], Dict[str, str]]:
    source_path = SOURCE_PATH + source + "/"

    channels = list(
        filter(lambda x: x not in NOT_CHANNEL_PATH, os.listdir(source_path))
    )

    user_map: Dict[str, str] = {}
    with open(source_path + "users.json", "r", encoding="utf-8") as f:
        users = json.loads(f.read())
        for user in users:
            user_map[user["id"]] = get_username(user)

    try:
        os.mkdir(f"./dist/{source.split(' ')[0]}/")
    except Exception as e:
        print(e)
        pass

    return source_path, channels, user_map


def channel_init(
    channel: str, source: str, source_path: str
) -> Tuple[str, str, List[str]]:
    export_path = f"./dist/{source.split(' ')[0]}/{channel}.md"
    channel_path = source_path + channel + "/"
    days = os.listdir(channel_path)

    return export_path, channel_path, days


def day_process(channel_path: str, day: str) -> str:
    export_data = f"## {day[-15:][:-5]}\n"

    with open(channel_path + day, "r", encoding="utf-8") as f:
        messages = json.loads(f.read())
        for message in messages:
            user = user_map.get(message.get("user", "dummy"), "unknown @unknown")
            export_data = export_data + f"### {user}\n{message['text']}\n"

    return export_data


def cleansing_dir(source: str):

    source_path, channels, _ = source_init(source)
    json_of_garbled_characters_channels = list(
        filter(lambda x: x[-5:] == ".json", channels)
    )
    garbled_characters_channels = {
        file_name[:-15]
        for file_name in json_of_garbled_characters_channels
        if file_name[-5:] == ".json"
    }
    for channel in garbled_characters_channels:
        os.remove(source_path + channel)
        os.mkdir(source_path + channel + "/")
        for filename in json_of_garbled_characters_channels:
            if filename[:-15] == channel:
                os.rename(
                    source_path + filename, source_path + channel + "/" + filename
                )


if __name__ == "__main__":

    sources = os.listdir(SOURCE_PATH)
    for source in sources:
        cleansing_dir(source)

    for source in sources:
        source_path, channels, user_map = source_init(source)
        for channel in channels:
            export_path, channel_path, days = channel_init(channel, source, source_path)
            export_data = f"# {channel}\n"
            for day in days:
                export_data = export_data + day_process(channel_path, day)
            with open(export_path, "w", encoding="utf-8") as f:
                f.write(export_data)
