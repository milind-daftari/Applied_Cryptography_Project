from flask import Flask, jsonify, request
from flask_cors import CORS
from data_search_poc import *
from openfhe import *

app = Flask(__name__)
# Configure CORS specifically for requests from the frontend at http://localhost:3000
CORS(app, resources={r"/api/*": {"origins": ["http://localhost:3000"]}})


def FILTER_IT_NOW(bhk, city, furnishing_status, bathroom):
    # Dummy function to simulate filtering and calculating average rent
    # This function initializes the FHE setup and performs an encrypted search
    setup()
    encrypted_search(bhk)
    return 25000  # Return a dummy average rent value


@app.route('/api/filter-options', methods=['GET'])
def filter_options():
    # Extract parameters from query string
    bhk = request.args.get('bhk')
    city = request.args.get('city')
    furnishing_status = request.args.get('furnishingStatus')
    bathroom = request.args.get('bathroom')

    # Compute the average rent based on the input parameters
    average_rent = FILTER_IT_NOW(bhk, city, furnishing_status, bathroom)

    # Return the average rent in a JSON response
    return jsonify(averageRent=average_rent)


if __name__ == '__main__':
    # Run the Flask app on all available interfaces and enable debug mode
    app.run(host='0.0.0.0', debug=True)
