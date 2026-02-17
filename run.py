from flask import Flask
from app.config import Config
from app.db import db
from app.routes import product_bp, order_bp, report_bp
from app.middleware import request_logger
from app.middleware.rate_limit import rate_limit
from app.utils import error_response


def create_app():

    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    with app.app_context():
        db.create_all()

    request_logger(app)
    rate_limit(app)

    app.register_blueprint(product_bp)
    app.register_blueprint(order_bp)
    app.register_blueprint(report_bp)

    @app.errorhandler(Exception)
    def handle(e):
        return error_response(str(e), "SERVER_ERROR", 500)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
