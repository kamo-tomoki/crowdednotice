from flask import Flask, request, redirect, url_for, send_from_directory, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)
import os

from linebot.models.send_messages import ImageSendMessage

import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

#環境変数取得
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

UPLOAD_FOLDER = "./uploads"

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    send_message = event.message.text
    if send_message == "現在":
       line_bot_api.reply_message(
          event.reply_token,
          ((ImageSendMessage(original_content_url="https://d4xawcq9u1fih.cloudfront.net/data8.png",
                              preview_image_url="https://d4xawcq9u1fih.cloudfront.net/data8.png")),
            (TextSendMessage(text="（東京都政策企画局サイト様のデータ）"))
        ))
    elif send_message == "ワクチン":
        url = 'https://www.kantei.go.jp/jp/headline/kansensho/vaccine.html'
        response = requests.get(url=url)
        html = response.content

        soup = BeautifulSoup(html, "html.parser")
        
        data1 = soup.find_all('td')[6]
        data1String = data1.get_text()
        
        data2 = soup.find_all("td")[11]
        data2String = data2.get_text()

        date = soup.find_all("p")[2]
        dateString = date.get_text()
        line_bot_api.reply_message(
            event.reply_token,
            ((TextSendMessage(text="1回以上接種した人の割合："+ data1String)),
             (TextSendMessage(text="2回接種完了した人の割合："+ data2String)),
             (TextSendMessage(text="このデータは"+ dateString[10:19]+"のものです。\n首相官邸サイト様より")))
        )
        
        
    
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="正しく入力してください。")
        )


if __name__ == "__main__":
#    app.run()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)