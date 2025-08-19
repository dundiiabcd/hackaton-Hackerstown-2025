from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    barcode = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    eco_score = db.Column(db.String(10))  # Ex.: 'A', 'B', etc. do Open Food Facts
    eco_score_description = db.Column(db.Text)  # Descrição do impacto ambiental
    custom_evaluation = db.Column(db.Float)  # Nota personalizada (0-10)

    def __init__(self, barcode, name, eco_score, eco_score_description, custom_evaluation=None):
        self.barcode = barcode
        self.name = name
        self.eco_score = eco_score
        self.eco_score_description = eco_score_description
        self.custom_evaluation = custom_evaluation

    def to_dict(self):
        return {
            'barcode': self.barcode,
            'name': self.name,
            'eco_score': self.eco_score,
            'eco_score_description': self.eco_score_description,
            'custom_evaluation': self.custom_evaluation
        }