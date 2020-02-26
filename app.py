from flask import Flask, jsonify, request, render_template, redirect
import sqlite3
from flask import g
from datetime import datetime
import json, requests
import os
import firebase_admin
from firebase_admin import messaging, credentials
# from sqlalchemy import text

cred = credentials.Certificate("lottery-system-d6016-firebase-adminsdk-vgaex-e2665d1ef6.json")
firebase_admin.initialize_app(cred)

app = Flask(__name__)

dir_path = os.getcwd()
database = dir_path + '/db.sqlite'
print(database)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(database)
        return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.after_request
def add_headers(response):
    white_origin = ['https://www.quinielashoy.com', 'https://staging.quiniela.workers.dev',
                    'https://quiniela.quiniela.workers.dev', 'http://api.quinielashoy.com', 'http://localhost:8000',
                    'http://localhost:28100', 'http://localhost:3005', "*"]

    if 'HTTP_ORIGIN' in request.environ and request.environ['HTTP_ORIGIN'] in white_origin:
        response.headers.add('Content-Type', 'application/json')
        response.headers.add('Access-Control-Allow-Origin', request.headers['Origin'])
        response.headers.add('Access-Control-Allow-Methods', 'GET')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Expose-Headers', 'Content-Type,Content-Length,Authorization,X-Pagination')
    return response


@app.route('/')
def index():
    date = request.args.get('date')
    data = ''
    if date:
        requested_date = datetime.strptime(date, '%Y-%m-%d')
        filename = 'data/data-%s.json' % (requested_date.strftime("%Y-%m-%d"))
    else:
        filename = 'data/data-%s.json' % (datetime.now().strftime("%Y-%m-%d"))
        if not os.path.exists(filename):
            filename = 'data.json'

    try:
        with open(filename, 'r') as fp:
            data = json.load(fp)
    except Exception as e:
        print(e)

    if data:
        return jsonify(data)
    else:
        return {'error ': 'request in a while'}


@app.route('/ping')
def ping():
    return jsonify({'success': 'it works'}), 200

@app.route('/notify')
def hello():
    db = get_db()
    # sql = text('select * from messages')
    messages = db.execute('select * from messages')
    message_obj = {}
    for message in messages:
        message_obj[message[1]] = message[2]
    print(message_obj)
    return render_template('notification_form.html', data=message_obj)


@app.route('/save_notify', methods=['POST'])
def save_notify():
    primeria = request.form['primeria']
    matutina = request.form['matutina']
    vespertina = request.form['vespertina']
    nocturna = request.form['nocturna']

    db = get_db()
    print('db connection is ', db)
    sqliteConnection = sqlite3.connect(database)
    cursor = sqliteConnection.cursor()
    cursor.execute("""UPDATE messages SET message = ? WHERE category = 'Primeria'""", (primeria,))
    cursor.execute("""UPDATE messages SET message = ? WHERE category = 'Matutina'""", (matutina,))
    cursor.execute("""UPDATE messages SET message = ? WHERE category = 'Vespertina'""", (vespertina,))
    cursor.execute("""UPDATE messages SET message = ? WHERE category = 'Nocturna'""", (nocturna,))
    sqliteConnection.commit()

    return redirect('/notify')


@app.route('/subscribe', methods=['POST'])
def save_subscription():
    data = json.loads(request.data.decode())
    sqliteconnection = sqlite3.connect(database)
    cursor = sqliteconnection.cursor()

    # check device id exist else create new one
    cursor.execute("""select * from devices WHERE token= ?""", (data['token'],))
    result = cursor.fetchone()
    if result:
        device_id = result[0]
    else:
        cursor.execute("INSERT INTO devices(token) VALUES (?)", (data['token'],))
        sqliteconnection.commit()
        cursor.execute("""select * from devices WHERE token= ?""", (data['token'],))
        result = cursor.fetchone()
        device_id = result[0]

    print('device_id is ', device_id)
    categories = ",".join(map(str, data['categories']))
    print('categories are ', categories)
    # subscribe device for notifications
    cursor.execute("""UPDATE devices SET categories = ? WHERE id = ?""", (categories, device_id))
    sqliteconnection.commit()

    return jsonify({"message":"Notification has been saved","success":True})

