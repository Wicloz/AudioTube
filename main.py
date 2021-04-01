from flask import Flask, render_template, redirect, url_for, send_file
from forms import QueryForm, AudioEditForm
from base64 import b32encode, b32decode
from youtube_dl import YoutubeDL
from tempfile import TemporaryDirectory
from os.path import join
from mutagen.easyid3 import EasyID3
from io import BytesIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'n1MF4absCxYuRyknQeNutaK9kcBW4o38'


def try_get_multiple(mapping, *keys):
    for key in keys:
        if key in mapping and mapping[key]:
            return mapping[key]


@app.route('/', methods=['get', 'post'])
def landing():
    form = QueryForm()

    if form.validate_on_submit():
        return redirect(url_for('editor', url=b32encode(form.url.data.encode('UTF8'))))

    return render_template('landing.html', title='IntelliFlow', form=form)


@app.route('/download/<url>', methods=['get', 'post'])
def editor(url):
    url = b32decode(url).decode('UTF8')
    form = AudioEditForm()

    if form.validate_on_submit():
        compound = f'{form.artist.data} - {form.title.data}'
        with TemporaryDirectory() as temp:
            pass

            with YoutubeDL({
                'outtmpl': join(temp, compound + '.%(ext)s'),
                'format': 'bestaudio/best',
                'writethumbnail': True,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '320',
                }, {
                    'key': 'EmbedThumbnail',
                }, {
                    'key': 'FFmpegMetadata',
                }],
            }) as ydl:
                ydl.download([url])

            mp3 = EasyID3(join(temp, compound + '.mp3'))
            mp3['artist'] = form.artist.data
            mp3['title'] = form.title.data
            mp3['album'] = form.album.data
            mp3.save()

            with open(join(temp, compound + '.mp3'), 'rb') as fp:
                memory = BytesIO(fp.read())

        return send_file(
            filename_or_fp=memory,
            as_attachment=True,
            mimetype='audio/mpeg',
            attachment_filename=compound + '.mp3',
        )

    with YoutubeDL({'skip_download': True}) as ydl:
        meta = ydl.extract_info(url)
        if not form.artist.data:
            form.artist.data = try_get_multiple(meta, 'artist', 'creator', 'uploader', 'uploader_id')
        if not form.title.data:
            form.title.data = try_get_multiple(meta, 'track', 'title')
        if not form.album.data:
            form.album.data = try_get_multiple(meta, 'album')

    return render_template('editor.html', title='IntelliFlow', form=form, thumbnail=meta['thumbnail'])


if __name__ == '__main__':
    app.run(debug=True)
