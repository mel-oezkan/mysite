from flask import Blueprint
from flask import redirect
from flask import request
from flask import url_for
from flask import Response

import re
import requests

from flaskr.db import get_db



bp = Blueprint("subBot", __name__)

token = "1275132898:AAHMM_0JXuzjU_ddRa5POsUCDgZC68Hsdmg"

def checkUser(username, chatId):

    db = get_db()
    user = db.execute(
        'SELECT username, chatId'
        ' FROM user'
        ' WHERE username = ?',
        (username,),
    ).fetchone()

    if user == None:
        return "Invalid username"
    else:
        if user["chatId"] == 0:
            db.execute(
                'UPDATE user SET chatId = ?'
                ' WHERE username = ?',
                (chatId, username)
            )
            db.commit()
            return "Successfully added you to the database :)"
        else:
            return "There is already a entry with your name. You can delete it on the webpage"


def checkIfInDB(chatId):
    db = get_db()
    user = db.execute(
        'SELECT username, chatId'
        ' FROM user'
        ' WHERE chatId = ?',
        (chatId,),
    ).fetchone()

    print(user)


def parse_message(message):
    chat_id = message["message"]["chat"]["id"]
    txt = message["message"]["text"]

    register_pattern = r'^/register (([a-zA-Z]|[0-9])|[_]){2,20}$'
    join_pattern = r'^/join$'

    register = re.match(register_pattern, txt)
    join = re.match(join_pattern, txt)

    if register:
        # sets the symbol to the username
        symbol = register[0].split("/register ")[1]
    elif join:
        # the bot needs to somehow get the time and subject
        symbol = "join something"
    else:
        symbol = ""

    return chat_id, symbol


def send_message(chat_id, text="bla-bal-bla"):
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    payload = {"chat_id": chat_id, "text": text}

    r = requests.post(url, json=payload)
    return r


@bp.route(f"/{token}", methods=["POST", "GET"])
def index():

    if request.method == "POST":
        # get the message and turn it into json
        msg = request.get_json()
        # parse the message
        chat_id, userMessage = parse_message(msg)

        if not userMessage or userMessage == "join something":
            send_message(chat_id, "Wrong Input. Try: /register username")
            return Response("ok", status=200)


        answer = checkUser(userMessage, chat_id)
        send_message(chat_id, answer)

        return Response('ok', status=200)

    return redirect(url_for("blog.index"))







