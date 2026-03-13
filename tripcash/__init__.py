import os

from flask import Flask, session, request
from flask.templating import render_template
from flask_babel import Babel, _


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev'),
        BABEL_DEFAULT_LOCALE='en',
        BABEL_SUPPORTED_LOCALES=['en', 'pt'],
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Locale selector: session preference takes priority over the browser header.
    # Supported locales: 'en' (English) and 'pt' (Portuguese).
    def get_locale():
        if 'language' in session:
            return session['language']
        return request.accept_languages.best_match(['en', 'pt'], default='en')

    babel = Babel(app, locale_selector=get_locale)

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import expense
    app.register_blueprint(expense.bp)

    from . import trip
    app.register_blueprint(trip.bp)

    from . import label
    app.register_blueprint(label.bp)

    from . import list
    app.register_blueprint(list.bp)

    from . import home
    app.register_blueprint(home.bp)
    app.add_url_rule('/', endpoint='index')

    # Saves the chosen language in the session so it persists across requests.
    @app.route('/set_language/<lang>')
    def set_language(lang):
        from flask import redirect
        if lang in app.config['BABEL_SUPPORTED_LOCALES']:
            session['language'] = lang
        return redirect(request.referrer or '/')

    @app.template_filter()
    def currencyFormat(value):
        value = float(value)
        return '${:,.2f}'.format(value)

    return app
