#!/usr/bin/env python

import logging
import os
import urllib

import flask


def get_files(d, rel=True):
    d = os.path.expanduser(d)
    dirs = []
    fns = []
    for fn in sorted(os.listdir(d)):
        ffn = os.path.join(d, fn)
        if not rel:
            fn = ffn
        if os.path.isdir(ffn):
            dirs.append(fn)
        else:
            fns.append(fn)
    return fns, dirs


def make_blueprint(app=None, register=True):
    main_dir = os.path.dirname(os.path.abspath(__file__))
    template_folder = os.path.join(main_dir, 'templates')
    static_folder = os.path.join(main_dir, 'static')
    logging.debug('filetree main_dir: %s' % main_dir)
    logging.debug('filetree template_folder: %s' % template_folder)
    logging.debug('filetree static_folder: %s' % static_folder)
    filetree = flask.Blueprint('filetree', 'filetree', \
            template_folder=template_folder, static_folder=static_folder)

    @filetree.route('/json')
    def dirlist():
        try:
            d = urllib.unquote(flask.request.args.get('dir', './'))
            fns, dirs = get_files(d, rel=False)
            error = ""
        except Exception as E:
            fns = []
            dirs = []
            error = "PY: %s" % E
        return flask.jsonify(fns=fns, dirs=dirs, error=error)

    @filetree.route('/sfiles', methods=['POST'])
    def sfiles():
        r = []
        try:
            d = urllib.unquote(flask.request.form.get('dir', './'))
            fns, dirs = get_files(d, rel=True)
            r = ['<ul class="jqueryFileTree" style="display: none;">']
            for f in dirs:
                ff = os.path.join(d, f)
                r.append('<li class="directory collapsed">' \
                        '<a href="#" rel="%s/">%s</a></li>' % (ff, f))
            for f in fns:
                ff = os.path.join(d, f)
                e = os.path.splitext(f)[1][1:]  # get .ext and remove dot
                r.append('<li class="file ext_%s">' \
                '<a href="#" rel="%s">%s</a></li>' % (e, ff, f))
            r.append('</ul>')
        except Exception as E:
            r.append('Could not load directory: %s' % (str(E)))
        return ''.join(r)

    @filetree.route('/test')
    def test():
        return flask.render_template('index.html')

    # dirty fix for flask static bug
    @filetree.route('/files/<path:path>')
    def files(path):
        return filetree.send_static_file(path)

    if register:
        if app is None:
            app = flask.Flask('filetree')
        app.register_blueprint(filetree, url_prefix='/filetree')
        return filetree, app
    return filetree


def old():
    app = flask.Flask('fileTree')

    @app.route('/sfiles', methods=['POST'])
    def dirlist():
        r = ['<ul class="jqueryFileTree" style="display: none;">']
        try:
            r = ['<ul class="jqueryFileTree" style="display: none;">']
            d = urllib.unquote(flask.request.form.get('dir', './'))
            d = os.path.expanduser(d)
            for f in sorted(os.listdir(d)):
                ff = os.path.join(d, f)
                if os.path.isdir(ff):
                    r.append('<li class="directory collapsed">'
                            '<a href="#" rel="%s/">%s</a></li>' % (ff, f))
                else:
                    e = os.path.splitext(f)[1][1:]  # get .ext and remove dot
                    r.append('<li class="file ext_%s">'
                    '<a href="#" rel="%s">%s</a></li>' % (e, ff, f))
            r.append('</ul>')
        except Exception, e:
            r.append('Could not load directory: %s' % str(e))
        r.append('</ul>')
        return ''.join(r)

    @app.route('/')
    def default():
        return flask.render_template('index.html')

    app.run(debug=True)


def test(**kwargs):
    ft, app = make_blueprint(register=True)
    logging.debug(app.url_map)
    app.run(**kwargs)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    test()
