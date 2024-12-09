from flask import Flask, request, jsonify, g, render_template
from db import Database
import os
import threading

app = Flask(__name__, template_folder=os.path.abspath('templates'))
db_name = 'my_database.db'

def get_db():
    if 'db' not in g:
        g.db = Database(db_name)
        g.db.init_db()
    return g.db

@app.teardown_appcontext
def close_db(error):
    db = g.pop('db', None)
    if db is not None:
        db.disconnect()

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"}), 200

@app.route('/reset', methods=['POST'])
def reset_database():
    db = get_db()
    db.init_db()
    return jsonify({"message": "Database reset successfully"}), 200

@app.route('/shutdown', methods=['GET'])
def shutdown():
    def shutdown_server():
        os._exit(0)
    threading.Timer(0.1, shutdown_server).start()
    return jsonify({"message": "Server is shutting down..."}), 200

@app.route('/user', methods=['POST'])
def add_user():
    data = request.get_json(force=True)
    if not data or 'name' not in data or 'email' not in data:
        return jsonify({'error': 'Invalid input. Name and email are required.'}), 400
    
    try:
        db = get_db()
        user_id = db.add_user(data['name'], data['email'])
        return jsonify({'id': user_id}), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        app.logger.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

@app.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    db = get_db()
    user = db.get_user(user_id)
    if user:
        return render_template('user.html', user={'id': user[0], 'name': user[1], 'email': user[2]})
    return render_template('user.html', error='User not found'), 404

@app.route('/users', methods=['GET'])
def get_users():
    db = get_db()
    users = db.get_all_users()
    return jsonify(users), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
