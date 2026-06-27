from flask import Flask, jsonify

app = Flask(__name__)
flask==3.0.0

@app.route("/")
def home():
    return jsonify({"message": "Backend Flask running"})

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)