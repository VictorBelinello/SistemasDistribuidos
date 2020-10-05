from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


from server.market import market_bp
app.register_blueprint(market_bp)


from server.interests import interests_bp
app.register_blueprint(interests_bp)

from server.subscriptions import subscriptions_bp
app.register_blueprint(subscriptions_bp)

from server.transactions import transactions_bp
app.register_blueprint(transactions_bp)
    
