import json
import re
from modeusauthmodule import ModeusAuthModule
from modeusauthmodule.types import Credentials
import httpx
import test_date
from datetime import datetime, timedelta
import jwt


def authorization(login, password):
    auth = ModeusAuthModule()
    token = auth.login(Credentials(email=login, password=password))
    return token


def search_user(input_search, token):
    url_search = 'https://narfu.modeus.org/schedule-calendar-v2/api/people/persons/search'
    headers_to_search = {'Authorization': f"Bearer {token}", "Content-Type": 'application/json'}

    mask = r"\w{8}-\w{4}-\w{4}-\w{4}-\w{12}"

    # Проверяем соответствие маске
    if re.match(mask, input_search):
        print("Соответствует маске")
        data_to_search = {"id": input_search}
        data_to_search = json.dumps(data_to_search)
        search = httpx.post(url=url_search, data=data_to_search, headers=headers_to_search)
        result_search = search.json()
        return [result_search['_embedded']['persons']]

    else:
        data_to_search = {"fullName": input_search}
        print("Не соответствует маске")
        data_to_search = json.dumps(data_to_search)
        search = httpx.post(url=url_search, data=data_to_search, headers=headers_to_search)
        result_search = search.json()

        try:
            count_results = len(result_search['_embedded']['persons'])
        except KeyError:
            count_results = 0
        if count_results >= 2:
            keys = ['fullName', 'id']
            print(
                f'Several users were found. Choose the correct one from this list and send id \n {[[fullName[key] for key in keys] for fullName in result_search["_embedded"]["persons"]]}')
            return search_user(input_search, token)
        elif count_results == 1:
            return result_search['_embedded']['persons']
        else:
            print('Something went wrong')
            return search_user(input_search, token)


def search_user_id(input, token):
    id_student = search_user(input, token)[0]["id"]
    return id_student


import psycopg2
from psycopg2.extensions import register_type, UNICODE

CONN_STR = ("host='localhost' dbname='test' user='postgres' password='12345'")


def create_table(table_name):
    register_type(UNICODE)
    conn = psycopg2.connect(CONN_STR)
    cursor = conn.cursor()
    create_table_query = f"""
    CREATE TABLE hsitas."{table_name}" (
        name_student VARCHAR(255),
        id_student VARCHAR(255),
        data VARCHAR(255)
    );
    """
    cursor.execute(create_table_query)
    conn.commit()
    cursor.close()
    conn.close()
    print(f"Table '{table_name}' created successfully.")


def get_students_postgres(table_name):
    register_type(UNICODE)
    conn = psycopg2.connect(CONN_STR)
    cursor = conn.cursor()
    # Выполняем SQL-запрос для получения данных из таблицы
    query = f"""SELECT id, data FROM hsitas."{table_name}";"""
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results


def add_students(table_name, data_list):
    register_type(UNICODE)
    conn = psycopg2.connect(CONN_STR)
    cursor = conn.cursor()
    for data in data_list:
        insert_query = f"""INSERT INTO hsitas."{table_name}" (name_student, id_student, data) VALUES ('{data[0]}', '{data[1]}', null);"""
        cursor.execute(insert_query)
    conn.commit()
    cursor.close()
    conn.close()
    print(f"Table '{table_name}' successfully.")


def print_lessons(id_student, token):
    url_search = 'https://narfu.modeus.org/schedule-calendar-v2/api/calendar/events/search'
    headers_to_search = {'Authorization': f"Bearer {token}", "Content-Type": 'application/json'}
    dates = test_date.get_dates_schedule(datetime.now() + timedelta(days=5))
    data_to_search = {"size": 500,
                      "timeMin": f"{dates[0]}",
                      "timeMax": f"{dates[1]}",
                      "attendeePersonId": [f"{id_student}"]}
    data_to_search = json.dumps(data_to_search)
    search = httpx.post(url=url_search, data=data_to_search, headers=headers_to_search)
    result_search = search.json()
    return result_search


def get_course_unit_realization(id_student, token):
    return print_lessons(id_student, token)['_embedded']['events'][0]['_links']['course-unit-realization']['href'][
           1:]  # надо разобраться с тем, что сейчас оно выводит первую пару


def get_lesson_id(id_student, token):
    return print_lessons(id_student, token)['_embedded']['events'][0]['id']


def send_teacher_mark(input, token):  # функция не доделана, надо разобраться
    for student in get_students_postgres("0aa214e1-9d6d-46bd-a1be-84d9d4fe7688"):
        student_id = student[0]
        student_code = student[1]
    url_search = f'https://narfu.modeus.org/results-control/api/v2/results/course-unit-realizations/{get_course_unit_realization(input, token)}/events/{get_lesson_id(input, token)}/attendances'
    headers_to_search = {'Authorization': f"Bearer {token}", "Content-Type": 'application/json'}

    data_to_search = {"requests": [{"studentId": f"{student_id}", "attendanceCode": f"{student_code}"}]}
    data_to_search = json.dumps(data_to_search)
    search = httpx.put(url=url_search, data=data_to_search, headers=headers_to_search)
    return search.json()


def get_students_modeus(lesson_id, token):
    url_search = f'https://narfu.modeus.org/schedule-calendar-v2/api/calendar/events/{lesson_id}/attendees'
    headers_to_search = {'Authorization': f"Bearer {token}", "Content-Type": 'application/json'}
    search = httpx.get(url=url_search, headers=headers_to_search)
    search_formed = search.json()
    list_students = []
    for student in search_formed:
        if student['roleId'] == 'STUDENT':
            list_students.append((student['fullName'], student['studentId']))
        elif student['roleId'] == 'TEACH':
            print('teacher')
    return list_students


def get_user_id(token):
    return jwt.decode(token, algorithms=['RS256'], options={'verify_signature': False})['person_id']


if __name__ == '__main__':
    token = authorization('kotkin.d1@edu.narfu.ru', 'k@to6{pUSA')
    # test = jwt.decode(token, algorithms=['RS256'], options={'verify_signature': False})['person_id']
    # print(type(test))
    # paras = para = print_lessons('Коткин Денис', token)['_embedded']['events']
    # for para in paras:
    #     para = para['id']
    #     try:
    #         create_table(para)
    #         add_students(para, get_students_modeus(para, token))
    #     except:
    #         add_students(para, get_students_modeus(para, token))
