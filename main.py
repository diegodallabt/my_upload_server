from flask import Flask, render_template, send_from_directory, redirect, url_for, request
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from werkzeug.utils import secure_filename
import os
from wtforms.validators import InputRequired

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = 'static/files'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

users = {'user': {'password': 'password'}}
users['guess'] = {'password': 'guess'}

class User(UserMixin):
    pass

@login_manager.user_loader
def user_loader(email):
    if email not in users:
        return

    user = User()
    user.id = email
    return user

@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    username = request.form['username']
    if request.form['password'] == users[username]['password']:
        user = User()
        user.id = username
        login_user(user)
        return redirect(url_for('upload_file'))

    return 'Failed to login, please check your email and password and try again.'

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/files')
@login_required
def files():
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    if current_user.id != 'user':
        return "Você não tem permissão para acessar esta página."
    else:
        return render_template('files.html', files=files)

class UploadFileForm(FlaskForm):
    file = FileField("File", validators=[InputRequired()])
    submit = SubmitField("Upload file")    

@app.route('/upload_file', methods=['GET', 'POST'])
@login_required
def upload_file():
    form = UploadFileForm()
    if form.validate_on_submit():
        file = form.file.data
        file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)),app.config['UPLOAD_FOLDER'],secure_filename(file.filename)))
        if current_user.id != 'user':
            return redirect(url_for('upload_file'))
        else:
            return redirect(url_for('files'))
    
    return render_template('index.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)