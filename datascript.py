import pandas as pd
import re
import numpy as np

# 1. Fix malformed 'crore' values
def clean_crore(value):
    if pd.isna(value):
        return np.nan
    value = str(value).replace(",", "")
    if value.count('.') > 1:
        parts = value.split('.')
        value = ''.join(parts[:-1]) + '.' + parts[-1]
    try:
        return float(value)
    except ValueError:
        return np.nan

# 2. Fix large numbers stored as text or malformed numbers
def fix_number(value):
    if pd.isna(value):
        return np.nan
    value = str(value).replace(",", "").replace("’", "").strip()
    if value.count('.') > 1:
        parts = value.split('.')
        value = ''.join(parts[:-1]) + '.' + parts[-1]
    try:
        return float(value)
    except:
        return np.nan

# 3. Standardize and load any of the three Excel datasets
def load_clean(file, platform, date_col, banks_col, vol_col, amt_col, tag_col=None):
    df = pd.read_excel(file, na_values=["", " "]).replace(r'^\s*$', np.nan, regex=True)

    df = df.rename(columns={
        date_col: "Date",
        banks_col: "Banks",
        vol_col: "Volume_Mn",
        amt_col: "Amount_Cr"
    })

    df["Platform"] = platform
    df["Tag_Issued"] = df[tag_col] if tag_col and tag_col in df.columns else np.nan

    # Clean each numeric column
    df["Amount_Cr"] = df["Amount_Cr"].apply(clean_crore)
    for col in ["Banks", "Volume_Mn", "Tag_Issued"]:
        df[col] = df[col].apply(fix_number)

    # Convert 'Amount_Cr' to absolute rupees
    df["Amount_INR"] = df["Amount_Cr"] * 1e7
    df = df.drop(columns=["Amount_Cr"])

    # Standardize date format
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce").dt.to_period("M").astype(str)

    return df[["Date", "Platform", "Banks", "Volume_Mn", "Amount_INR", "Tag_Issued"]]

# 4. Load all 3 sheets
upi = load_clean("upi.xlsx", "UPI", "Month", "No. of Banks live on UPI", "Volume (in Mn)", "Value (in Cr.)")
imps = load_clean("imps.xlsx", "IMPS", "Month", "No. of Member Banks", "Volume (in Mn)", "Value (in Cr.)")
fastag = load_clean("fastag.xlsx", "NETC", "Month", "No. of Banks Live on NETC", "Volume (In Mn)", "Amount (In Cr)", "Tag Issuance (In Nos.)")

# 5. Combine and filter data
combined = pd.concat([upi, imps, fastag], ignore_index=True)
combined["Date"] = pd.to_datetime(combined["Date"], errors="coerce")
combined = combined[combined["Date"] >= "2016-11-01"]
combined["Date"] = combined["Date"].dt.to_period("M").astype(str)
combined = combined.sort_values(by=["Date", "Platform"]).reset_index(drop=True)

# 6. Save to Excel with clean numeric formatting
output_file = "final_cashless_payments_inr.xlsx"
combined.to_excel(output_file, index=False, float_format="%.2f", na_rep="NaN")

print(f"Final output saved as '{output_file}' with proper numeric types and no text formatting.")