@app.route('/send_all_notifications')
def send_all_notifications():

    send_notification("Primeria")
    send_notification('Matutina')
    send_notification('Vespertina')
    return send_notification('Nocturna')


@app.route('/send_primeria_notifications')
def send_primeria_notifications():

    return send_notification("Primeria")

    # sqliteconnection = sqlite3.connect(database)
    # cursor = sqliteconnection.cursor()
    # cursor.execute("""select * from messages WHERE category = 'Primeria'""")
    # result = cursor.fetchone()
    #
    #
    # devices = cursor.execute("""select * from devices""")
    # registration_tokens = [device[1] for device in devices]
    # print('registration_tokens', registration_tokens)
    #
    # url = "https://fcm.googleapis.com/fcm/send"
    #
    # for device in registration_tokens:
    #     # to = device[1]
    #     data = {
    #         "notification": {
    #             "title": "Firebase",
    #             "body": result[2],
    #             "click_action": "http://localhost:3000/",
    #             "icon": "http://url-to-an-icon/icon.png"
    #         },
    #         "to": device
    #     }
    #     response = requests.post(url, json.dumps(data), headers={
    #         "Authorization" : "key=AAAAgUfefDI:APA91bFXqTUJ7M_0L8qJ3ZUK6YWo6O9lybbwEeI_5eVDd13IR-72PoABYvERRJ-mB8sN7uYKO9lXSNG0DNrI9UIkTd4KRnTiMqqm_WOKvYqtlAIGr8nNmssr2lmIekGBrN-Vr_92-xjF",
    #         "Content-Type" :  "application/json"
    #     })
    # return jsonify({"success" : True}), 200


@app.route('/send_matutina_notifications')
def send_matutina_notifications():
    return send_notification('Matutina')

@app.route('/send_Vespertina_notifications')
def send_vespertina_notifications():
    return send_notification('Vespertina')

@app.route('/send_nocturna_notifications')
def send_nocturna_notifications():
    return send_notification('Nocturna')

def send_notification(category):
    sqliteconnection = sqlite3.connect(database)
    cursor = sqliteconnection.cursor()
    cursor.execute("""select * from messages WHERE category = ?""", (category,))
    result = cursor.fetchone()

    message_to_send = result[2]
    category_id = result[0]
    print(message_to_send)
    print(category_id)

    # GET THE DEVICES WHICH HAVE SELECTED CATEGORIES

    devices = cursor.execute("""select * from devices WHERE categories LIKE ? or categories LIKE '%0%'""", ('%'+str(category_id)+'%',))

    registration_tokens = [device[1] for device in devices]
    print('registration_tokens', registration_tokens)


    url = "https://fcm.googleapis.com/fcm/send"
    for device in registration_tokens:
        # to = device[1]
        data = {
            "notification": {
                "title": category,
                "body": message_to_send,
                "click_action": "https://www.quinielashoy.com/",
                "icon": "https://www.quinielashoy.com/icons/icon-48x48.png?v=8620d1fcfdcb742bea0354c017476e55"
            },
            "to": device
        }
        try:
            response = requests.post(url, json.dumps(data), headers={
            "Authorization": "key=AAAAgUfefDI:APA91bFXqTUJ7M_0L8qJ3ZUK6YWo6O9lybbwEeI_5eVDd13IR-72PoABYvERRJ-mB8sN7uYKO9lXSNG0DNrI9UIkTd4KRnTiMqqm_WOKvYqtlAIGr8nNmssr2lmIekGBrN-Vr_92-xjF",
            "Content-Type": "application/json"
            })
        except:
            return jsonify({"success": False}), 200

    return jsonify({"success": True}), 200




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=28100, debug=True)
