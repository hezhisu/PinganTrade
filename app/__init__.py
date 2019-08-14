from flask import Flask


from api import app_api as api
def create_app(config_name):
    app = Flask(__name__)
    app.config.SWAGGER_UI_JSONEDITOR = True
    app.register_blueprint(api)
    # attach routes and custom error pages here
    return app