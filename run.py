import os
from app import create_app
from config import get_config   # ✅ importa a função que decide o ambiente

app = create_app(get_config())

if __name__ == "__main__":
    host = os.environ.get("FLASK_RUN_HOST", "0.0.0.0")
    port = int(os.environ.get("FLASK_RUN_PORT", 5000))
    app.run(host=host, port=port, debug=app.config["DEBUG"])
