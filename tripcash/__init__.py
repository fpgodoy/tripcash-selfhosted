import os
import logging

from flask import Flask, session, request
from flask_babel import Babel


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    secret_key = os.environ.get('SECRET_KEY')
    if not secret_key:
        logging.warning(
            "SECRET_KEY não configurada no ambiente. Usando chave aleatória — "
            "as sessões serão invalidadas a cada restart do servidor. "
            "Defina SECRET_KEY no seu arquivo .env para produção."
        )
        secret_key = os.urandom(32)

    app.config.from_mapping(
        SECRET_KEY=secret_key,
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

    Babel(app, locale_selector=get_locale)

    # Lê a variável de ambiente que controla o registro de novos usuários.
    # Padrão: True (registro habilitado). Defina ALLOW_REGISTRATION=false no .env para desabilitar.
    allow_registration = os.environ.get('ALLOW_REGISTRATION', 'true').strip().lower() not in ('false', '0', 'no')
    app.config['ALLOW_REGISTRATION'] = allow_registration

    # Injeta allow_registration em todos os templates automaticamente.
    @app.context_processor
    def inject_config():
        return {'allow_registration': app.config['ALLOW_REGISTRATION']}

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

    from . import settlement
    app.register_blueprint(settlement.bp)

    app.add_url_rule('/', endpoint='index')

    # Saves the chosen language in the session so it persists across requests.
    @app.route('/set_language/<lang>')
    def set_language(lang):
        from flask import redirect
        if lang in app.config['BABEL_SUPPORTED_LOCALES']:
            session['language'] = lang
        return redirect(request.referrer or '/')

    @app.template_filter()
    def currency_format(value):
        value = float(value)
        return '${:,.2f}'.format(value)

    return app
