from flask import Flask, render_template
import pandas as pd

app = Flask(__name__)

@app.route('/')
def index():
    df = pd.read_excel("data.xlsx")

    # Filter rows starting with 4, 5, 6, or 7
    df['Subject Visit ID'] = df['Subject Visit ID'].astype(str)
    df_filtered = df[df['Subject Visit ID'].str.startswith(('4','5','6','7'))]

    # Classify H&E_S1 as Done/Not-Done robustly
    def classify_status(val):
        if isinstance(val, str) and val.strip().lower() == "done":
            return "Done"
        if str(val).strip() in ["1", "True", "true"]:
            return "Done"
        return "Not-Done"

    df_filtered['H&E_S1'] = df_filtered['H&E_S1'].apply(classify_status)

    # Group by first digit of Subject Visit ID + Tissue Type
    df_filtered['Group'] = df_filtered['Subject Visit ID'].str[0] + " - " + df_filtered['Tissue Type']

    # Count Done/Not-Done for each group
    pivot = df_filtered.pivot_table(index='Group', columns='H&E_S1', aggfunc='size', fill_value=0)

    if "Done" not in pivot.columns:
        pivot["Done"] = 0
    if "Not-Done" not in pivot.columns:
        pivot["Not-Done"] = 0

    chart_data = {
        'labels': list(pivot.index),
        'done': list(pivot["Done"]),
        'not_done': list(pivot["Not-Done"])
    }

    return render_template("index.html", chart_data=chart_data)

if __name__ == '__main__':
    app.run(debug=True)