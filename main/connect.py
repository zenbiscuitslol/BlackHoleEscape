# main/connect.py
"""
Flask web server for BlackHoleEscape
- Serves the UI from templates/index.html
- Exposes API endpoints for the frontend (e.g., /api/escape/<login>)
"""

from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import os

from .main import BlackHoleEscape  # your class with generate_escape_plan(...)

def create_app():
    app = Flask(__name__, template_folder="../templates", static_folder="../static")
    CORS(app)

    client_id = os.getenv("FT_CLIENT_ID", "PUT_CLIENT_ID_HERE")
    client_secret = os.getenv("FT_CLIENT_SECRET", "PUT_CLIENT_SECRET_HERE")
    bhe = BlackHoleEscape(client_id, client_secret)

    @app.get("/")
    def home():
        """Serve the main UI."""
        return render_template("index.html")

    @app.get("/api/escape/<login>")
    def escape(login: str):
        """
        GET /api/escape/<login>
        Returns the computed Black Hole status and circle info for a 42 intra login.
        Returns 404 if user is not found.
        Returns 400 if there's an error processing the request.
        """
        try:
            result = bhe.generate_escape_plan(login)
            
            # Check if there was an error in the result
            if result.get("status", {}).get("error"):
                error_msg = result["status"]["error"]
                return jsonify({"error": error_msg}), 404
            
            return jsonify(result), 200
        except Exception as e:
            print(f"❌ Error processing escape plan for {login}: {e}")
            return jsonify({"error": str(e)}), 500

    @app.post("/api/circle")
    def circle():
        """
        POST /api/circle
        Body: { completed_projects: [...], current_level: 0.0 }
        Returns circle information computed from client-provided data.
        """
        data = request.get_json(force=True) or {}
        completed_projects = data.get("completed_projects", [])
        current_level = data.get("current_level", 0.0)
        info = bhe._calculate_circle_progress(completed_projects, current_level)
        return jsonify(info)

    return app

# For `python -m flask --app main.connect run --debug`
app = create_app()
