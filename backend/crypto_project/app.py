from flask import Flask, jsonify, request
from flask_cors import CORS
from data_search_poc import *
from openfhe import *

app = Flask(__name__)
CORS(app)


def FILTER_IT_NOW(bhk, city, furnishing_status, bathroom):
    # Dummy function to simulate filtering and calculating average rent
    # Replace this logic with your actual database query or calculation
    setup()
    encrypted_search(bhk)
    return 25000  # Dummy average rent value


@app.route('/api/filter-options', methods=['GET'])
def filter_options():
    bhk = request.args.get('bhk')
    city = request.args.get('city')
    furnishing_status = request.args.get('furnishingStatus')
    bathroom = request.args.get('bathroom')

    average_rent = FILTER_IT_NOW(bhk, city, furnishing_status, bathroom)
    return jsonify(averageRent=average_rent)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
