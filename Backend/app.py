import os
from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from models import init_db

# Import all 5 blueprints
from blueprints.auth_routes import auth_bp
from blueprints.student_routes import student_bp
from blueprints.academician_routes import academician_bp
from blueprints.industry_routes import industry_bp
from blueprints.institute_routes import institute_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app, supports_credentials=True, origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173"
    ])
    
    # Initialize the SQLite tables
    init_db()

    # Register all 5 stakeholder blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(academician_bp)
    app.register_blueprint(industry_bp)
    app.register_blueprint(institute_bp)

    # Friendly Home Route (No more 404 on the root URL!)
    @app.route('/', methods=['GET'])
    def home():
        return jsonify({
            'name': 'Skill Alignment Portal API',
            'status': 'online',
            'endpoints': {
                'health': '/api/health',
                'auth': '/api/auth',
                'student': '/api/student',
                'industry': '/api/industry',
                'academician': '/api/academician',
                'institute': '/api/institute'
            }
        }), 200

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