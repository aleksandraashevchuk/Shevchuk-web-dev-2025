import random
import re
from functools import lru_cache
from flask import Flask, render_template, abort, make_response, request

app = Flask(__name__)
application = app


def validate_phone(phone):
    # удаляются все пробелы, дефисы, точки, скобки и плюсы
    cleaned_phone = re.sub(r"[ \-().+]", "", phone)

    if not cleaned_phone.isdigit():
        return "Недопустимый ввод. В номере телефона встречаются недопустимые символы."

    if cleaned_phone.startswith("8") or cleaned_phone.startswith("7"):
        if len(cleaned_phone) != 11:
            return "Недопустимый ввод. Неверное количество цифр."
    else:
        if len(cleaned_phone) != 10:
            return "Недопустимый ввод. Неверное количество цифр."

    return None


def format_phone(phone):

    digits = re.sub(r"\D", "", phone) # удаляются все нецифровые символы

    if len(digits) == 10:
        digits = "8" + digits

    return f"8-{digits[1:4]}-{digits[4:7]}-{digits[7:9]}-{digits[9:11]}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/args')
def args():
    return render_template('args.html')

@app.route('/headers')
def headers():
    return render_template('headers.html')

@app.route('/cookies')
def cookies():
    # make_response позволяет сначала подготовить ответ, а затем модифицировать его, например, здесь установка куки
    resp = make_response(render_template('cookies.html'))
    if 'name' not in request.cookies:
        resp.set_cookie('name', 'Vyacheslav')
    else:
        resp.set_cookie('name', expires=0)
    return resp

@app.route('/form', methods=['GET', 'POST'])
def form():
    return render_template('form.html')

@app.route("/form-phone", methods=['GET', 'POST'])
def form_phone():
    # request — это глобальный объект запроса, работает толко в контексте запроса
    phone = ""
    error = None
    formatted_phone = ""

    if request.method == "POST":
        phone = request.form.get("phone", "").strip()
        error = validate_phone(phone)
        if not error:
            formatted_phone = format_phone(phone)

    return render_template("form_phone.html", phone=phone, error=error, formatted_phone=formatted_phone)

