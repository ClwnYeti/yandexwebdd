from flask import Flask, render_template, redirect, session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, PasswordField, BooleanField, SelectField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['Encoding'] = 'UTF-8'
db = SQLAlchemy(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


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
	
	def __repr__(self):
		return '<YandexLyceumStudent {} {} {} {}>'.format(
			self.id, self.username, self.name, self.surname)


class YandexLyceumTeacher(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(80), unique=True, nullable=False)
	password = db.Column(db.String(80), unique=True, nullable=False)
	name = db.Column(db.String(80), unique=False, nullable=False)
	surname = db.Column(db.String(80), unique=False, nullable=False)
	email = db.Column(db.String(120), unique=True, nullable=False)
	
	def __repr__(self):
		return '<YandexLyceumTeacher {} {} {} {}>'.format(
			self.id, self.username, self.name, self.surname)


class Admin(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(80), unique=True, nullable=False)
	password = db.Column(db.String(80), unique=True, nullable=False)
	
	def __repr__(self):
		return '<Admin {} {}>'.format(
			self.id, self.username)


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
if Admin.query.all() == []:
	admin = Admin(username='admin', password='admin')
	db.session.add(admin)
if YandexLyceumTeacher.query.all() == []:
	admint = YandexLyceumTeacher(username='admin', password='admin',
	                             name='admin', surname='admin', email='admin')
	db.session.add(admint)
db.session.commit()


class LoginForm(FlaskForm):
	username = StringField('Логин', validators=[DataRequired()])
	password = PasswordField('Пароль', validators=[DataRequired()])
	remember_me = BooleanField('Запомнить меня')
	submit = SubmitField('Войти')


class RegisterFormSt(FlaskForm):
	username = StringField('Логин', validators=[DataRequired()])
	email = StringField('Email', validators=[DataRequired()])
	name = StringField('Имя', validators=[DataRequired()])
	surname = StringField('Фамилия', validators=[DataRequired()])
	a = YandexLyceumTeacher.query.all()
	a = [(i.id, i.name + ' ' + i.surname) for i in a]
	teacher = SelectField('Учитель', coerce=int, choices=a)
	year = SelectField('Год', coerce=int, choices=[(1, 'Первый'), (2, 'Второй')])
	password = PasswordField('Пароль', validators=[DataRequired()])
	
	submit = SubmitField('Зарегистрироваться')


class AddForm(FlaskForm):
	title = StringField('Задание', validators=[DataRequired()])
	content = TextAreaField('Код', validators=[DataRequired()])
	submit = SubmitField('Добавить')


@app.route('/')
@app.route('/main', methods=['GET', 'POST'])
def main():
	if 'class' in session:
		return redirect('/' + session['class'] + '/' + str(session['user_id']))
	return render_template('main.html', title='Main')


@app.route('/login/<classer>', methods=['GET', 'POST'])
def login(classer):
	if classer == 'student':
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
	elif classer == 'admin':
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


@app.route('/register/student', methods=['GET', 'POST'])
def reg():
	form = RegisterFormSt()
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
		student = YandexLyceumStudent.query.filter_by(username=username).all()
		print(student)
		db.session.commit()
		student = student[0]
		session['username'] = username
		session['class'] = 'YandexLyceumStudent'
		session['user_id'] = student.id
		return redirect("/" + session['class'] + "/" + str(session['user_id']))
	return render_template('reg.html', title='Авторизация', form=form)


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
	session.pop('class', 0)
	session.pop('user_id', 0)
	return redirect('/')


@app.route('/YandexLyceumStudent/<int:s>', methods=['GET', 'POST'])
def index(s):
	if 'username' not in session:
		return redirect('/')
	if (session['user_id'] != s or session['class'] == 'YandexLyceumTeacher') and not (session['class'] == 'Admin'):
		return redirect('/' + session['class'] + '/' + str(session['user_id']))
	attempts = SolutionAttempt.query.filter_by(student_id=session['user_id']).all()
	return render_template('index.html', username=session['username'],
	                       all=attempts, id=int(session['user_id']))


@app.route('/YandexLyceumStudent/<int:s>/add', methods=['GET', 'POST'])
def request(s):
	if 'username' not in session:
		return redirect('/login')
	if session['user_id'] != s or session['class'] != 'YandexLyceumStudent':
		return redirect('/' + session['class'] + '/' + str(session['user_id']))
	form = AddForm()
	if form.validate_on_submit():
		title = form.title.data
		code = form.content.data
		user = YandexLyceumStudent.query.filter_by(id=s).first()
		attempt = SolutionAttempt(task=title,
		                          code=code,
		                          status='OK')
		user.SolutionAttempts.append(attempt)
		db.session.commit()
		content = form.content.data
		return redirect('/' + session['class'] + '/' + str(session['user_id']))
	return render_template('add.html', title='Добавление новости',
	                       form=form, username=session['username'])

@app.route("/YandexLyceumStudent/<int:s>/tasks/<int:k>", methods=['GET', 'POST', 'PUT', "DELETE"])
def task(s, k):



if __name__ == '__main__':
	app.run(port=8080, host='127.0.0.1')
