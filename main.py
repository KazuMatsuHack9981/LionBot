from flask import Flask, request, abort
from pathlib import Path
import os
import sys
import json


from linebot import (
	LineBotApi, WebhookHandler
)

from linebot.exceptions import (
	InvalidSignatureError
)

from linebot.models import (
	MessageEvent, TextMessage, TextSendMessage, ImageMessage, ImageSendMessage
)





#Flaskの起動
app = Flask(__name__)


#環境変数取得
CHANNEL_ACCESS_TOKEN = os.environ["CHANNEL_ACCESS_TOKEN"]
CHANNEL_SECRET       = os.environ["CHANNEL_SECRET"]

if CHANNEL_ACCESS_TOKEN is None:
	print("Specify CHANNEL_ACCESS_TOKEN as environment variable!");
	sys.exit(1);
if CHANNEL_SECRET is None:
	print("Specify CHANNEL_SECRET as environment variable!");
	sys.exit(1);



line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)





#処理内容

#"/"(root_path)をGETリクエストを送った時の処理
@app.route("/")
def hello_world():
	return "hello world!"


@app.route("/callback", methods=['POST'])
def callback():
	signature = request.headers["X-Line-Signature"]
	body = request.get_data(as_text=True)
	app.logger.info("Request body: "+body)
	
	try:
		handler.handle(body, signature)
	except InvalidSignatureError:
		abort(400)
	
	return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
	word = event.message.text
	line_bot_api.reply_message(
		event.reply_token,
		TextSendMessage(text=word)
	)


@handler.add(MessageEvent, message=ImageMessage)
def handle_image(event):
	message_id = event.message.id
	message_content = line_bot_api.get_message_content(message_id)

	#画像の保存
	#Flaskにより画像はstatic配下の以下のパスに保存される
	with open(Path(f"static/images/{message_id}.jpg").absolute(), "wb") as f:
		#バイナリを1024ずつ書き込む
		for chunk in message_content.iter_content():
			f.write(chunk)

	line_bot_api.reply_message(
		event.reply_token,
		ImageSendMessage(
			original_content_url = f"https://lionpro-linebot.herokuapp.com/{message_id}.jpg",
			preview_image_url = f"https://lionpro-linebot.herokuapp.com/{message_id}.jpg"
		)
	)





#main関数
if __name__ == "__main__":
	port = int(os.getenv("PORT"))
	app.run(host="0.0.0.0", port=port)


