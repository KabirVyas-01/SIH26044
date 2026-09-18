import os
from flask import Flask, jsonify
from config import Config
from models import init_db
from blueprints.auth_routes import auth_bp
from blueprints.student_routes import student_bp
from blueprints.academician_routes import academician_bp
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    init_db()
    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(academician_bp)
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'healthy',
            'message': 'Skill Alignment Portal Backend is live!', 
            'database_path': app.config['DATABASE_PATH'],
            'author': 'Adi'
        }), 200
    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5001))
    print(f"Server starting on http://127.0.0.1:{port}")
    app.run(host='127.0.0.1', port=port, debug=True)