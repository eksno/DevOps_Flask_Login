import app

if __name__ == "__main__":
    app.serve_app(app.app)


"""
from app import app
from waitress import serve

if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=8080, url_scheme="https")
"""
