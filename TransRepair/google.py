from google_trans_new

GoogleAPI = "https://translate.google.com/"

if __name__ == "__main__":
    s = "你好"
    params = {
        'text': s,
        'hl': "zh-CN",
        'tl': "en",
        'op': "translate",
        'sl': "auto"
    }

    try:
        t = json.loads(requests.get(GoogleAPI, params).text)
        print(t)
    except:
        print("获取失败")