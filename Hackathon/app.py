from flask import Flask, render_template
from flask_restful import Api
from models import db
from resources import ProductResource, EvaluateResource
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    api = Api(app)

    # Cria as tabelas no DB se não existirem
    with app.app_context():
        db.create_all()

    # Rotas da API
    api.add_resource(ProductResource, '/products/', '/products/<string:barcode>')
    api.add_resource(EvaluateResource, '/products/evaluate')

    # Interface web simples (página inicial para teste)
    @app.route('/')
    def index():
        return render_template('index.html')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)