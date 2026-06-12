"""
测试用例自动生成工具
"""
from flask import Flask
from flask_cors import CORS
from app.modules.web.routes import web_bp


def create_app():
    app = Flask(__name__, static_folder='../static', template_folder='../templates')
    CORS(app)

    app.register_blueprint(web_bp, url_prefix='/')

    return app
