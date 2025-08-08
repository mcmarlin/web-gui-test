from flask import Flask, render_template, jsonify
import pandas as pd
import os

app = Flask(__name__)

# Load the spreadsheet
def load_data(file_path):
    df = pd.read_excel(file_path)

    # Create a new column for the first digit of Subject Visit ID
    df["VisitPrefix"] = df["Subject Visit ID"].astype(str).str[0]

    # Group by VisitPrefix, Tissue Type, and H&E_S1
    grouped = (
        df.groupby(["VisitPrefix", "Tissue Type", "H&E_S1"])
        .size()
        .reset_index(name="Count")
    )

    return grouped

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/data")
def data():
    file_path = "data.xlsx"  # Change this path if you want a different file
    grouped = load_data(file_path)

    # Prepare chart data
    chart_data = {}
    for prefix in grouped["VisitPrefix"].unique():
        subset = grouped[grouped["VisitPrefix"] == prefix]
        labels = subset["Tissue Type"].unique().tolist()

        done_counts = []
        not_done_counts = []
        for label in labels:
            done = subset[(subset["Tissue Type"] == label) & (subset["H&E_S1"] == "Done")]["Count"].sum()
            not_done = subset[(subset["Tissue Type"] == label) & (subset["H&E_S1"] == "Not-Done")]["Count"].sum()
            done_counts.append(done)
            not_done_counts.append(not_done)

        chart_data[prefix] = {
            "labels": labels,
            "done": done_counts,
            "not_done": not_done_counts
        }

    return jsonify(chart_data)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render will set PORT
    app.run(host="0.0.0.0", port=port)
