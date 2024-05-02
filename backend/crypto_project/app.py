from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Dummy data for demonstration purposes
rental_data = [
    {"BHK": 3, "Rent": 25000, "Size": 1200, "Floor": "3 out of 5", "AreaType": "Super Area", "AreaLocality": "Marathalli",
        "City": "Bangalore", "FurnishingStatus": "Furnished", "TenantPreferred": "Family", "Bathroom": 2, "PointOfContact": "Owner"},
    # Add more entries as needed
]

# Assuming each property in rental_data has all the keys
available_filters = {key: set() for key in rental_data[0].keys()}
for entry in rental_data:
    for key, value in entry.items():
        available_filters[key].add(value)


@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/api/filter-options')
def filter_options():
    category = request.args.get('category', 'BHK')
    if category in available_filters:
        return jsonify(options=list(available_filters[category]))
    else:
        return jsonify({"error": "Invalid category"}), 400


@app.route('/api/rental-data')
def rental_data_api():
    filter_key = request.args.get('filter')
    filter_value = request.args.get('value')
    if not filter_key or not filter_value:
        return jsonify({"error": "Filter key and value required"}), 400

    filtered_data = [entry for entry in rental_data if entry.get(
        filter_key) == filter_value]
    return jsonify(filtered_data)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
