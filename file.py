from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        # Parse the incoming JSON data
        data = request.get_json()

        # Check if the data is valid
        if not data or 'message' not in data:
            return jsonify({'error': 'Invalid input'}), 400

        # Example processing logic (replace with your actual code)
        user_message = data['message']
        response_message = f"Echo: {user_message}"

        # Return a successful JSON response
        return jsonify({'response': response_message}), 200

    except Exception as e:
        # Log the exception with details
        app.logger.error(f"Exception occurred: {e}", exc_info=True)

        # Return a generic error message to the client
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True)
    app.run(host='127.0.0.1', port=5000, debug=True)

# Test with:
# curl -X POST http://127.0.0.1:5000/api/chat -H "Content-Type: application/json" -d '{"message": "Hello"}'
    app.run(host='127.0.0.1', port=5000, debug=True)

# Test with:
# curl -X POST http://127.0.0.1:5000/api/chat -H "Content-Type: application/json" -d '{"message": "Hello"}'
