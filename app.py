from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from models import db, User, Event, Profile, Like, Message, Admin
import logging
from flask_login import login_user, logout_user, LoginManager, login_required, current_user
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)
login_manager = LoginManager(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/sofya/PycharmProjects/git/.db'  # Путь к базе данных SQLite
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Отключение отслеживания изменений

migrate = Migrate(app, db)

@login_manager.user_loader
def load_user(user_id):
    # Загрузка пользователя из базы данных или другого источника данных
    return db.session.get(User, int(user_id))

def create_app():
    db.init_app(app)
    with app.app_context():
        db.create_all()

        if not User.query.filter_by(username='user1').first():
            user1 = User(username='user1', email='user1@example.com')
            user1.set_password('password1')
            db.session.add(user1)

        if not User.query.filter_by(username='user2').first():
            user2 = User(username='user2', email='user2@example.com')
            user2.set_password('password2')
            db.session.add(user2)

        if not User.query.filter_by(username='user3').first():
            user3 = User(username='user3', email='user3@example.com')
            user3.set_password('password3')
            db.session.add(user3)

        if not Admin.query.filter_by(username='admin').first():
            admin = Admin(username='admin', email='admin@example.com')
            admin.set_password('admin')
            db.session.add(admin)

        if not Event.query.filter_by(name='Воркшоп по веб-разработке').first():
            workshop = Event(name='Воркшоп по веб-разработке', date=datetime(2024, 4, 1),
                             location='Место проведения',
                             description='Описание события')
            db.session.add(workshop)

        if not Event.query.filter_by(name='Конференция по искусственному интеллекту').first():
            conference = Event(name='Конференция по искусственному интеллекту', date=datetime(2024, 5, 15),
                               location='Место проведения', description='Описание события')
            db.session.add(conference)

        if not Event.query.filter_by(name='Фестиваль музыки и искусства').first():
            festival = Event(name='Фестиваль музыки и искусства', date=datetime(2024, 7, 20),
                             location='Место проведения', description='Описание события')
            db.session.add(festival)

        db.session.commit()

    # Ваш код обработки запросов и маршрутов

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/home')
    @login_required
    def home():
        return render_template('home.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            user = User.query.filter_by(username=username).first()
            if user and user.check_password(password):
                login_user(user)
                # Аутентификация прошла успешно
                app.logger.info(f"Пользователь {user.username} успешно аутентифицирован.")
                return redirect(url_for('home'))
            else:
                return render_template('login.html', message='Неверное имя пользователя или пароль')
            session['username'] = username

        return render_template('login.html', message='')

    @app.route('/reset_password', methods=['GET', 'POST'])
    def reset_password():
        if request.method == 'POST':
            username = request.form['username']
            email = request.form['email']
            new_password = request.form['new_password']

            # Проверяем, существует ли пользователь с указанным логином и почтой
            user = User.query.filter_by(username=username, email=email).first()
            if user:
                # Устанавливаем новый пароль для пользователя
                user.set_password(new_password)
                db.session.commit()
                flash('Пароль успешно изменен.', 'success')
                return redirect(url_for('login'))
            else:
                flash('Пользователь с указанными данными не найден.', 'error')

        return render_template('reset_password.html')

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']

            # Проверяем, существует ли пользователь с таким же именем пользователя или email
            existing_user = User.query.filter_by(username=username).first()
            existing_email = User.query.filter_by(email=email).first()

            if existing_user:
                return render_template('register.html', message='Username already exists')
            elif existing_email:
                return render_template('register.html', message='Email already registered')
            else:
                # Создаем нового пользователя и сохраняем его в базе данных
                new_user = User(username=username, email=email)
                new_user.set_password(password)
                db.session.add(new_user)
                db.session.commit()

            return redirect(url_for('home'))
        return render_template('register.html')

    @app.route('/logout')
    def logout():
        logout_user()
        # Код для выхода из системы
        return redirect(url_for('index'))

    @app.route('/profile/<username>')
    @login_required
    def profile(username):
        # Получаем текущего пользователя
        current_user_username = current_user.username

        # Получаем пользователя из базы данных
        user = User.query.filter_by(username=username).first()
        if user is None:
            return 'User not found'

        # Проверяем, является ли текущий пользователь администратором
        admin = Admin.query.filter_by(username=current_user_username).first()
        if admin:
            # Показываем профиль пользователя администратору
            return render_template('profile.html', username=user.username, email=user.email)
        else:
            # Проверяем, является ли запрошенный профиль текущим пользователем
            if username != current_user_username:
                return 'You can only view your own profile'
            else:
                # Показываем профиль текущего пользователя
                return render_template('profile.html', username=user.username, email=user.email)

    @app.route('/profile/edit/<username>', methods=['GET', 'POST'])
    @login_required
    def edit_profile(username):
        # Проверяем, имеет ли текущий пользователь право редактировать профиль
        if current_user.username != username:
            return 'You are not authorized to edit this profile'

        user = User.query.filter_by(username=username).first()
        if user is None:
            return 'User not found'

        if request.method == 'POST':
            new_username = request.form['username']
            new_email = request.form['email']

            # Обновляем данные профиля пользователя
            user.username = new_username
            user.email = new_email
            db.session.commit()

            # После сохранения изменений перенаправляем пользователя на страницу профиля
            return redirect(url_for('profile', username=new_username))

        # Если метод запроса GET, отображаем форму редактирования профиля
        return render_template('edit_profile.html', username=user.username, email=user.email)

    @app.route('/profile/<username>')
    @login_required
    def view_profile(username):
        user = User.query.filter_by(username=username).first()
        if user is None:
            return 'User not found'
        return render_template('view_profile.html', username=user.username, email=user.email)


    @app.route('/events', methods=['GET', 'POST'])
    @login_required
    def events():

        if request.method == 'POST':
            event_id = request.form.get('event_id')
            event = Event.query.get(event_id)
            if event:
                event.likes += 1
                db.session.commit()

        current_user_username = current_user.username

        # Проверяем, является ли текущий пользователь администратором
        admin = Admin.query.filter_by(username=current_user_username).first()

        # Отображаем список событий
        events = Event.query.all()
        return render_template('events.html', events=events, admin=admin)

    @app.route('/add_event', methods=['GET', 'POST'])
    @login_required
    def add_event():
        if request.method == 'POST':
            # Получаем данные формы добавления события
            name = request.form['name']
            date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
            location = request.form['location']
            description = request.form['description']

            # Создаем новое событие и сохраняем его в базе данных
            new_event = Event(name=name, date=date, location=location, description=description)
            db.session.add(new_event)
            db.session.commit()

            flash('Событие успешно добавлено!', 'success')
            return redirect(url_for('events'))

        return render_template('add_event.html')

    @app.route('/events/<event_id>')
    @login_required
    def event_details(event_id):
        event = Event.query.get(event_id)
        if event is None:
            return 'Event not found'
        return render_template('event_details.html', event=event)

    @app.route('/event/<int:event_id>/like/<int:user_id>', methods=['POST'])
    @login_required
    def like_person(event_id, user_id):
        event = Event.query.get(event_id)
        user = User.query.get(user_id)
        if event is None or user is None:
            return 'Event or user not found'
        event.attendees.append(user)
        db.session.commit()
        return redirect(url_for('event_details', event_id=event_id))

    @app.route('/search')
    @login_required
    def search():
        # Код для поиска событий по различным параметрам
        return render_template('search.html')

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
    @login_required
    def dialog(username):
        # Здесь может быть код для открытия диалога с выбранным пользователем
        return f"You are now in dialog with {username}."


    @app.route('/send_message', methods=['POST'])
    @login_required
    def send_message():
        data = request.json
        sender_id = data.get('sender_id')
        recipient_id = data.get('recipient_id')
        message_text = data.get('message_text')


        return jsonify({'success': True, 'message': 'Message sent successfully'})

    @app.route('/get_messages/<int:user_id>', methods=['GET'])
    @login_required
    def get_messages(user_id):
        # Здесь можно добавить логику для получения сообщений из базы данных
        # Например, запросить все сообщения, где user_id является отправителем или получателем

        # Вернуть список сообщений в формате JSON
        return jsonify({'messages': messages})

    @app.route('/like/<int:user_id>', methods=['POST'])
    @login_required
    def like_user(user_id):
        # Получить текущего пользователя или его сеанс
        return jsonify({'success': True, 'message': 'User liked successfully'})

    @app.route('/unlike/<int:user_id>', methods=['POST'])
    @login_required
    def unlike_user(user_id):
        # Получить текущего пользователя или его сеанс
        return jsonify({'success': True, 'message': 'User unliked successfully'})


if __name__ == '__main__':
    create_app()
    app.run(debug=True)
