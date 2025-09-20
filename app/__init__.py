from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'dev-no-security-needed'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///crowdfund.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    from models import User, Project, RewardTier, Pledge  

    from controllers.auth import auth_bp
    from controllers.projects import proj_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(proj_bp)

    @app.cli.command("init-db")
    def init_db():
        with app.app_context():
            db.drop_all()
            db.create_all()
            print("Database initialized.")

    @app.route("/health")
    def health():
        return {"status": "ok", "time": datetime.utcnow().isoformat()}

    return app

if __name__ == "__main__":
    app = create_app()

    with app.app_context():
        from models import User, Project, RewardTier, Pledge  
        if not os.path.exists("crowdfund.db"):
            db.create_all()
    app.run(debug=True)
