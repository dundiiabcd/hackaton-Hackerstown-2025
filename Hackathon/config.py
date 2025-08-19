import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'mysql+pymysql://root@localhost:3307/eco_consumo')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    OPEN_FOOD_FACTS_API_URL = "https://world.openfoodfacts.org/api/v2/product/"