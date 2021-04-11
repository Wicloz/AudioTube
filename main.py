#!/usr/bin/env python3

from flask import Flask, render_template, redirect, url_for, send_file
from forms import QueryForm, AudioEditForm
from base64 import b32encode, b32decode
from youtube_dl import YoutubeDL
from tempfile import TemporaryDirectory
from os.path import join
from mutagen.easyid3 import EasyID3
from io import BytesIO
from socket import gethostname
from slugify import slugify

app = Flask(__name__)
app.config['SECRET_KEY'] = 'n1MF4absCxYuRyknQeNutaK9kcBW4o38'
EasyID3.RegisterTXXXKey('artists', 'ARTISTS')


def try_get_multiple(mapping, *keys):
    for key in keys:
        if key in mapping and mapping[key]:
            return mapping[key]


@app.route('/', methods=['get', 'post'])
def landing():
    form = QueryForm()

    if form.validate_on_submit():
        return redirect(url_for('editor', url=b32encode(form.url.data.encode('UTF8'))))

    return render_template('landing.html', form=form)


@app.route('/download/<url>', methods=['get', 'post'])
def editor(url):
    url = b32decode(url).decode('UTF8')
    form = AudioEditForm()

    if form.validate_on_submit():
        with TemporaryDirectory() as temp:
            pass

            artists_list = [' '.join(reversed(artist.split(', '))) for artist in form.artist.data]
            artists_fancy = ' & '.join(artists_list)
            artists_slugs = [slugify(artist) for artist in form.artist.data]

            with YoutubeDL({
                'outtmpl': join(temp, 'download.%(ext)s'),
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

            mp3 = EasyID3(join(temp, 'download.mp3'))
            mp3['artists'] = artists_list
            mp3['artist'] = artists_fancy
            mp3['artistsort'] = artists_slugs
            mp3['title'] = form.title.data
            mp3['album'] = form.album.data
            mp3['genre'] = form.genre.data
            mp3.save()

            with open(join(temp, 'download.mp3'), 'rb') as fp:
                memory = BytesIO(fp.read())

        return send_file(
            filename_or_fp=memory,
            as_attachment=True,
            mimetype='audio/mpeg',
            attachment_filename=artists_fancy + ' - ' + form.title.data + '.mp3',
        )

    with YoutubeDL({'skip_download': True}) as ydl:
        meta = ydl.extract_info(url)

    if not form.is_submitted():
        form.artist.entries[0].data = try_get_multiple(meta, 'artist', 'creator', 'uploader', 'uploader_id')
        form.title.data = try_get_multiple(meta, 'track', 'title')
        form.album.data = try_get_multiple(meta, 'album')
        form.genre.data = try_get_multiple(meta, 'genre')

    return render_template('editor.html', form=form, thumbnail=meta['thumbnail'], channel=meta['uploader'])


if __name__ == '__main__':
    if gethostname() == 'scramjet':
        app.run()
    else:
        app.run(debug=True, port=80, host='0.0.0.0')
