import os
from flask import Flask
from dotenv import load_dotenv
from auth import auth_bp  # Import authentication Blueprint
from routes import routes_bp  # Import API routes Blueprint

app = Flask(__name__)

# Register Blueprints
app.register_blueprint(auth_bp)  
app.register_blueprint(routes_bp)  



env_path = os.path.abspath("proj.env")
load_dotenv(env_path)


app.secret_key = os.getenv("FLASK_SECRET_KEY", "your_secret_key")
app.config["SESSION_COOKIE_NAME"] = "Spotify Login Session"




if __name__ == "__main__":
    app.run(port=8888, debug=True)  # Enable debug mode for development
