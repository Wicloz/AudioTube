from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import URL, InputRequired


class QueryForm(FlaskForm):
    url = StringField(label='URL', validators=[URL()])
    submit = SubmitField(label='Start Download!')


class AudioEditForm(FlaskForm):
    artist = StringField(label='Artist', validators=[InputRequired()])
    title = StringField(label='Title', validators=[InputRequired()])
    album = StringField(label='Album')
    submit = SubmitField(label='Start Download!')
