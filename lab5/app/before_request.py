from functools import wraps
from flask import redirect, flash, url_for, request
from flask_login import current_user
from .repositories import UserRepository, RoleRepository, LogsRepository
from .extensions import db

logs_repository = LogsRepository(db)


def before_request():
    def decorator(view_func):
        @wraps(view_func) # сохранение метаданных оригинальной функции
        def wrapped_view(*args, **kwargs):
            try:
                user_id = current_user.get_id() if current_user.is_authenticated else None
                if not request.path.startswith('/static/'):
                    logs_repository.create(request.path, user_id)
            except Exception as e:
                print(f"Ошибка при логировании посещения: {str(e)}")

            return view_func(*args, **kwargs)

        return wrapped_view

    return decorator