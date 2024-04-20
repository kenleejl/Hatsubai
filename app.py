from flask import Flask, render_template, request, jsonify

# from flask_socketio import SocketIO, emit
from main import *

app = Flask(__name__)
# socketio = SocketIO(app, async_mode="threading")


@app.route("/")
def index():
    return render_template("index.html")


# @socketio.event
# def connect():
# print("client connected.")


@app.route("/query", methods=["POST"])
# @socketio.on("query")
# def handle_query(form_data):
# print(form_data)
def handle_query():
    query = request.values["query"]
    qty = request.values["qty"]
    strict = request.values["strict"] == "true"
    # query = form_data.get("query")
    # qty = form_data.get("qty")
    # strict = form_data.get("strict")
    if qty == "10":
        qty = None
    html = gsearch(query, results=qty)
    car_urls = get_valid_urls(html)
    keywords = query.split()
    if not strict:
        keywords = []
    urls = []
    for url in set(car_urls):
        strict_fail = any([kw.lower() not in url for kw in keywords])
        if strict_fail:
            print(f"Skipped {url} [STRICT MODE]")
            continue
        urls.append(url)
    # emit("urls", urls)
    return jsonify(urls)


# @socketio.on("get_data")
@app.route("/get_data", methods=["POST"])
def get_data():
    # Ensure the URL parameter is provided
    if "url" not in request.values:
        return jsonify({"error": "URL parameter is missing"}), 400

    url = request.values["url"]

    print(f"Getting data from {url}")
    # make url unique



    # Assuming get_name_date_price and get_html_carousell are defined elsewhere
    item = get_name_date_price(get_html_carousell(url))

    if not item:
        print(f"Skipped {url} [INVALID URL]")
        return jsonify({"error": "Invalid URL or data could not be retrieved"}), 404

    item["url"] = url
    print(item)

    # Try to return the item as JSON
    try:
        item_in_json = jsonify(item)
        return item_in_json
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": "Failed to serialize item"}), 500



if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
