import os
from flask import Flask

def create_app():
    """Create and configure an instance of the Flask application."""

    # It's better to provide absolute paths for templates and static files
    # to avoid issues with the current working directory.
    app_dir = os.path.abspath(os.path.dirname(__file__))
    static_folder = os.path.join(app_dir, 'static')
    template_folder = os.path.join(app_dir, 'templates')

    app = Flask(__name__,
                template_folder=template_folder,
                static_folder=static_folder)

    app.config['SECRET_KEY'] = 'holehe-web-interface-secret-key'

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Register blueprint
    from . import routes
    app.register_blueprint(routes.main)

    return app
