import locale
import time

import pandas as pd
from seleniumwire import webdriver
from seleniumwire.utils import decode
import json


def scrape_data(page, keyword):
    driver = webdriver.Chrome()
    url = f'https://shopee.co.id/search?keyword={keyword}&page={page}'
    driver.get(url)
    driver.maximize_window()

    time.sleep(2)

    bottom = False
    a = 0
    while not bottom:
        new_height = driver.execute_script("return document.body.scrollHeight")
        driver.execute_script(f"window.scrollTo(0, {a});")
        if a > new_height:
            bottom = True
        a += 15

    for request in driver.requests:
        if request.response:
            if request.url.startswith('https://shopee.co.id/api/v4/search/search_items?by=relevancy&keyword='):
                response = request.response
                body = decode(response.body, response.headers.get('Content-Encoding', 'Identity'))
                decoded_body = body.decode('utf-8')
                json_data = json.loads(decoded_body)
                locale.setlocale(locale.LC_ALL, 'id_ID.UTF-8')
                data = []

                for i in range(0, len(json_data['items'])):
                    product_name = json_data['items'][i]['item_basic']['name']
                    price = int(json_data['items'][i]['item_basic']['price'])
                    price = locale.format_string("%d", (price / 100000), grouping=True)
                    rating = json_data['items'][i]['item_basic']['item_rating']['rating_star']
                    rating = round(rating, 1)
                    sold = json_data['items'][i]['item_basic']['historical_sold']
                    location = json_data['items'][i]['item_basic']['shop_location']

                    data_dict = {
                        'Product': product_name,
                        'Price(Rp)': price,
                        'Rating': rating,
                        'Total sold': sold,
                        'Location': location,
                    }
                    data.append(data_dict)

                return data


def extract_data(data):
    df = pd.DataFrame(data)

    return df


def run():
    search = input('Product search keyword: ')

    datas = []
    for i in range(0, 60):
        print(f'scraping page...{i+1}')
        scraping = scrape_data(i, search)
        datas.extend(scraping)
        time.sleep(1)

    print('writing file...')
    extarction = extract_data(datas)
    extarction.to_excel('result.xlsx', index=False)
    print('Finished!')


if __name__ == '__main__':
    run()
