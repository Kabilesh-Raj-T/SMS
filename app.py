import mysql.connector
from flask import Flask, g, jsonify, request
from flask_cors import CORS # Will be used later

# Database Configuration (Consider moving to a config file or environment variables)
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWD = "Kabilesh1!"
DB_NAME = "sms_database"

app = Flask(__name__)
CORS(app) # Enable CORS for all routes

def get_db():
    """Opens a new database connection if there is none yet for the current application context."""
    if 'db' not in g:
        g.db = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            passwd=DB_PASSWD,
            database=DB_NAME
        )
    return g.db

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

# --- Original Database Class (modified for Flask context) ---
# We will mostly use get_db() directly, but this class structure can be adapted if preferred.
# For now, the manager classes will expect a connection and cursor directly.

class Database:
    def __init__(self):
        # This init is now less relevant as we use get_db() for connection management per request.
        # However, methods could be adapted to use g.db if a class instance is preferred.
        pass

    def execute(self, query, values=None):
        cursor = get_db().cursor()
        cursor.execute(query, values or ())
        return cursor

    def commit(self):
        get_db().commit()

    def fetch_all(self, cursor): # Modified to accept cursor
        return cursor.fetchall()

    def fetch_one(self, cursor): # Added helper
        return cursor.fetchone()

from models import init_app as init_db_app, product_mgr, customer_mgr, employee_mgr, finance_mgr, stat_mgr

# Initialize database handling for the app
init_db_app(app)

# --- Helper for error responses ---
def make_error_response(message, status_code):
    return jsonify({"error": message}), status_code

# --- Product Routes ---
@app.route('/products', methods=['GET'])
def get_all_products():
    products = product_mgr.view_all()
    return jsonify(products), 200

@app.route('/products/<string:product_id>', methods=['GET'])
def get_product(product_id):
    product_info, status_code = product_mgr.search_product_by_id_manager(product_id)
    if status_code == 404:
        return make_error_response(product_info["error"], status_code)
    return jsonify(product_info), status_code

@app.route('/products', methods=['POST'])
def create_product():
    if not request.json:
        return make_error_response("Missing JSON in request", 400)

    data = request.json
    # Basic validation - more can be added here or in the manager
    required_fields = ['ID', 'NAME', 'SELLING_PRICE', 'COST_PRICE', 'BRAND', 'QUANTITY', 'ITEMS_SOLD']
    if not all(field in data for field in required_fields):
        return make_error_response(f"Missing one or more required fields: {', '.join(required_fields)}", 400)

    response, status_code = product_mgr.add_product(data)
    if "error" in response:
        return make_error_response(response["error"], status_code)
    return jsonify(response), status_code

@app.route('/products/<string:product_id>', methods=['PUT'])
def update_product(product_id):
    if not request.json:
        return make_error_response("Missing JSON in request", 400)

    update_data = request.json
    if not update_data:
        return make_error_response("No update data provided", 400)

    response, status_code = product_mgr.edit_product(product_id, update_data)
    if "error" in response and status_code != 200: # edit_product might return 200 with a "no change" message
        return make_error_response(response["error"], status_code)
    return jsonify(response), status_code

@app.route('/products/<string:product_id>', methods=['DELETE'])
def remove_product(product_id):
    response, status_code = product_mgr.delete_product(product_id)
    if "error" in response:
        return make_error_response(response["error"], status_code)
    return jsonify(response), status_code


@app.route('/purchases', methods=['POST'])
def record_purchase():
    if not request.json:
        return make_error_response("Missing JSON in request", 400)

    data = request.json
    customer_contact = data.get('customer_contact')
    purchase_items = data.get('items') # Expecting a list of {'product_id': ..., 'quantity': ...}
    customer_name_if_new = data.get('customer_name') # Optional, but required if customer is new

    if not customer_contact or not purchase_items:
        return make_error_response("Missing 'customer_contact' or 'items' in request body.", 400)

    if not isinstance(purchase_items, list) or not all(isinstance(item, dict) and 'product_id' in item and 'quantity' in item for item in purchase_items):
        return make_error_response("Field 'items' must be a list of objects with 'product_id' and 'quantity'.", 400)

    # The ProductManager.make_purchase method now handles new customer creation internally if customer_name_if_new is provided.
    # It returns a tuple (response_dict, status_code)
    response, status_code = product_mgr.make_purchase(customer_contact, purchase_items, customer_name_if_new)

    if "error" in response: # Check if the response dictionary contains an error key
        return make_error_response(response["error"], status_code)
    return jsonify(response), status_code

# --- Customer Routes ---
@app.route('/customers', methods=['GET'])
def get_all_customers():
    customers = customer_mgr.view_all_customers()
    return jsonify(customers), 200

@app.route('/customers/<string:customer_id>', methods=['GET'])
def get_customer(customer_id):
    # Assuming search_customer_by_id_manager returns (data, status_code) or (error_dict, status_code)
    customer_info, status_code = customer_mgr.search_customer_by_id_manager(customer_id)
    if "error" in customer_info and status_code != 200: # Check if it's an error response
        return make_error_response(customer_info["error"], status_code)
    return jsonify(customer_info), status_code

