from flask import Flask, jsonify, request
from flask_cors import CORS
from data_search_poc import *

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Pre-initialize FHE setup
setup()


def FILTER_IT_NOW(bhk):
    return encrypted_search(bhk)


@app.route('/api/filter-options', methods=['GET'])
def filter_options():
    # Direct conversion and default handling
    bhk = request.args.get('bhk', type=int)
    if bhk is not None:
        average_rent = FILTER_IT_NOW(bhk)
        return jsonify(averageRent=average_rent)
    else:
        return jsonify(message="Invalid input"), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
