from flask import Flask, jsonify
from smartgrid_fetcher import fetch_and_send_demand_data

app = Flask(__name__)

@app.route("/", methods=["GET"])
def root():
    return "Smart Data Ingestor (Kafka Version) is running.", 200

@app.route("/fetch-and-publish", methods=["GET"])
def trigger_fetch_and_publish():
    try:
        result = fetch_and_send_demand_data()
        return jsonify({"status": result}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5104)
