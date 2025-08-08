from flask import Flask, render_template
import pandas as pd
import os

app = Flask(__name__)

@app.route("/")
def index():
    # Always define defaults so Jinja never sees 'Undefined'
    chart_data = {}
    error_message = None

    try:
        # Path to spreadsheet
        excel_path = os.path.join(os.path.dirname(__file__), "data.xlsx")

        # Load Excel
        df = pd.read_excel(excel_path)

        # Strip whitespace from column names
        df.columns = df.columns.str.strip()

        # Required columns
        required_columns = ["Subject Visit ID", "Tissue Type", "H&E_S1"]
        for col in required_columns:
            if col not in df.columns:
                raise ValueError(f"Missing required column: {col}")

        # Create a 'group' column for Subject Visit ID start number
        df["ID_Start"] = df["Subject Visit ID"].astype(str).str[0]

        # Group by ID_Start, Tissue Type, and H&E_S1 status
        grouped = df.groupby(["ID_Start", "Tissue Type", "H&E_S1"]).size().reset_index(name="Count")

        # Convert to nested dict: {group: {"Done": x, "Not-Done": y}}
        chart_data = {}
        for _, row in grouped.iterrows():
            group_label = f"{row['ID_Start']} - {row['Tissue Type']}"
            status = row["H&E_S1"]
            if group_label not in chart_data:
                chart_data[group_label] = {"Done": 0, "Not-Done": 0}
            if status == "Done":
                chart_data[group_label]["Done"] += row["Count"]
            else:
                chart_data[group_label]["Not-Done"] += row["Count"]

    except Exception as e:
        error_message = f"Error loading data: {e}"

    return render_template("index.html", chart_data=chart_data, error_message=error_message)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

