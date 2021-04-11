from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FieldList
from wtforms.validators import URL, InputRequired


class QueryForm(FlaskForm):
    url = StringField(label='URL', validators=[URL()])
    submit = SubmitField(label='Start Download!')


class AudioEditForm(FlaskForm):
    artist = FieldList(StringField(validators=[InputRequired()]), label='Artists', min_entries=1)
    title = StringField(label='Title', validators=[InputRequired()])
    album = StringField(label='Album')
    genre = StringField(label='Genre')
    submit = SubmitField(label='Start Download!')
