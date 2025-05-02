from flask import Flask, request, render_template_string, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://flaskuser:flaskpass@db:5432/flaskdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = '/app/static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    company = db.Column(db.String(100))
    position = db.Column(db.String(100))
    photo = db.Column(db.String(200))  # path to uploaded photo

base_template = """
<!DOCTYPE html>
<html lang="az">
<head>
    <meta charset="UTF-8">
    <title>{{ title }}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
<div class="container mt-5">
    <nav class="navbar navbar-expand-lg navbar-light bg-white shadow-sm mb-4">
        <div class="container-fluid">
            <a class="navbar-brand" href="/">Flask Tətbiqi</a>
            <div class="collapse navbar-collapse">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item"><a class="nav-link" href="/">Ana səhifə</a></li>
                    <li class="nav-item"><a class="nav-link" href="/form">İstifadəçi əlavə et</a></li>
                    <li class="nav-item"><a class="nav-link" href="/users">İstifadəçilər</a></li>
                </ul>
            </div>
        </div>
    </nav>
    {{ content|safe }}
</div>
</body>
</html>
"""

@app.route('/')
def index():
    html = """
    <div class="text-center">
        <h1>Salam, bu Flask tətbiqidir!</h1>
        <p class="lead">Yeni istifadəçi əlavə edin və siyahıya baxın.</p>
        <a href="/form" class="btn btn-primary">İstifadəçi əlavə et</a>
    </div>
    """
    return render_template_string(base_template, title="Ana səhifə", content=html)

@app.route('/form')
def user_form():
    html = """
    <h2 class="mb-4">Yeni İstifadəçi Əlavə Et</h2>
    <form method="POST" action="/add_user" enctype="multipart/form-data">
        <div class="row g-3">
            <div class="col-md-6">
                <label class="form-label">Ad</label>
                <input name="first_name" class="form-control" required>
            </div>
            <div class="col-md-6">
                <label class="form-label">Soyad</label>
                <input name="last_name" class="form-control" required>
            </div>
            <div class="col-md-6">
                <label class="form-label">Telefon</label>
                <input name="phone" class="form-control">
            </div>
            <div class="col-md-6">
                <label class="form-label">Şirkət</label>
                <input name="company" class="form-control">
            </div>
            <div class="col-md-12">
                <label class="form-label">Vəzifə</label>
                <input name="position" class="form-control">
            </div>
            <div class="col-md-12">
                <label class="form-label">Şəkil</label>
                <input name="photo" type="file" accept="image/*" class="form-control">
            </div>
            <div class="col-12">
                <button type="submit" class="btn btn-success">Əlavə et</button>
            </div>
        </div>
    </form>
    """
    return render_template_string(base_template, title="İstifadəçi Əlavə Et", content=html)

@app.route('/add_user', methods=['POST'])
def add_user():
    data = request.form
    photo = request.files.get('photo')
    photo_path = ''
    if photo and photo.filename:
        filename = secure_filename(photo.filename)
        photo_path = f"uploads/{filename}"
        photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    user = User(
        first_name=data.get('first_name'),
        last_name=data.get('last_name'),
        phone=data.get('phone'),
        company=data.get('company'),
        position=data.get('position'),
        photo=photo_path
    )
    db.session.add(user)
    db.session.commit()
    return redirect(url_for('list_users'))

@app.route('/users')
def list_users():
    users = User.query.all()
    if not users:
        html = """<div class='alert alert-info'>Heç bir istifadəçi yoxdur.</div>"""
    else:
        rows = "".join([
            f"""
            <tr>
                <td>{u.id}</td>
                <td><img src='/static/{u.photo}' width='50'></td>
                <td>{u.first_name}</td><td>{u.last_name}</td><td>{u.phone}</td>
                <td>{u.company}</td><td>{u.position}</td>
                <td>
                    <a href='/edit/{u.id}' class='btn btn-sm btn-outline-warning'>Redaktə et</a>
                    <a href='/delete/{u.id}' class='btn btn-sm btn-outline-danger'>Sil</a>
                </td>
            </tr>
            """ for u in users
        ])
        html = f"""
        <h3 class="mb-4">İstifadəçilər Siyahısı</h3>
        <table class="table table-bordered table-striped">
            <thead class="table-light">
                <tr><th>ID</th><th>Şəkil</th><th>Ad</th><th>Soyad</th><th>Telefon</th><th>Şirkət</th><th>Vəzifə</th><th>Əməliyyat</th></tr>
            </thead>
            <tbody>{rows}</tbody>
        </table>
        """
    return render_template_string(base_template, title="İstifadəçilər", content=html)

@app.route('/delete/<int:user_id>')
def delete_user(user_id):
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
    return redirect(url_for('list_users'))

@app.route('/edit/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return redirect(url_for('list_users'))

    if request.method == 'POST':
        user.first_name = request.form.get('first_name')
        user.last_name = request.form.get('last_name')
        user.phone = request.form.get('phone')
        user.company = request.form.get('company')
        user.position = request.form.get('position')
        db.session.commit()
        return redirect(url_for('list_users'))

    html = f"""
    <h2 class="mb-4">İstifadəçini Redaktə Et</h2>
    <form method="POST">
        <div class="row g-3">
            <div class="col-md-6">
                <label class="form-label">Ad</label>
                <input name="first_name" value="{user.first_name}" class="form-control" required>
            </div>
            <div class="col-md-6">
                <label class="form-label">Soyad</label>
                <input name="last_name" value="{user.last_name}" class="form-control" required>
            </div>
            <div class="col-md-6">
                <label class="form-label">Telefon</label>
                <input name="phone" value="{user.phone}" class="form-control">
            </div>
            <div class="col-md-6">
                <label class="form-label">Şirkət</label>
                <input name="company" value="{user.company}" class="form-control">
            </div>
            <div class="col-md-12">
                <label class="form-label">Vəzifə</label>
                <input name="position" value="{user.position}" class="form-control">
            </div>
            <div class="col-12">
                <button type="submit" class="btn btn-primary">Yadda saxla</button>
            </div>
        </div>
    </form>
    """
    return render_template_string(base_template, title="Redaktə", content=html)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000)

