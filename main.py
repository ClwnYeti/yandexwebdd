from flask import Flask, render_template, redirect, session, request
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, PasswordField, BooleanField, SelectField, FileField
from flask_wtf.file import FileRequired, FileAllowed
from wtforms.validators import DataRequired
from werkzeug.utils import secure_filename
from flask import make_response


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
	im = db.Column(db.String(256), unique=False, nullable=False)
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

class Change(FlaskForm):
	code = TextAreaField('Код', validators=[DataRequired()])
	submit = SubmitField('Подтвердить')
	
class Task(FlaskForm):
	code = SelectField('Решение', coerce=int, choices=[(1, 'Зачтено'), (2, 'На доработку')])
	submit = SubmitField('Подтвердить')
	
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


class AddTForm(FlaskForm):
	title = StringField('Задание', validators=[DataRequired()])
	content = TextAreaField('Код', validators=[DataRequired()])
	submit = SubmitField('Добавить')
	
class AddFForm(FlaskForm):
	title = StringField('Задание', validators=[DataRequired()])
	content = FileField('Файл с задачей', validators=[FileRequired()])
	submit = SubmitField('Добавить')
	
class AddPForm(FlaskForm):
	content = FileField('Картинка', validators=[FileRequired(), FileAllowed(['jpg', 'png'], 'Images only!')])
	submit = SubmitField('Выбрать')

@app.errorhandler(404)
def not_found(error):
	return render_template('404.html')

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
	elif classer == 'teacher':
			form = LoginForm()
			if form.validate_on_submit():
				user_name = form.username.data
				password = form.password.data
				a = YandexLyceumTeacher.query.filter_by(username=user_name, password=password).all()
				if a != []:
					a = a[0]
					session['username'] = user_name
					session['class'] = 'YandexLyceumTeacher'
					session['user_id'] = a.id
				return redirect("/" + session['class'] + "/" + str(session['user_id']))
			return render_template('login.html', title='Авторизация', form=form)


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
									  year=year,
		                              im='')
		teacher.YandexLyceumStudent.append(student)
		student = YandexLyceumStudent.query.filter_by(username=username).all()
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
	if session['class'] != 'Admin' or session['user_id'] != 1:
		return redirect('/' + session['class'] + '/' + str(session['user_id']))
	a = YandexLyceumTeacher.query.all()
	a = [(YandexLyceumStudent.query.filter_by(teacherid=i.id).all(), i) for i in a]
	x = []
	for i in a:
		k = len(i[0])
		p = 0
		n = 0
		for j in i[0]:
			v = SolutionAttempt.query.filter_by(student_id=j.id).all()
			for l in v:
				if l.status == 'Check':
					n += 1
				else:
					p += 1
		x.append([k, p, n, i[1]])
	return render_template('admin.html', username=session['username'],
	                       all=x)


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
	user = YandexLyceumStudent.query.filter_by(id=session['user_id']).first()
	
	return render_template('index.html', user=user,
	                       all=attempts, id=int(session['user_id']))


@app.route('/YandexLyceumStudent/<int:s>/add', methods=['GET', 'POST'])
def ss(s):
	return redirect('/YandexLyceumStudent/' +str(s) + '/add/text')

@app.route('/YandexLyceumStudent/<int:s>/add/text', methods=['GET', 'POST'])
def request(s):
	if 'username' not in session:
		return redirect('/login')
	if session['user_id'] != s or session['class'] != 'YandexLyceumStudent':
		return redirect('/' + session['class'] + '/' + str(session['user_id']))
	form = AddTForm()
	if form.validate_on_submit():
		title = form.title.data
		code = form.content.data
		user = YandexLyceumStudent.query.filter_by(id=s).first()
		attempt = SolutionAttempt(task=title,
		                          code=code,
		                          status='Check')
		user.SolutionAttempts.append(attempt)
		db.session.commit()
		content = form.content.data
		return redirect('/' + session['class'] + '/' + str(session['user_id']))
	return render_template('add.html', title='Добавление новости',
	                       form=form, username=session['username'], inp='file', id=s)



@app.route("/YandexLyceumStudent/<int:s>/tasks/<int:k>/")
def ta(s, k):
	return redirect('/' + session['class'] + '/' + str(s) + '/tasks/' + str(k) + '/text')


@app.route("/YandexLyceumStudent/<int:s>/tasks/<int:k>/text", methods=['GET', 'POST'])
def t(s, k):
	if 'username' not in session:
		return redirect('/login')
	if (session['user_id'] != s or session['class'] != 'YandexLyceumStudent') or session['class'] == 'Admin':
		return redirect('/' + session['class'] + '/' + str(session['user_id']))
	return render_template('task.html', title='Новости', user_id=s, task=SolutionAttempt.query.filter_by(id=k).first())


