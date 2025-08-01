import streamlit as st
import pandas as pd
import nltk
import re, json, io
import emoji
from packaging import version

# Ensure NLTK sentence tokenizer resources are available
nltk.download("punkt", quiet=True)
if version.parse(nltk.__version__) >= version.parse("3.9"):
    nltk.download("punkt_tab", quiet=True)

st.set_page_config(page_title="IG Caption Transformer", page_icon="📄", layout="centered")

st.title("📄 Instagram Caption Transformer")
st.markdown(
    """
    Upload an Instagram posts CSV, tweak the **column‑rename mapping** in the sidebar if needed, 
    and download a sentence‑level, emoji‑stripped CSV – perfect for further NLP!
    """
)

# ---------------------------- Sidebar: configuration ---------------------------------
st.sidebar.header("🔧 Configuration")

default_mapping = {"shortcode": "ID", "caption": "Context"}

mapping_json = st.sidebar.text_area(
    "Column‑rename mapping (JSON)",
    value=json.dumps(default_mapping, indent=2),
    height=120,
    help="Keys are current column names ➡️ values are the desired names. 'ID' & 'Context' must exist after renaming."
)

try:
    rename_mapping = json.loads(mapping_json or "{}")
    if not isinstance(rename_mapping, dict):
        raise ValueError
except (json.JSONDecodeError, ValueError):
    st.sidebar.error("⚠️ Invalid JSON – using the default mapping.")
    rename_mapping = default_mapping

remove_emoji = st.sidebar.checkbox("Remove all emoji", value=True)

# ---------------------------- Core logic ----------------------------------------------

def clean_sentence(txt: str, strip_emoji: bool = True) -> str:
    """Normalise whitespace, optionally strip emoji, and ensure terminal punctuation."""
    txt = txt.replace("’", "'")
    if strip_emoji:
        txt = emoji.replace_emoji(txt, replace="")
    txt = re.sub(r"\s+", " ", txt).strip()
    if txt and txt[-1] not in ".!?":
        txt += "."
    return txt

uploaded_file = st.file_uploader("📤 Upload CSV file", type=["csv"])  # main input

if uploaded_file is not None:
    try:
        raw_df = pd.read_csv(uploaded_file)
    except Exception as e:
        st.error(f"❌ Could not read CSV: {e}")
        st.stop()

    # Apply rename mapping
    raw_df = raw_df.rename(columns=rename_mapping)

    required_cols = {"ID", "Context"}
    if not required_cols.issubset(raw_df.columns):
        missing = required_cols - set(raw_df.columns)
        st.error(f"❌ Columns missing after renaming: {', '.join(missing)}")
        st.stop()

    # Explode captions → sentences
    records = []
    for _, row in raw_df.iterrows():
        for idx, sent in enumerate(nltk.sent_tokenize(str(row["Context"])), 1):
            records.append(
                {
                    "ID": row["ID"],
                    "Sentence ID": idx,
                    "Context": row["Context"],
                    "Statement": clean_sentence(sent, strip_emoji=remove_emoji),
                }
            )

    out_df = pd.DataFrame(records)

    st.subheader("👀 Preview (first 10 rows)")
    st.dataframe(out_df.head(10), use_container_width=True)

    # Download button
    csv_bytes = out_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "💾 Download transformed CSV",
        data=csv_bytes,
        file_name="ig_posts_transformed.csv",
        mime="text/csv",
    )

    st.success("✅ Transformation complete!")
else:
    st.info("⬆️ Upload a CSV to begin.")

# ---------------------------------------------------------------------------------------
with st.sidebar.expander("ℹ️ About this app", expanded=False):
    st.markdown(
        """
        * Converts IG post captions into sentence‑level rows.
        * Strips emoji (optional) and ensures each sentence ends with punctuation.
        * Built with **Streamlit** – feel free to fork & extend! 🛠️
        """
    )

st.sidebar.markdown("---")
st.sidebar.caption("Made with ❤️ by Streamlit App Creator")
