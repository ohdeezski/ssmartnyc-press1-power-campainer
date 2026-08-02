import os

from app import create_app, socketio

app = create_app()

if __name__ == "__main__":
    host = os.environ.get("FLASK_HOST", "0.0.0.0")
    port = int(os.environ.get("FLASK_PORT", 8080))
    debug = os.environ.get("FLASK_ENV", "development") == "development"
    print("\n--- Street Smart NYC Campaign Operations Center ---")
    print(f"Access the UI at: http://{host}:{port}/")
    print(f"Environment: {os.environ.get('FLASK_ENV', 'development')}")
    print(f"Database: {app.config.get('SQLALCHEMY_DATABASE_URI')}")
    print("----------------------------------------------------\n")
    socketio.run(app, host=host, port=port, debug=debug, allow_unsafe_werkzeug=True)
