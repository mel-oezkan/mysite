# This is a comment
#
from flask import Blueprint
from flask import g
from flask import render_template
from flask import request
from flask import url_for
from flask import jsonify
from flask import session
from flask import Response
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db
from flaskr.subBot import send_message

import os


bp = Blueprint("blog", __name__)


@bp.route("/")
# In order to view the events, log in is required
# This measure minimizes the risk that people without accout show up at events
@login_required
def index():
    """Show all the posts, most recent first."""
    db = get_db()
    meets = db.execute(
        'SELECT meet.id, datum, from_time, to_time, study_subject, place, created, author_id, realName, current_participants, max_participants'
        #' FROM meet m JOIN user u ON m.author_id = u.id'
        ' FROM meet'
        ' INNER JOIN user ON meet.author_id = user.id'
        # Only print posts happening now or in the future
        ' WHERE datum >= CURRENT_DATE'
        ' ORDER BY created DESC'
    ).fetchall()

    participants = db.execute(
        'SELECT user.realName, participant.study_subject, participant.from_time, participant.to_time, participant.meet_id'
        ' FROM participant'
        ' INNER JOIN meet ON participant.meet_id = meet.id'
        ' INNER JOIN user ON participant_id = user.id '
        ' ORDER BY participant.created DESC'
    ).fetchall()


    user_id = int(session.get("user_id"))

    # every post in which curren user is in
    inPosts = db.execute(
        'SELECT meet.id'
        ' FROM participant'
        ' INNER JOIN meet ON participant.meet_id = meet.id'
        ' INNER JOIN user ON participant_id = user.id '
        ' WHERE participant_id = ?',
        (user_id,),
    ).fetchall()

    return render_template("blog/index.html", meets=meets, participants=participants, inPosts=inPosts)


def getParticipants(id):

    parts = (
        get_db()
        .execute(
            'SELECT meet.author_id, participant.participant_id'
            ' FROM participant'
            ' INNER JOIN meet ON participant.meet_id = meet.id'
            ' INNER JOIN user ON participant_id = user.id '
            " WHERE participant.meet_id = ?",
            (id,),
        )
        .fetchall()
    )

    if parts is None:
        abort(404, f"Post id {id} doesn't exist.")

    return parts


# returns the current and max participants
def getAmount(id):
    participantAmounts = (
        get_db()
        .execute(
            'SELECT current_participants, max_participants'
            ' FROM meet'
            " WHERE id = ?",
            (id,),
        )
        .fetchone()
    )

    if participantAmounts is None:
        abort(404, f"Post id {id} doesn't exist.")

    return participantAmounts


@bp.route('/process', methods=['POST'])
def process():
    print("process function was called")

    date = request.form['date']
    from_t = request.form['from_t']
    to_t = request.form['to_t']
    subject = request.form['subject']
    place = request.form['place']
    maxPeople = request.form['maxPeople']


    if date and from_t and to_t and subject and place and maxPeople:

        try:

            db = get_db()
            db.execute(
                'INSERT INTO meet (datum, from_time, to_time, study_subject, place, max_participants, author_id)'
                ' VALUES (?, ?, ?, ?, ?, ?, ?)',
                (date, from_t, to_t, subject ,place, maxPeople, g.user['id'])
            )
            db.commit()

            userChats = db.execute(
                'SELECT chatId, id'
                ' FROM user'
            ).fetchall()

            name = db.execute(
                'SELECT realName'
                ' FROM user'
                ' WHERE id = ?',
                (g.user["id"],),
            ).fetchone()

            author_name = name["realName"]

            for user in userChats:
                if user["chatId"] != 0 and user["id"] != g.user["id"]:
                    send_message(user["chatId"], text=f"{author_name} has created a new event. So if you have time on {date} from around {from_t} until {to_t} add yourself to the event. Check it out on: substudy.pythonanywhere.com")
                    return Response('ok', status=200)


            # return jsonify({'name': place})
        except Exception as e:
            print(e)

    else:
        print("something is missing")

    return jsonify({'error' : "Missing data!"})


# Add user with ajax
@bp.route('/addParticipant', methods=['POST'])
def addParticipant():

    name = request.form['name']
    subject = request.form['parSubject']
    from_t = request.form['parFrom']
    to_t = request.form['parTo']
    meetID = request.form['meetId']

    amounts = getAmount(meetID)

    if amounts["current_participants"] == amounts["max_participants"]:
        return jsonify({'error' : "The event is full"})

    for i in getParticipants(meetID):
        if g.user['id'] ==  i["author_id"] or g.user['id'] == i["participant_id"]:
            return jsonify({'error' : "You are already joined this event"})

    if name and from_t and to_t and subject and meetID:

        try:
            db = get_db()
            db.execute(
                'INSERT INTO participant (participant_id, meet_id, study_subject, from_time, to_time)'
                ' VALUES (?, ?, ?, ?, ?)',
                (g.user['id'], meetID, subject, from_t, to_t)
            )
            db.commit()



            db = get_db()
            db.execute(
                'UPDATE meet SET current_participants = current_participants + 1'
                ' WHERE id = ?',
                (meetID,)
            )
            db.commit()

            print("debug 1")


            return jsonify({'name': "place"})
        except Exception as e:
            print(e)

    else:
        print("something is missing")

    print("missing data")
    return jsonify({'error' : "Missing data!"})


@bp.route('/delete', methods=['POST'])
def delete():

    meetId = request.form['meetId']

    print(meetId)

    db = get_db()
    db.execute("DELETE FROM meet WHERE id = ?", (meetId,))
    db.commit()

    return jsonify({'message': "deleted"})

# Delete every post in the past
@bp.route('/deletePastEvents')
def deletePastEvents():
    print("Test")


@bp.route('/teleBot')
@login_required
def teleBot():
    return render_template("blog/teleBot.html")


@bp.route('/adminArea')
@login_required
def adminArea():
    db = get_db()
    meets = db.execute(
        'SELECT meet.id, datum, from_time, to_time, study_subject, place, created, author_id, realName, current_participants, max_participants'
        ' FROM meet'
        ' INNER JOIN user ON meet.author_id = user.id'
        ' ORDER BY created DESC'
    ).fetchall()

    userChats = db.execute(
        'SELECT username, realName, chatId, id'
        ' FROM user'
    ).fetchall()

    users = db.execute(
        'SELECT username, id, realName'
        ' FROM user'
    ).fetchall()

    return render_template("blog/adminArea.html", meets=meets, userChats=userChats, users=users)



# not important
# some script that loads static files
@bp.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)

def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(bp.root_path,
                                endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)
