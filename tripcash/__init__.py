import os

from flask import Flask
from flask.templating import render_template


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'tripcash.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

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

    @app.template_filter()
    def currencyFormat(value):
        value = float(value)
        return '${:,.2f}'.format(value)

    return app
