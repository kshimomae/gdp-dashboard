import pandas as pd

# 1 Load data ─ change the path if your file lives elsewhere
df = pd.read_csv("sample_data.csv")     # “Statement” column is the text to scan

# 2 Dictionaries of trigger phrases  (feel free to extend)
dictionaries = {
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

# 3 Classifier
def classify(statement: str):
    """Return a list of tactic labels matched in the text (empty list ⇒ no match)."""
    if not isinstance(statement, str):
        return []
    text = statement.lower()
    hits = [cat for cat, terms in dictionaries.items() if any(t in text for t in terms)]
    return hits

df["tactics"] = df["Statement"].apply(classify)

# 4 Save / inspect
df.to_csv("classified_data.csv", index=False)
df.head()        # optional – shows the new 'tactics' column in the notebook
