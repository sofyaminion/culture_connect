from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from models import db, User, Event
import logging


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/sofya/PycharmProjects/git/.db'  # Путь к базе данных SQLite
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Отключение отслеживания изменений

db = SQLAlchemy(app)
migrate = Migrate(app, db)

with app.app_context():
    # Создаем все таблицы, определенные в моделях
    db.create_all()

# Создаем пользователей
user1 = User(username='user1', email='user1@example.com')
user1.set_password('password1')

user2 = User(username='user2', email='user2@example.com')
user2.set_password('password2')

user3 = User(username='user3', email='user3@example.com')
user3.set_password('password3')

# Добавляем пользователей в сессию и сохраняем изменения в базе данных
db.session.add(user1)
db.session.add(user2)
db.session.add(user3)
db.session.commit()



# Ваш код обработки запросов и маршрутов

@app.route('/')
def home():
    return 'Домашняя страница'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            # Аутентификация прошла успешно
            return redirect(url_for('home'))
        else:
            return render_template('login.html', message='Неверное имя пользователя или пароль')

    return render_template('login.html', message='')

@app.route('/create_user')
def create_user():
    # Создаем пользователя
    new_user = User(username='example', email='example@example.com', password='password')

    # Добавляем пользователя в сессию
    db.session.add(new_user)

    # Сохраняем изменения в базе данных
    db.session.commit()
    logging.debug("This is a debug message")

    return 'User created successfully!'

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Проверяем, существует ли пользователь с таким же именем пользователя или email
        if User.query.filter_by(username=username).first() is not None:
            return render_template('register.html', message='Username already exists')
        if User.query.filter_by(email=email).first() is not None:
            return render_template('register.html', message='Email already registered')

        # Создаем нового пользователя и сохраняем его в базе данных
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('home'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    # Код для выхода из системы
    return redirect(url_for('index'))

@app.route('/profile')
def profile():
    user = User.query.filter_by(username=username).first()
    if user is None:
        return 'User not found'
    return render_template('profile.html')

@app.route('/profile/edit', methods=['GET', 'POST'])
def edit_profile():
    # Получаем текущего пользователя из базы данных
    # В данном примере я предполагаю, что имя пользователя хранится в сеансе
    # Вы можете использовать другой механизм для определения текущего пользователя, если у вас он есть
    username_from_session = request.form.get('username_from_session')  # Получаем имя пользователя из сессии
    user = User.query.filter_by(username=username_from_session).first()
    if user is None:
        return 'User not found'

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']

        # Обновляем данные профиля пользователя
        user.username = username
        user.email = email
        db.session.commit()

        # После сохранения изменений перенаправляем пользователя на страницу профиля
        return redirect(url_for('profile', username=username))

    # Если метод запроса GET, отображаем форму редактирования профиля
    return render_template('edit_profile.html', username=user.username, email=user.email)

@app.route('/profile/<username>')
def view_profile(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        return 'User not found'
    return render_template('view_profile.html', username=user.username, email=user.email)

@app.route('/events')
def events():
    if request.method == 'POST':
        event_id = request.form.get('event_id')
        event = Event.query.get(event_id)
        if event:
            event.likes += 1
            db.session.commit()
    events = Event.query.all()
    return render_template('events.html', events=events)

@app.route('/events/<event_id>')
def event_details(event_id):
    event = Event.query.get(event_id)
    if event is None:
        return 'Event not found'
    return render_template('event_details.html', event=event)

@app.route('/event/<int:event_id>/like/<int:user_id>', methods=['POST'])
def like_person(event_id, user_id):
    event = Event.query.get(event_id)
    user = User.query.get(user_id)
    if event is None or user is None:
        return 'Event or user not found'
    event.attendees.append(user)
    db.session.commit()
    return redirect(url_for('event_details', event_id=event_id))

@app.route('/search')
def search():
    # Код для поиска событий по различным параметрам
    return render_template('search.html')

@app.route('/events/category/<category_id>')
def events_by_category(category_id):
    # Код для фильтрации событий по категориям
    return render_template('events_by_category.html')

def match():
    matched_events = []

    # Получаем список всех событий
    events = Event.query.all()

    # Получаем текущего пользователя (предположим, что имя пользователя сохранено в сессии)
    current_user = User.query.filter_by(username=session.get('username')).first()

    # Для каждого события проверяем, есть ли участники, которые лайкнули текущего пользователя,
    # и добавляем такие события в список matched_events
    for event in events:
        matched_attendees = [attendee for attendee in event.attendees if current_user in attendee.liked_by]
        if matched_attendees:
            matched_events.append({'event': event, 'matched_attendees': matched_attendees})

    return render_template('match.html', matched_events=matched_events)

@app.route('/dialog/<username>')
def dialog(username):
    # Здесь может быть код для открытия диалога с выбранным пользователем
    return f"You are now in dialog with {username}."


@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.json
    sender_id = data.get('sender_id')
    recipient_id = data.get('recipient_id')
    message_text = data.get('message_text')


    return jsonify({'success': True, 'message': 'Message sent successfully'})

@app.route('/get_messages/<int:user_id>', methods=['GET'])
def get_messages(user_id):
    # Здесь можно добавить логику для получения сообщений из базы данных
    # Например, запросить все сообщения, где user_id является отправителем или получателем

    # Вернуть список сообщений в формате JSON
    return jsonify({'messages': messages})

@app.route('/like/<int:user_id>', methods=['POST'])
def like_user(user_id):
    # Получить текущего пользователя или его сеанс
    return jsonify({'success': True, 'message': 'User liked successfully'})

@app.route('/unlike/<int:user_id>', methods=['POST'])
def unlike_user(user_id):
    # Получить текущего пользователя или его сеанс
    return jsonify({'success': True, 'message': 'User unliked successfully'})


if __name__ == '__main__':
    app.run(debug=True)
