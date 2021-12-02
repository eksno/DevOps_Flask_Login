from app import app
from waitress import serve
import logging

if __name__ == "__main__":
    logging.basicConfig(filename="app.log", filemode="w", level=logging.DEBUG)
    serve(app, host="0.0.0.0", port=8080, url_scheme="https")
