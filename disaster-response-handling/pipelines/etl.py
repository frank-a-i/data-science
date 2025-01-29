import os 
import argparse
import pandas as pd

from sqlalchemy.engine import create_engine

def getRawData(messagesPath: str, categoriesPath: str) -> pd.DataFrame:
    """ Fetch raw data to work on

    Args:
        messagesPath (str, optional): path to the messages file
        categoriesPath (str, optional): path to the categories file

    Returns:
        pd.DataFrame: the processable data frame
    """
    messages = pd.read_csv(messagesPath)
    categories = pd.read_csv(categoriesPath)
    return pd.merge(messages, categories, on="id")


def makeIndividualColumns(categories):
    """ Turn category string into individual columns in the frame

    The indicator, which category is related to the message comes in an unpleasant shape; which whill be broken up here 

    Args:
        categories: the raw unprocessable ground truth

    Returns:
        the polished categories
    """
    row = [categories.get(col)[0] for col in range(categories.columns[-1] + 1)]
    category_colnames = [col.split("-")[0] for col in row]
    categories.columns = category_colnames
    for column in categories:
        categories[column] = [float(col.split("-")[1]) for col in categories[column]]

    return categories


def cleanDataFrame(cleaned_categories: pd.DataFrame) -> pd.DataFrame:
    """ Replace flaky categories and remove duplicates

    Args:
        cleaned_categories (pd.DataFrame): the content that will replace the flaky categories

    Returns:
        pd.DataFrame: the processable dataset
    """
    df_wo_flaky_categories = df.drop("categories", axis=1)
    df_w_good_categories = df_wo_flaky_categories.join(cleaned_categories)
    for category in cleaned_categories.columns:
        df_w_good_categories.drop(df_w_good_categories[df_w_good_categories[category] > 1].index, inplace=True)

    df_nodup = df_w_good_categories.drop_duplicates()
    return df_nodup


def exportData(
    df: pd.DataFrame, 
    sqlitePath: str = f'sqlite:///{os.path.join(os.path.dirname(os.path.realpath(__file__)),  "..", "ressources", "disaster_response_data.db")}',
    tableName: str = "Dataset"):
    """ Store dataset persistently

    Args:
        df (pd.DataFrame): the dataframe to be stored
        sqlitePath (_type_, optional): the target storage path
        tableName (str, optional): table name of the dataset to be generated
    """

    engine = create_engine(sqlitePath)
    df.to_sql(tableName, engine, index=False, if_exists='replace')
    print(f"Successfully exported database to '{sqlitePath}' under '{tableName}'")


def userHandling() -> argparse.Namespace:
    """ Let user define the path to the two necessary datasets

    Returns:
        argparse.Namespace: existing file path to both datasets
    """
    parser = argparse.ArgumentParser(description="Composes the data basis for disaster category estimation")
    parser.add_argument("-m", "--message-dataset", help="Path to 'messages' dataset", default=os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "ressources", "messages.csv"))
    parser.add_argument("-c", "--categories-dataset", help="Path to 'categories' dataset", default=os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "ressources",  "categories.csv"))

    args = parser.parse_args()
    assert os.path.isfile(args.message_dataset), f"Could not find file under '{args.message_dataset}'"
    assert os.path.isfile(args.categories_dataset), f"Could not find file under '{args.categories_dataset}'"

    return args


if __name__ == "__main__":
    datasetPaths = userHandling()
    df = getRawData(datasetPaths.message_dataset, datasetPaths.categories_dataset)
    categories = df.get("categories").str.split(";", expand=True)
    cleaned_categories = makeIndividualColumns(categories)
    dataset = cleanDataFrame(cleaned_categories)
    exportData(dataset)