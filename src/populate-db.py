# setup
import pandas as pd
import requests
from bs4 import BeautifulSoup
import psycopg2
from sqlalchemy import create_engine
import argparse

# arguments parsing
parser = argparse.ArgumentParser(description='Parse information to populate databases.')
parser.add_argument('--url', metavar='url', type=str, nargs='?',
                    help='url to fetch data')
parser.add_argument('--db', metavar='db name', type=str, nargs='?',
                    help='db name')
parser.add_argument('--table', metavar='table name', type=str, nargs='?',
                    help='table name')
args = parser.parse_args()


# functions to fetch, extract headlines and populate a SQL table


def fetch_france_info(url):
    """
    Fetch a web page from france info website (https://www.francetvinfo.fr/)

    Args:
        url: url of the web page to fetch

    Returns:
        page: html text processed with BeautifulSoup
    """
    # fetch a web page
    htlm_page = requests.get(url)

    page = BeautifulSoup(htlm_page.text, "html5lib")

    return page

def extract_head_news(web_page):
    """
    From france info website fetched web page (https://www.francetvinfo.fr/) extract headlines

    Args:
       web_page: fetched web page

    Returns:
        headlines: list of news heads
    """

    # extract title
    summaries = web_page.find_all('div', class_="flowItem")

    headlines = [x.select_one("h2").get_text() for x in summaries]

    return headlines

def write_in_db(headlines, db_name, table_name):
    """
    Insert headlines into the database

    Args:
       headlines: list of news heads
       db_name: database name to insert in
       table_name: table name in the database to insert in

    Returns:
        None
    """

    df = pd.DataFrame({"source": "franceinfo", "headline": headlines, "date": pd.to_datetime('today').to_pydatetime().date()})
    df = df.drop_duplicates(subset="headline", keep="first")
    print(df.head())
    alchemy_engine = create_engine('postgresql+psycopg2://antoinemertz@localhost/'+str(db_name), pool_recycle=3600)

    conn = alchemy_engine.connect()

    try:
        frame = df.to_sql(name=table_name, con=conn, if_exists='append', index=False)
    except Exception as ex:
        print(ex)

    conn.close()

    return None

if __name__ == '__main__':
    web_page = fetch_france_info(url=args.url)
    head_news = extract_head_news(web_page=web_page)
    write_in_db(headlines=head_news, db_name=args.db, table_name=args.table)
    print("OK")
