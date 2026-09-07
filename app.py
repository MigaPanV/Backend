from flask import Flask
from routes.horario_route import routes
from config import Config
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
app.config.from_object(Config)
app.register_blueprint(routes)

if __name__ == "__main__":
    app.run(debug=app.config['DEBUG'])