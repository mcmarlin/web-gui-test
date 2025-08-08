from flask import Flask, render_template
import pandas as pd
import os

app = Flask(__name__)

@app.route("/")
def index():
    chart_data = {}
    error_message = None

    try:
        # Path to your Excel file (adjust if needed)
        excel_path = os.path.join(os.path.dirname(__file__), "data.xlsx")

        # Load Excel file
        df = pd.read_excel(excel_path)

        # Normalize column names (strip spaces)
        df.columns = df.columns.str.strip()

        # Required columns
        required_columns = ["Subject Visit ID", "Tissue Type", "H&E_S1"]
        for col in required_columns:
            if col not in df.columns:
                raise ValueError(f"Missing required column: {col}")

        # Create column for first digit of Subject Visit ID
        df["ID_Start"] = df["Subject Visit ID"].astype(str).str[0]

        # Filter only IDs starting with 4,5,6,7
        allowed_prefixes = {"4", "5", "6", "7"}
        df = df[df["ID_Start"].isin(allowed_prefixes)]

        # Clean H&E_S1 column: fill missing and normalize to "Done"/"Not-Done"
        df["H&E_S1"] = df["H&E_S1"].fillna("Not-Done")
        df["H&E_S1"] = df["H&E_S1"].apply(
            lambda x: "Done" if str(x).strip().lower() == "done" else "Not-Done"
        )

        # Group data by ID_Start, Tissue Type, and H&E_S1 status
        grouped = df.groupby(["ID_Start", "Tissue Type", "H&E_S1"]).size().reset_index(name="Count")

        # Aggregate counts into a dict for charting
        chart_data = {}
        for _, row in grouped.iterrows():
            group_label = f"{row['ID_Start']} - {row['Tissue Type']}"
            status = row["H&E_S1"]
            if group_label not in chart_data:
                chart_data[group_label] = {"Done": 0, "Not-Done": 0}
            chart_data[group_label][status] += row["Count"]

    except Exception as e:
        error_message = f"Error loading data: {e}"

    return render_template("index.html", chart_data=chart_data, error_message=error_message)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
