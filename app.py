from flask import Flask, render_template, request, redirect, url_for
import asyncio
from main import scrape_product

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        product_name = request.form["product"]
        return redirect(url_for("results", query=product_name))
    return render_template("index.html")


@app.route("/results")
def results():
    query = request.args.get("query")
    if not query:
        return redirect(url_for("index"))

    # Run async scraper
    results_data = asyncio.run(scrape_product(query))
    return render_template("results.html", query=query, results=results_data)


if __name__ == "__main__":
    app.run(debug=True)
