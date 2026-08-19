import pandas as pd

from categorizer import categorize_transaction


def load_and_categorize_statement(file_path: str) -> pd.DataFrame:
    """Load a CSV bank statement and categorize each transaction."""

    df = pd.read_csv(file_path)

    categories = df["description"].apply(categorize_transaction)

    df["category"] = categories.apply(lambda x: x["category"])
    df["confidence"] = categories.apply(lambda x: x["confidence"])

    return df


if __name__ == "__main__":
    statement = load_and_categorize_statement("data/sample_statement.csv")
    print(statement)