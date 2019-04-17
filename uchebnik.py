from flask import Flask, url_for, request, render_template, redirect
from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField
from wtforms.validators import DataRequired
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

class LoginForm(FlaskForm):
    select = SelectField('Выберите промежуток времени', coerce=int, choices=[(0, 'Завтра'), (1, '3 дня'),
                                                                             (2, 'Неделя'), (3, 'Месяц')])
    submit = SubmitField('Создать прогноз')
    
@app.route('/weather', methods=['GET', 'POST'])
def w():
    form = LoginForm()
    if form.validate_on_submit():
        with open("we.json", "rt", encoding="utf8") as f:
            log = json.loads(f.read())
        if form.select.data == 0:
            return render_template('Tomorrow.html', title='Завтра', log=log['1'])
        if form.select.data == 1:
            return render_template('Chutb.html', title='Завтра', log=list(log.items())[:3])
        if form.select.data == 2:
            return render_template('Chutb.html', title='Завтра', log=list(log.items())[:7])
        if form.select.data == 3:
            return render_template('month.html', title='Завтра', log=log)
    return render_template('weather.html', title='Погода', form=form)



if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')


