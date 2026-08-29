import pandas as pd

from categorizer import categorize_transaction

def load_and_categorize_statement(file_path):
    df = pd.read_csv(file_path)

    required_columns = {"date", "description", "amount", "type"}
    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            "Missing required columns: "
            + ", ".join(sorted(missing_columns))
        )

    df["description"] = df["description"].fillna("").astype(str)
    df["type"] = df["type"].fillna("").astype(str).str.upper()
    df["amount"] = pd.to_numeric(df["amount"], errors="raise")

    categories = df["description"].apply(categorize_transaction)

    df["category"] = categories.apply(lambda x: x["category"])
    df["confidence"] = categories.apply(lambda x: x["confidence"])

    return df


if __name__ == "__main__":
    statement = load_and_categorize_statement("data/sample_statement.csv")
    print(statement)