from flask import render_template, request
from models import db, User
from flask import Blueprint

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return 'Salam, bu Flask tətbiqidir!'

@main.route('/users')
def list_users():
    users = User.query.all()
    return f"{len(users)} istifadəçi var"

@main.route('/form')
def user_form():
    return render_template('form.html')

@main.route('/add_user', methods=['POST'])
def add_user():
    data = request.form
    user = User(
        first_name=data.get('first_name'),
        last_name=data.get('last_name'),
        phone=data.get('phone'),
        company=data.get('company'),
        position=data.get('position')
    )
    db.session.add(user)
    db.session.commit()
    return f"İstifadəçi əlavə olundu: {user.first_name} {user.last_name}"

