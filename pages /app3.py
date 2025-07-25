# app.py
import io
import json
import pandas as pd
import streamlit as st

# ---------------------------------------------
# 1️⃣  Default trigger-phrase dictionaries
# ---------------------------------------------
DEFAULT_DICTIONARIES = {
    "urgency_marketing": {
        "limited", "limited time", "limited run", "limited edition",
        "order now", "last chance", "hurry", "while supplies last",
        "before they're gone", "selling out", "selling fast", "act now",
        "don't wait", "today only", "expires soon", "final hours", "almost gone",
    },
    "exclusive_marketing": {
        "exclusive", "exclusively", "exclusive offer", "exclusive deal",
        "members only", "vip", "special access", "invitation only",
        "premium", "privileged", "limited access", "select customers",
        "insider", "private sale", "early access",
    },
}

# Helper to classify a single text value
def classify(text: str, dictionaries) -> list[str]:
    if not isinstance(text, str):
        return []
    text = text.lower()
    return [cat for cat, terms in dictionaries.items() if any(t in text for t in terms)]

# ---------------------------------------------
# Streamlit UI
# ---------------------------------------------
st.set_page_config(page_title="Tactic Classifier", page_icon="🔍", layout="wide")
st.title("🔍 Marketing-Tactic Classifier")

# --- Upload section
st.header("1. Upload a CSV file")
uploaded_file = st.file_uploader("Choose a file", type=["csv"])

if uploaded_file:
    # Read the CSV into a dataframe
    df = pd.read_csv(uploaded_file)
    st.success(f"Loaded **{len(df):,}** rows.")
    st.write("Preview:", df.head())

    # Let the user pick the text column
    with st.form("column_form"):
        st.subheader("Which column contains the text to scan?")
        text_col = st.selectbox(
            "Text column",
            options=df.columns.tolist(),
            index=df.columns.get_loc("Statement") if "Statement" in df.columns else 0,
        )
        submitted_col = st.form_submit_button("Confirm column")
    if not submitted_col:
        st.stop()

    # --- Dictionary editor
    st.header("2. Edit or extend trigger-phrase dictionaries")
    # We work on a copy, so default dict is never mutated permanently
    dict_json = st.text_area(
        "Edit the JSON below and press **Apply changes**.",
        value=json.dumps(
            {k: sorted(list(v)) for k, v in DEFAULT_DICTIONARIES.items()},
            indent=2,
            ensure_ascii=False,
        ),
        height=300,
    )

    if st.button("Apply changes"):
        try:
            user_dict = json.loads(dict_json)
            # convert lists -> sets for faster lookup
            dictionaries = {k: set(v) for k, v in user_dict.items()}
            st.success("Dictionaries updated!")
        except (ValueError, TypeError) as e:
            st.error(f"❌ Invalid JSON: {e}")
            st.stop()
    else:
        dictionaries = DEFAULT_DICTIONARIES

    # --- Classification
    st.header("3. Classify")
    if st.button("Run classifier"):
        df["tactics"] = df[text_col].apply(lambda x: classify(x, dictionaries))
        st.dataframe(df.head(20))
        # --- Download
        csv_bytes = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Download full classified CSV",
            data=csv_bytes,
            file_name="classified_data.csv",
            mime="text/csv",
        )
else:
    st.info("👆 Upload a CSV file to get started.")