@app.route("/YandexLyceumStudent/<int:s>/tasks")
def ter(s):
	if 'username' not in session:
		return redirect('/login')
	if session['user_id'] != s or session['class'] != 'YandexLyceumStudent':
		return redirect('/' + session['class'] + '/' + str(session['user_id']))
	return redirect('/YandexLyceumStudent/' + str(s))


@app.route("/YandexLyceumStudent/<int:s>/tasks/<int:k>/change/text", methods=['GET', 'POST'])
def te(s, k):
	if 'username' not in session:
		return redirect('/login')
	if session['user_id'] != s or session['class'] != 'YandexLyceumStudent':
		return redirect('/' + session['class'] + '/' + str(session['user_id']))
	form = Change()
	if form.validate_on_submit():
		code = form.code.data
		a = SolutionAttempt.query.filter_by(id=k).first()
		user = YandexLyceumStudent.query.filter_by(id=s).first()
		attempt = SolutionAttempt(task=a.task,
		                          code=code,
		                          status='Check')
		user.SolutionAttempts.append(attempt)
		db.session.delete(a)
		db.session.commit()
		return redirect('/' + session['class'] + '/' + str(session['user_id']))
	return render_template('textedit.html', form=form)


@app.route("/YandexLyceumStudent/<int:s>/tasks/<int:k>/delete")
def terk(s, k):
	if 'username' not in session:
		return redirect('/login')
	if session['user_id'] != s or session['class'] != 'YandexLyceumStudent':
		return redirect('/' + session['class'] + '/' + str(session['user_id']))
	a = SolutionAttempt.query.filter_by(id=k).first()
	db.session.delete(a)
	db.session.commit()
	return redirect('/' + session['class'] + '/' + str(session['user_id']))


@app.route('/YandexLyceumTeacher/<int:s>', methods=['GET', 'POST'])
def indext(s):
	if 'username' not in session:
		return redirect('/')
	if (session['user_id'] != s or session['class'] == 'YandexLyceumStudent') and not (session['class'] == 'Admin'):
		return redirect('/' + session['class'] + '/' + str(session['user_id']))
	students = YandexLyceumStudent.query.filter_by(teacherid=session['user_id']).all()
	students = [(SolutionAttempt.query.filter_by(student_id=i.id), i) for i in students]
	x = []
	for i in students:
		s = 0
		e = 0
		c = 0
		for j in i[0]:
			if j.status == 'OK':
				s += 1
			elif j.status == 'Check':
				c += 1
			else:
				e += 1
		x.append([c, s, e, i[1]])
	students = x.copy()
	user = YandexLyceumTeacher.query.filter_by(id=session['user_id']).first()
	return render_template('indext.html', user=user,
	                       all=students, id=int(session['user_id']))


@app.route('/YandexLyceumTeacher/<int:s>/students/<int:k>', methods=['GET', 'POST'])
def st(s, k):
	if 'username' not in session:
		return redirect('/')
	if (session['user_id'] != s or session['class'] == 'YandexLyceumStudent') and not (session['class'] == 'Admin'):
		return redirect('/' + session['class'] + '/' + str(session['user_id']))
	attempts = SolutionAttempt.query.filter_by(student_id=k).all()
	user = YandexLyceumStudent.query.filter_by(id=k).first()
	return render_template('st.html', user=user,
	                       all=attempts, id=s)


@app.route('/YandexLyceumTeacher/<int:s>/students/<int:k>/tasks/<int:f>/text', methods=['GET', 'POST'])
def stt(s, k, f):
	if 'username' not in session:
		return redirect('/')
	if (session['user_id'] != s or session['class'] == 'YandexLyceumStudent') and not (session['class'] == 'Admin'):
		return redirect('/' + session['class'] + '/' + str(session['user_id']))
	form = Task()
	if form.validate_on_submit():
		a = SolutionAttempt.query.filter_by(id=f).first()
		db.session.delete(a)
		c = SolutionAttempt()
		b = YandexLyceumStudent.query.filter_by(id=k).first()
		if form.code.data == 1:
			a.status = 'OK'
			c = SolutionAttempt(task=a.task, status=a.status, code=a.code)
			b.SolutionAttempts.append(c)
		else:
			a.status = 'Error'
			c = SolutionAttempt(task=a.task, status=a.status, code=a.code)
			b.SolutionAttempts.append(c)
		db.session.commit()
		return redirect('/YandexLyceumTeacher/' + str(s) + '/students/' + str(k))
	return render_template('taskt.html', title='Новости', user_id=s,
	                       task=SolutionAttempt.query.filter_by(id=f).first(), form=form)


if __name__ == '__main__':
	app.run(port=8080, host='127.0.0.1')
