from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FieldList
from wtforms.validators import URL, InputRequired, Regexp


class QueryForm(FlaskForm):
    url = StringField(label='URL', validators=[InputRequired(), URL()])
    submit = SubmitField(label='Start Download!')


class AudioEditForm(FlaskForm):
    artist = FieldList(StringField(label='Artist', validators=[InputRequired()]), min_entries=1)
    title = StringField(label='Title', validators=[InputRequired()])
    album = StringField(label='Album')
    genre = StringField(label='Genre')
    language = StringField(label='Language', validators=[Regexp(r'^$|^[a-z]{2}_[A-Z]{2}$')])
    submit = SubmitField(label='Start Download!')
