import requests
import time
import hmac
import base64
import urllib.parse
import json
import hashlib


class DingTalk:
    def __init__(self, secret, dingtalk_token):
        self.secret = secret
        self.dingtalk_token = dingtalk_token

    def generate_dingtalk_signature(self):
        timestamp = str(round(time.time() * 1000))
        string_to_sign = f"{timestamp}\n{self.secret}"
        hmac_code = hmac.new(
            self.secret.encode(), string_to_sign.encode(), digestmod=hashlib.sha256
        ).digest()
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
        return timestamp, sign

    # ========== 发送钉钉通知 ==========
    def send_dingtalk_links(self, ding_msg='', ding_title=None):
        timestamp, sign = self.generate_dingtalk_signature()
        webhook = f"https://oapi.dingtalk.com/robot/send?access_token={self.dingtalk_token}&timestamp={timestamp}&sign={sign}"
        headers = {"Content-Type": "application/json"}

        payload = {
            "msgtype": "text",
            "text": {
                "content": ding_msg
            },
        }

        try:
            response = requests.post(webhook, headers=headers, data=json.dumps(payload))
            print("钉钉发送结果：", response.text)
        except Exception as e:
            print("钉钉发送失败：", e)
