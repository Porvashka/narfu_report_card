from flask import Flask, request, redirect, url_for, render_template, jsonify
import psycopg2
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


@app.route('/marks', methods=['GET', 'POST'])
def index(token):
    if request.method == 'POST':
        idd = request.form['id']
        id_lesson = request.form['id_lesson']
        new_data = request.form['data']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(f"""UPDATE hsitas."{id_lesson}" SET data = %s WHERE name_student = %s""", (new_data, idd))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for(endpoint='main', token=token, _method='POST'))


@app.route('/main/<token>', methods=['GET', 'POST'])
def main(token):
    # token = request.headers.get('Authorization')
    lessons = print_lessons(get_user_id(token), token)['_embedded']
    lessons_events = lessons['events']
    lessons_sorted = sorted(lessons_events, key=lambda x: x["start"])
    grouped_data = OrderedDict()

    for item in lessons_sorted:
        date_object = datetime.fromisoformat(item["start"])
        day = str(date_object.date())
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
    if request.method == 'POST':
        id_lesson = request.form['id_lesson']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(f"""SELECT name_student, data FROM hsitas."{id_lesson}";""")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('index.html', grouped_data=grouped_data, rows=rows, token=token, id_lesson=id_lesson)
    return render_template('index.html', grouped_data=grouped_data, token=token)


if __name__ == '__main__':
    app.run(debug=True)
