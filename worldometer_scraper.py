import requests
import re
from bs4 import BeautifulSoup
import pandas as pd
import os

def worldometer_scraper(url=''):
    """
    Scrapes "Total Cases" and "Total Deaths" graphs on worldometer.
    Arguments:
    url -- defaults to the main page which has worldwide totals
    """
    base_url = 'https://www.worldometers.info/coronavirus/'
    page = requests.get(base_url + url)
    page = BeautifulSoup(page.text, 'html.parser')

    dates_pattern = 'categories: (.*?)]'
    data_pattern = 'data: (.*?)]'

    case_dates,death_dates = None,None
    #extract data from the U.S graphs on worldometer
    for script in page.find_all('script'):
        text = script.text
        if text.find('Total Cases') + 1:
            case_dates = re.findall(dates_pattern,text)
            cases = re.findall(data_pattern,text)
        if text.find('Total Deaths') + 1:
            death_dates = re.findall(dates_pattern,text)
            deaths = re.findall(data_pattern,text)

    if death_dates:
        death_dates = death_dates[0][1:].replace('"','').split(",")
        deaths = [int(death) for death in deaths[0][1:].replace('"','').split(",")]
        death_df = pd.DataFrame(zip(death_dates,deaths),columns=['date','total deaths'])
    else:
        death_df = pd.DataFrame(columns=['date','total deaths'])

    if case_dates:
        case_dates = case_dates[0][1:].replace('"','').split(",")
        cases = [int(case) for case in cases[0][1:].replace('"','').split(",")]
        case_df = pd.DataFrame(zip(case_dates,cases),columns=['date','total cases'])
    else:
        case_df = pd.DataFrame(columns=['date','total cases'])


    df = pd.merge(case_df,death_df,on='date',how='outer')
    return df


def get_urls():
    """
    Returns Worldometer urls for every available country
    """
    urls = []
    worldometer_page = requests.get("https://www.worldometers.info/coronavirus/")
    worldometer_page = BeautifulSoup(worldometer_page.text, 'html.parser')
    for row in worldometer_page.find_all("tr"):
        for link in row.find_all('a'):
            urls.append(link.get('href'))
    return urls


if __name__ == '__main__':

    if not 'worldometer_data' in os.listdir():
        os.mkdir('worldometer_data')

    urls = get_urls()
    for url in urls:
        df = worldometer_scraper(url)
        file_name = '{}.csv'.format(url.split('/')[1])
        path = os.path.join('worldometer_data',file_name)
        df.to_csv(path)
