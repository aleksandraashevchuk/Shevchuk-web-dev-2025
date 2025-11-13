from flask import Flask, render_template, session, request, redirect, url_for, flash, Blueprint
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from .repositories import UserRepository
from .extensions import db
from .extensions import login_manager
from .before_request import before_request
user_repository = UserRepository(db)

bp = Blueprint('auth', __name__, url_prefix='/auth')


login_manager.login_view = 'auth.login'
login_manager.login_message = 'Для доступа к запрашиваемой странице необходимо пройти процедуру аутентификации!'
login_manager.login_message_category = 'warning'

class User(UserMixin):
    def __init__(self, user_id, login):
        self.id = user_id
        self.login = login

@login_manager.user_loader
def load_user(user_id):
    user = user_repository.get_by_id(user_id)
    if user is not None:
        return User(user.id, user.username)
    return None

@bp.route('/login', methods=['GET', 'POST'])
@before_request()
def login():
    if request.method == 'POST':
        login = request.form.get('username')
        password = request.form.get('password')
        remember_me = request.form.get('remember_me') == 'on'

        user = user_repository.get_by_username_and_password(login, password)
        if user is not None:
            login_user(User(user.id, user.username), remember=remember_me)
            flash('Вы успешно аутентифицированы!', 'success')
            if request.args.get('next'):
                return redirect(request.args.get('next'))
            return redirect(url_for('users.index'))
        flash('Пользователь не найден, проверьте корректность введенных данных', 'danger')
        return render_template('auth/auth.html')
    return render_template('auth/auth.html')

@bp.route('/logout')
@before_request()
def logout():
    logout_user()
    return redirect(url_for('users.index'))


