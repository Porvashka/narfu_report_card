from flask import Flask, request, redirect, url_for, render_template, jsonify
import psycopg2
import psycopg2.extras
from auth import get_user_id, authorization, get_students_postgres, print_lessons
from datetime import datetime
from collections import OrderedDict


app = Flask(__name__)
app.secret_key = 'your_secret_key_here'


def get_db_connection():
    conn = psycopg2.connect(
        dbname="test",
        user="postgres",
        password="12345",
        host="localhost",
        port="5432"
    )
    return conn


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        token = authorization(login, password)
        return redirect(url_for('main', token=token))
    return render_template('login.html')

@app.route('/main/<token>', methods=['GET', 'POST'])
def main(token):
    lessons = print_lessons(get_user_id(token), token)['_embedded']
    lessons_events = lessons['events']
    lessons_sorted = sorted(lessons_events, key=lambda x: x["start"])
    grouped_data = OrderedDict()

    for item in lessons_sorted:
        date_object = datetime.fromisoformat(item["start"])
        match date_object.weekday():
            case 0: day = f"Понедельник {date_object.date()}"
            case 1: day = f"Вторник {date_object.date()}"
            case 2: day = f"Среда {date_object.date()}"
            case 3: day = f"Четверг {date_object.date()}"
            case 4: day = f"Пятница {date_object.date()}"
            case 5: day = f"Суббота {date_object.date()}"
            case 6: day = f"Воскресенье {date_object.date()}"
        if day not in grouped_data:
            grouped_data[day] = {"objects": []}
        grouped_data[day]["objects"].append(item)
    courses_links = lessons['course-unit-realizations']
    for day, data in grouped_data.items():
        for lesson in data["objects"]:
            for course_link in courses_links:
                if lesson['_links']['course-unit-realization']['href'][1:] == course_link['id']:
                    lesson['course-name'] = course_link['name']
                    break
    return render_template('index.html', grouped_data=grouped_data, token=token)
@app.route('/table/<table_name>', methods=['GET'])
def table(table_name):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(f"""SELECT id_student, name_student, data FROM hsitas."{table_name}";""")
    records = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(records)

@app.route('/update', methods=['POST'])
def update():
    table_name = request.json['table_name']
    record_id = request.json['id']

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(f"""SELECT data FROM hsitas."{table_name}" WHERE id_student = %s""", (record_id,))
    current_value = cur.fetchone()['data']

    new_value = 'PRESENT' if current_value == 'ABSENT' else 'ABSENT'

    cur.execute(f"""UPDATE hsitas."{table_name}" SET data = %s WHERE id_student = %s""", (new_value, record_id))
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({'status': 'success', 'new_value': new_value})
if __name__ == '__main__':
    app.run(debug=True)
