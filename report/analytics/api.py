# api.py

from flask import Flask, jsonify
from analytics.service import AnalyticsService

app = Flask(__name__)
service = AnalyticsService()

@app.route("/metrics/healing-rate")
def healing_rate():
    return jsonify(service.get_healing_success_rate())

@app.route("/metrics/history")
def healing_history():
    return jsonify(service.get_healing_history())

@app.route("/metrics/unstable-elements")
def unstable_elements():
    return jsonify(service.get_unstable_elements())
