import json
import os
import dingTalk


def load_config(file):
    if os.path.exists(file):
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def notice(msg):
    try:
        ding_talk = dingTalk.DingTalk(os.getenv('secret'), os.getenv('dingtalk_token'))
        ding_talk.send_dingtalk_links(ding_msg=msg)
        return True
    except Exception as e:
        print(e)
        return False
