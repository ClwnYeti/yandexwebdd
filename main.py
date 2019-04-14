from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, PasswordField, BooleanField
from flask import Flask, url_for, request, render_template, redirect, session
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class YandexLyceumStudent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(80), unique=False, nullable=False)
    surname = db.Column(db.String(80), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    teacherid = db.Column(db.Integer,
                               db.ForeignKey('yandex_lyceum_teacher.id'),
                               nullable=False)
    teacher = db.relationship('YandexLyceumTeacher',
                              backref=db.backref('YandexLyceumStudent',
                                                 lazy=True))
    year = db.Column(db.Integer, unique=False, nullable=False)
    
    
class YandexLyceumTeacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(80), unique=False, nullable=False)
    surname = db.Column(db.String(80), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)


class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=True, nullable=False)
    
    
class SolutionAttempt(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        task = db.Column(db.String(80), unique=False, nullable=False)
        code = db.Column(db.String(1000), unique=False, nullable=False)
        status = db.Column(db.String(50), unique=False, nullable=False)
        student_id = db.Column(db.Integer,
                               db.ForeignKey('yandex_lyceum_student.id'),
                               nullable=False)
        student = db.relationship('YandexLyceumStudent',
                                  backref=db.backref('SolutionAttempts',
                                                     lazy=True))
    
        def __repr__(self):
            return '<SolutionAttempt {} {} {}>'.format(
                    self.id, self.task, self.status)


db.create_all()
db.session.commit()
admin = Admin(username='admin', password='admin')
db.session.add(admin)
admint = YandexLyceumTeacher(username='admin', password='admin',
                             name='admin', surname='admin', email='admin')
db.session.add(admint)
db.session.commit()


class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegisterForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')


class AddNewsForm(FlaskForm):
    title = StringField('Заголовок новости', validators=[DataRequired()])
    content = TextAreaField('Текст новости', validators=[DataRequired()])
    submit = SubmitField('Добавить')


@app.route('/')
@app.route('/main')
def main():
    if 'username' in session:
        return redirect('/' + session['class'] + '/' + str(session['user_id']))
    return render_template('main.html', title='Авторизация')
    
    
@app.route('/login/student', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user_name = form.username.data
        password = form.password.data
        a = YandexLyceumStudent.query.filter_by(username=user_name, password=password).all()
        if a != []:
            a = a[0]
            session['username'] = user_name
            session['class'] = 'YandexLyceumStudent'
            session['user_id'] = a.id
        return redirect("/" + session['class'] + "/" + str(session['user_id']))
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/register/student', methods=['GET', 'POST'])
def reg():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        name = form.name.data
        surname = form.surname.data
        email = form.email.data
        teacher = YandexLyceumTeacher.query.filter_by(id=1).first()
        year = form.year.data
        user = YandexLyceumStudent.query.filter_by(username=username).all()
        if user != []:
            form.username.errors = list(form.username.errors)
            form.username.errors.append('Логин занят')
        user = YandexLyceumStudent.query.filter_by(email=email).all()
        if user != []:
            form.username.errors = list(form.username.errors)
            form.email.errors.append('Email занят')
            return render_template('reg.html', title='Авторизация', form=form)
        student = YandexLyceumStudent(username=username,
                                      email=email,
                                      name=name,
                                      surname=surname,
                                      password=password,
                                      year=year)
        teacher.YandexLyceumStudent.append(student)
        session['username'] = username
        session['class'] = 'YandexLyceumStudent'
        session['user_id'] = student.id
        return redirect("/" + session['class'] + "/" + str(session['user_id']))
    return render_template('reg.html', title='Авторизация', form=form)


@app.route('/login/admin', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user_name = form.username.data
        password = form.password.data
        a = Admin.query.filter_by(username=user_name, password=password).all()
        if a != []:
            a = a[0]
            session['username'] = user_name
            session['class'] = 'Admin'
            session['user_id'] = a.id
        return redirect("/admin")
    return render_template('loginadmin.html', title='Авторизация', form=form)


@app.route('/admin', methods=['GET', 'POST'])
def adm():
    if 'username' not in session:
        return redirect('/')
    if session['username'] != 'admin' or session['user_id'] != 1:
        return redirect('/' + session['class'] + '/' + str(session['user_id']))
    a = YandexLyceumTeacher.query.all()
    return render_template('admin.html', username=session['username'],
                           users=a)


@app.route('/logout')
def logout():
    session.pop('username', 0)
    session.pop('user_id', 0)
    return redirect('/')



@app.route('/student/<int: s>')
def index(s):
    if 'username' not in session:
        return redirect('/')
    if (session['user_id'] != s or session['class'] == 'YandexLyceumTeacher') and not(session['class'] == 'Admin'):
        return redirect('/' + session['class'] + '/' + str(session['user_id']))
    attempts = SolutionAttempt.query.filter_by(student_id=session['user_id']).all()
    return render_template('index.html', username=session['username'],
                           all=attempts)


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
