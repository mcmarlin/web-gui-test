import os
import pandas as pd
from flask import Flask, render_template
from collections import defaultdict

app = Flask(__name__)

# Function to load and prepare chart data
def load_chart_data():
    # Load Excel file
    excel_path = os.getenv("EXCEL_FILE", "data.xlsx")  # Allow dynamic file name
    df = pd.read_excel(excel_path)

    # Ensure expected columns exist
    required_columns = ["Subject Visit ID", "Tissue Type", "H&E_S1"]
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    # Normalize H&E_S1 values
    df["H&E_S1"] = df["H&E_S1"].fillna("Not-Done")
    df["H&E_S1"] = df["H&E_S1"].apply(lambda x: "Done" if str(x).strip().lower() == "done" else "Not-Done")

    # Prepare chart data
    charts = []
    for tissue_type, group in df.groupby("Tissue Type"):
        counts = defaultdict(int)
        for _, row in group.iterrows():
            counts[row["H&E_S1"]] += 1

        charts.append({
            "labels": list(counts.keys()),
            "values": list(counts.values()),
            "title": tissue_type
        })

    return charts


@app.route("/")
def index():
    try:
        chart_data = load_chart_data()
        return render_template("index.html", chart_data=chart_data)
    except Exception as e:
        return f"Error loading data: {str(e)}", 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

