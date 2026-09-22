import os
from pathlib import Path
from flask import Flask, jsonify, send_from_directory
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
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://localhost:5174",
        "http://192.168.29.194:5173"
    ])

    # Initialize the SQLite tables and ensure default seed data exists
    init_db()
    try:
        from seed_data import seed
        seed()
    except Exception as e:
        print(f"[Seed Warning] Auto-seeding skipped: {e}")

    # Register all 5 stakeholder blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(academician_bp)
    app.register_blueprint(industry_bp)
    app.register_blueprint(institute_bp)

    # Serve React frontend build in production
    frontend_dist = Path(__file__).resolve().parent.parent / "Frontend" / "dist"

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
        if path != "" and frontend_dist.exists() and (frontend_dist / path).exists():
            return send_from_directory(str(frontend_dist), path)
        elif frontend_dist.exists() and (frontend_dist / "index.html").exists():
            return send_from_directory(str(frontend_dist), "index.html")
        else:
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