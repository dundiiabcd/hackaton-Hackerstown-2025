from flask_restful import Resource, reqparse
from models import db, Product
import requests
from flask import jsonify, request, current_app
from sqlalchemy.exc import SQLAlchemyError

class ProductResource(Resource):
    def get(self, barcode=None):
        if barcode is None:
            barcode = request.args.get('barcode')
            if not barcode:
                return {'message': 'Código de barras não fornecido'}, 400
        # Remove espaços do código de barras
        barcode = barcode.replace(" ", "")

        # Verifica se o produto já está no DB
        try:
            product = Product.query.filter_by(barcode=barcode).first()
            if product:
                current_app.logger.info(f"Produto encontrado no DB: {product.to_dict()}")
                return product.to_dict(), 200
        except SQLAlchemyError as e:
            current_app.logger.error(f"Erro ao buscar produto no DB: {e}")
            return {'message': 'Erro interno ao consultar o banco de dados'}, 500

        # Fetch da Open Food Facts API
        try:
            url = f"{current_app.config['OPEN_FOOD_FACTS_API_URL']}{barcode}"
            current_app.logger.info(f"Requisição à API: {url}")
            response = requests.get(url, timeout=10)  # Aumentado para 10 segundos
            response.raise_for_status()
            data = response.json()
            current_app.logger.info(f"Resposta da API: {data}")

            if not data.get('product'):
                return {'message': 'Produto não encontrado na Open Food Facts'}, 404

            product_data = data['product']
            name = product_data.get('product_name', 'Nome desconhecido')
            eco_score = product_data.get('ecoscore_grade', 'Não disponível')
            current_app.logger.info(f"Eco-score retornado: {eco_score}")
            
            eco_desc = 'Dados detalhados não disponíveis.'
            eco_data = product_data.get('ecoscore_data', {})
            if eco_data:
                agribalyse_data = eco_data.get('agribalyse', {})
                if agribalyse_data:
                    warning = agribalyse_data.get('warning', 'Sem aviso específico.')
                    impacts = agribalyse_data.get('impacts', {})
                    
                    co2e = impacts.get('carbon', 'N/A')
                    water = impacts.get('water', 'N/A')
                    land = impacts.get('land', 'N/A')
                    
                    eco_desc = (
                        f"{warning} "
                        f"Impactos estimados: CO2e: {co2e}g, "
                        f"Água: {water}L, Uso de terra: {land}m²."
                    )

            # Salva no DB
            new_product = Product(barcode=barcode, name=name, eco_score=eco_score, eco_score_description=eco_desc)
            db.session.add(new_product)
            db.session.commit()
            current_app.logger.info(f"Produto salvo no DB: {new_product.to_dict()}")
            return new_product.to_dict(), 201
        
        except requests.exceptions.Timeout:
            current_app.logger.error(f"Timeout ao conectar à Open Food Facts para {barcode}")
            return {'message': 'Tempo limite excedido ao buscar dados do produto.'}, 504
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Erro ao conectar à Open Food Facts para {barcode}: {e}")
            return {'message': 'Erro ao buscar dados do produto na Open Food Facts.'}, 503
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f"Erro ao salvar produto no DB: {e}")
            return {'message': 'Erro interno ao salvar o produto.'}, 500
        except Exception as e:
            current_app.logger.error(f"Erro inesperado no ProductResource.get para {barcode}: {e}")
            return {'message': 'Ocorreu um erro inesperado.'}, 500

class EvaluateResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('barcode', type=str, required=True, help='Código de barras é obrigatório')
    parser.add_argument('custom_evaluation', type=float, required=True, help='Avaliação personalizada é obrigatória')

    def post(self):
        args = self.parser.parse_args()
        barcode = args['barcode']
        custom_evaluation = args['custom_evaluation']

        if not (0 <= custom_evaluation <= 10):
            return {'message': 'A avaliação personalizada deve ser entre 0 e 10.'}, 400

        try:
            product = Product.query.filter_by(barcode=barcode).first()
            if not product:
                return {'message': 'Produto não encontrado para avaliação'}, 404

            product.custom_evaluation = custom_evaluation
            db.session.commit()
            return product.to_dict(), 200
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f"Erro ao atualizar avaliação personalizada para {barcode}: {e}")
            return {'message': 'Erro interno ao atualizar a avaliação.'}, 500
        except Exception as e:
            current_app.logger.error(f"Erro inesperado no EvaluateResource.post para {barcode}: {e}")
            return {'message': 'Ocorreu um erro inesperado.'}, 500