@app.route('/customers', methods=['POST'])
def create_customer():
    if not request.json:
        return make_error_response("Missing JSON in request", 400)

    data = request.json
    required_fields = ['ID', 'NAME', 'CONTACT_NUMBER'] # GENDER, EMAIL are optional
    if not all(field in data for field in required_fields):
        return make_error_response(f"Missing one or more required fields: {', '.join(required_fields)}", 400)

    # add_customer returns (response_dict, status_code)
    response, status_code = customer_mgr.add_customer(data)
    if "error" in response:
        return make_error_response(response["error"], status_code)
    return jsonify(response), status_code

@app.route('/customers/<string:customer_id>', methods=['PUT'])
def update_customer(customer_id):
    if not request.json:
        return make_error_response("Missing JSON in request", 400)

    update_data = request.json
    if not update_data:
        return make_error_response("No update data provided", 400)

    # edit_customer returns (response_dict, status_code)
    response, status_code = customer_mgr.edit_customer(customer_id, update_data)
    if "error" in response and status_code != 200:
        return make_error_response(response["error"], status_code)
    return jsonify(response), status_code

@app.route('/customers/<string:customer_id>', methods=['DELETE'])
def remove_customer(customer_id):
    # delete_customer returns (response_dict, status_code)
    response, status_code = customer_mgr.delete_customer(customer_id)
    if "error" in response:
        return make_error_response(response["error"], status_code)
    return jsonify(response), status_code

# --- Employee Routes ---
@app.route('/employees', methods=['GET'])
def get_all_employees():
    employees = employee_mgr.view_all_employees()
    return jsonify(employees), 200

@app.route('/employees/<string:emp_id>', methods=['GET'])
def get_employee(emp_id):
    # Assuming search_employee_by_id_manager returns (data, status_code) or (error_dict, status_code)
    employee_info, status_code = employee_mgr.search_employee_by_id_manager(emp_id)
    if "error" in employee_info and status_code != 200: # Check if it's an error response
        return make_error_response(employee_info["error"], status_code)
    return jsonify(employee_info), status_code

@app.route('/employees', methods=['POST'])
def create_employee():
    if not request.json:
        return make_error_response("Missing JSON in request", 400)

    data = request.json
    required_fields = ['ID', 'NAME', 'CONTACT_NUMBER', 'GENDER', 'POSITION', 'SALARY']
    if not all(field in data for field in required_fields):
        return make_error_response(f"Missing one or more required fields: {', '.join(required_fields)}", 400)

    # add_employee returns (response_dict, status_code)
    response, status_code = employee_mgr.add_employee(data)
    if "error" in response:
        return make_error_response(response["error"], status_code)
    return jsonify(response), status_code

@app.route('/employees/<string:emp_id>', methods=['PUT'])
def update_employee(emp_id):
    if not request.json:
        return make_error_response("Missing JSON in request", 400)

    update_data = request.json
    if not update_data:
        return make_error_response("No update data provided", 400)

    # edit_employee returns (response_dict, status_code)
    response, status_code = employee_mgr.edit_employee(emp_id, update_data)
    if "error" in response and status_code != 200:
        return make_error_response(response["error"], status_code)
    return jsonify(response), status_code

@app.route('/employees/<string:emp_id>', methods=['DELETE'])
def remove_employee(emp_id):
    # delete_employee returns (response_dict, status_code)
    response, status_code = employee_mgr.delete_employee(emp_id)
    if "error" in response:
        return make_error_response(response["error"], status_code)
    return jsonify(response), status_code

# --- Finance Routes ---
@app.route('/finance/profit-by-product', methods=['GET'])
def get_profit_by_product():
    data = finance_mgr.profit_by_product()
    return jsonify(data), 200

@app.route('/finance/total-profit-loss', methods=['GET'])
def get_total_profit_loss():
    data = finance_mgr.total_profit_or_loss()
    return jsonify(data), 200

# --- Statistics Routes ---
@app.route('/stats/best-selling-product', methods=['GET'])
def get_best_selling_product():
    data = stat_mgr.best_selling_product()
    if "message" in data and ("No products found" in data["message"] or "no sales data available" in data["message"]):
        # Could return 404 if no data, or 200 with the message. Let's be consistent with current manager returns.
        return jsonify(data), 200 # Or 404 if preferred for "not found" type scenarios
    return jsonify(data), 200

@app.route('/stats/most-profitable-product', methods=['GET'])
def get_most_profitable_product():
    data = stat_mgr.most_profitable_product()
    if "message" in data and ("No products found" in data["message"] or "no sales data available" in data["message"]):
        return jsonify(data), 200 # Or 404
    return jsonify(data), 200

@app.route('/stats/least-selling-product', methods=['GET'])
def get_least_selling_product():
    data = stat_mgr.least_selling_product()
    if "message" in data and "No products found" in data["message"]:
        return jsonify(data), 200 # Or 404
    return jsonify(data), 200

# --- Fallback Routes ---
@app.route('/')
def hello():
    return jsonify(message="Welcome to the Store Management API!"), 200

if __name__ == '__main__':
    # It's good practice to get port from environment or config
    # For development, ensure MySQL server is running and accessible with provided credentials.
    app.run(debug=True, port=5000)
