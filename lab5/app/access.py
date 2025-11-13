from functools import wraps
from flask import redirect, flash, url_for
from flask_login import current_user
from .repositories import UserRepository, RoleRepository
from .extensions import db

user_repository = UserRepository(db)

def check_rights(action):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Необходима авторизация', 'danger')
                return redirect(url_for('auth.login'))

            current_user_id = current_user.get_id()
            user = user_repository.get_by_id(current_user_id)

            if not user or not user.role:
                flash('Ошибка доступа к данным пользователя.', 'danger')
                return redirect(url_for('users.index'))

            allowed_actions = {
                'admin': ['create', 'edit', 'delete', 'view', 'logs_by_pages', 'logs_by_users'],
                'user': ['self_edit', 'self_view']
            }
            if user.role in allowed_actions:
                if (action in allowed_actions[user.role] or
                        (action == 'edit' and kwargs.get('user_id') == int(current_user_id) and 'self_edit' in
                         allowed_actions[user.role]) or
                            (action == 'view' and kwargs.get('user_id') == int(current_user_id) and 'self_view' in
                            allowed_actions[user.role])):
                    return f(*args, **kwargs)

            flash('У вас недостаточно прав для доступа к данной странице.', 'danger')
            return redirect(url_for('users.index'))

        return decorated_function

    return decorator