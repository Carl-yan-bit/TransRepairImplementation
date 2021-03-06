import requests
import random
import json
from hashlib import md5
import re
import time


'''
英译中,返回翻译数组，[{'src':'...','dst':'...'},...]
可以替换translationAPI中调用的接口来测试其他翻译软件，如google translation
'''


def translationBlackBox(query):
    time.sleep(1)
    """
    黑盒翻译模型
    :param query: 英文
    :return: 翻译结果
    """
    # 此处替换为自己的百度appid和appkey
    appid = '你的百度appid'
    appkey = '你的百度appkey'

    from_lang = 'en'
    to_lang = 'zh'

    endpoint = 'http://api.fanyi.baidu.com'
    path = '/api/trans/vip/translate'
    url = endpoint + path

    # Generate salt and sign
    def make_md5(s, encoding='utf-8'):
        return md5(s.encode(encoding)).hexdigest()
    salt = random.randint(32768, 65536)
    sign = make_md5(appid + query + str(salt) + appkey)

    # Build request
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    payload = {'appid': appid, 'q': query, 'from': from_lang, 'to': to_lang, 'salt': salt, 'sign': sign}

    # Send request
    r = requests.post(url, params=payload, headers=headers)
    result = r.json()

    # Show response
    return json.loads(json.dumps(result, indent=4, ensure_ascii=False))['trans_result']


if __name__ == "__main__":
    s = "I'm writing to express sincere gratitude to you all for your devotion and sacrifice in this battle against the Novel Coronavirus"
    s = re.sub(r"[^A-Za-z\s']", "", s)
    t = translationBlackBox(s)
    print(t[0]['dst'])
