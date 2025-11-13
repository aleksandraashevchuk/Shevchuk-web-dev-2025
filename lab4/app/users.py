import re
from flask import Flask, render_template, session, request, redirect, url_for, flash, Blueprint
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from mysql import connector

from .repositories import UserRepository, RoleRepository
from .extensions import db

user_repository = UserRepository(db)
role_repository = RoleRepository(db)

bp = Blueprint('users', __name__, url_prefix='/users')

def validate_login(login):
    errors = []
    if not login:
        errors.append('Поле не может быть пустым')
    elif not re.match(r'^[A-Za-z0-9]{5,}$', login):
        errors.append('Логин должен содержать только латинские буквы и цифры, минимум 5 символов')
    return errors

def validate_password(password):
    errors = []
    if not password:
        errors.append('Поле не может быть пустым')
    elif len(password) < 8 or len(password) > 128:
        errors.append('Пароль должен быть от 8 до 128 символов')
    elif not re.search(r'[A-ZА-Я]', password):
        errors.append('Пароль должен содержать хотя бы одну заглавную букву')
    elif not re.search(r'[a-zа-я]', password):
        errors.append('Пароль должен содержать хотя бы одну строчную букву')
    elif not re.search(r'\d', password):
        errors.append('Пароль должен содержать хотя бы одну цифру')
    elif ' ' in password:
        errors.append('Пароль не должен содержать пробелы')
    elif not re.match(r'^[A-Za-zА-Яа-я0-9~!?@#$%^&*_\-+()\[\]{}><\/\\|\"\'\.,:]+$', password):
        errors.append('Пароль содержит недопустимые символы')
    return errors

@bp.route('/', endpoint='index')
def index():
    return render_template('users/index.html', users=user_repository.get_all())

@bp.route('/<int:user_id>')
def show(user_id):
    user = user_repository.get_by_id(user_id)
    if user is None:
        flash('Пользователя нет в базе данных', 'danger')
        return redirect(url_for('users.index'))
    user_role = role_repository.get_by_id(user.role_id)
    return render_template('users/show.html', user_data=user, user_role=user_role.name)


@bp.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    user_data = {}
    errors = {}

    if request.method == 'POST':
        fields = ('username', 'password', 'first_name', 'middle_name', 'last_name', 'role_id')
        user_data = { field: request.form.get(field) or '' for field in fields }

        login_errors = validate_login(user_data['username'])
        if login_errors:
            errors['username'] = login_errors[0]

        password_errors = validate_password(user_data['password'])
        if password_errors:
            errors['password'] = password_errors[0]

        for field in ('first_name', 'last_name'):
            if not user_data[field]:
                errors[field] = 'Поле не может быть пустым'

        if not errors:
            try:
                user_repository.create(**user_data)
                flash('Учетная запись успешно создана', 'success')
                return redirect(url_for('users.index'))
            except connector.errors.DatabaseError:
                flash('Ошибка при создании записи. Проверьте введённые данные.', 'danger')
                db.connect().rollback()
        else:
            flash('Ошибка при создании записи. Проверьте введённые данные.', 'danger')

    return render_template('users/new.html', user_data=user_data, roles=role_repository.get_all(), errors=errors)


@bp.route('/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(user_id):
    user = user_repository.get_by_id(user_id)

    if user is None:
        flash('Пользователя нет в базе данных!', 'danger')
        return redirect(url_for('users.index'))

    errors = {}

    if request.method == 'POST':
        fields = ('first_name', 'middle_name', 'last_name', 'role_id')
        user_data = {field: request.form.get(field) or '' for field in fields}
        user_data['user_id'] = user_id

        if not user_data['first_name']:
            errors['first_name'] = 'Поле не может быть пустым'
        if not user_data['last_name']:
            errors['last_name'] = 'Поле не может быть пустым'

        if not errors:
            try:
                user_repository.update(**user_data)
                flash('Учетная запись успешно изменена', 'success')
                return redirect(url_for('users.index'))
            except connector.errors.DatabaseError:
                flash('Произошла ошибка при изменении записи', 'danger')
                db.connect().rollback()
        else:
            user = user_data  # Чтобы сохранить введённые данные при ошибке

    return render_template('users/edit.html', user_data=user, roles=role_repository.get_all(), errors=errors)


@bp.route('/<int:user_id>/delete', methods=['POST'])
@login_required
def delete(user_id):
    try:
        user_repository.delete(user_id)
        flash('Учетная запись успешно удалена', 'success')
    except connector.errors.DatabaseError:
        db.connect().rollback()
        flash('Произошла ошибка при удалении учетной записи', 'danger')
    return redirect(url_for('users.index'))

@bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        user = user_repository.get_by_id(current_user.id)

        errors = {}

        if not user_repository.check_password(user.id, old_password):
            errors['old_password'] = 'Неверный текущий пароль'
            flash('Ошибка при изменении пароля. Проверьте введённые данные.', 'danger')
            return render_template('users/change_password.html', errors=errors)

        login_errors = validate_login(new_password)
        if login_errors:
            errors['username'] = login_errors[0]

        if errors:
            flash('Ошибка при изменении пароля. Проверьте введённые данные.', 'danger')
            return render_template('users/change_password.html', errors=errors)

        if new_password != confirm_password:
            errors['confirm_password'] = 'Пароли не совпадают'
            flash('Ошибка при изменении пароля. Проверьте введённые данные.', 'danger')
            return render_template('users/change_password.html', errors=errors)

        user_repository.update_password(user.id, new_password)
        flash('Пароль успешно изменен', 'success')
        return redirect(url_for('users.index'))

    return render_template('users/change_password.html', errors={})

