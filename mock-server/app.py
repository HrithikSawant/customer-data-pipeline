from flask import Flask, jsonify, request
import json
import os

app = Flask(__name__)

DATA_FILE = os.path.join('data', 'customers.json')


def load_customers():
    with open(DATA_FILE, 'r') as f:
        return json.load(f)


@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"}), 200


@app.route('/api/customers', methods=['GET'])
def get_customers():
    customers = load_customers()

    # Pagination params
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
    except ValueError:
        return jsonify({"error": "Invalid pagination parameters"}), 400

    start = (page - 1) * limit
    end = start + limit

    paginated_data = customers[start:end]

    return jsonify({
        "data": paginated_data,
        "total": len(customers),
        "page": page,
        "limit": limit
    }), 200


@app.route('/api/customers/<int:customer_id>', methods=['GET'])
def get_customer(customer_id):
    customers = load_customers()

    customer = next(
        (c for c in customers if c['customer_id'] == customer_id),
        None
    )

    if not customer:
        return jsonify({"error": "Customer not found"}), 404

    return jsonify(customer), 200


if __name__ == "__main__":
    # Listen on all interfaces
    app.run(host="0.0.0.0", port=5000, debug=True)
