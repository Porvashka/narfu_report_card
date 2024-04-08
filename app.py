from flask import Flask, request, redirect, url_for, render_template
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Замените на ваш секретный ключ

login_manager = LoginManager()
login_manager.init_app(app)

# Пример класса модели пользователя
class User(UserMixin):
    def __init__(self, id, username, password, last_name, first_name, middle_name, group_number):
        self.id = id
        self.username = username
        self.password = password
        self.last_name = last_name
        self.first_name = first_name
        self.middle_name = middle_name
        self.group_number = group_number

# Пример функции загрузки пользователя из JSON
def load_user(user_id):
    with open('users.json', 'r') as f:
        users = json.load(f)
        user_data = users.get(user_id)
        if user_data:
            return User(user_id, user_data['username'], user_data['password'],
                        user_data['last_name'], user_data['first_name'],
                        user_data['middle_name'], user_data['group_number'])

@login_manager.user_loader
def load_user_by_id(user_id):
    return load_user(user_id)

# Функция для добавления новых пользователей из файла new_users.json
def add_new_user(user_data):
    with open('users.json', 'r+') as users_file:
        users_data = json.load(users_file)
        users_data.update(user_data)
        users_file.seek(0)
        json.dump(users_data, users_file)
        users_file.truncate()


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

# Маршрут для входа в систему
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['login']
        password = request.form['password']
        with open('users.json', 'r') as f:
            users = json.load(f)
            for user_id, user_data in users.items():
                if user_data['username'] == username and user_data['password'] == password:
                    user = load_user(user_id)
                    login_user(user)
                    return redirect(url_for('dashboard'))
        return 'Invalid username or password'
    return render_template('index.html')

# Маршрут для выхода из системы
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return 'Logged out successfully'

# Защищенный маршрут
@app.route('/dashboard')
@login_required
def dashboard():
    schedule_data = [
        ("Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"),
        ("Занятие 1", "Занятие 3", "", "", "Занятие 6", ""),
        ("Занятие 2", "", "", "", "", ""),
        ("", "", "", "Занятие 5", "", ""),
        ("", "", "Занятие 4", "", "", ""),
        ("", "", "", "", "", ""),
        ("", "", "", "", "Занятие 7", "")]
    return render_template('about.html', schedule_data=schedule_data)

@app.route('/add_user', methods=['GET', 'POST'])
@login_required
def add_user():
    if request.method == 'POST':
        user_data = {
            request.form['id']: {
                'id': request.form['id'],
                'username': request.form['username'],
                'password': request.form['password'],
                'last_name': request.form['last_name'],
                'first_name': request.form['first_name'],
                'middle_name': request.form['middle_name'],
                'group_number': request.form['group_number']
            }
        }
        add_new_user(user_data)
        return redirect(url_for('dashboard'))
    return render_template('add_user.html')

if __name__ == '__main__':
    app.run(debug=True)
