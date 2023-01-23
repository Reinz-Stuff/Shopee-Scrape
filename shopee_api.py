import locale
import time

import pandas as pd
from seleniumwire import webdriver  # Import from seleniumwire
from seleniumwire.utils import decode
import json

# Create a new instance of the Chrome driver
driver = webdriver.Chrome()

# Go to the Google home page
url = 'https://shopee.co.id/search?keyword=laptop'

driver.get(url)
driver.maximize_window()

# Scroll down
bottom = False
a = 0
while not bottom:
    new_height = driver.execute_script("return document.body.scrollHeight")
    driver.execute_script(f"window.scrollTo(0, {a});")
    if a > new_height:
        bottom = True
    a += 5

# Access requests via the `requests` attribute
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
                price        = int(json_data['items'][i]['item_basic']['price'])
                price        = locale.format_string("%d", (price/100000), grouping=True)
                rating       = json_data['items'][i]['item_basic']['item_rating']['rating_star']
                rating       = round(rating, 1)
                sold         = json_data['items'][i]['item_basic']['historical_sold']
                location     = json_data['items'][i]['item_basic']['shop_location']

                data_dict = {
                    'Product': product_name,
                    'Price(Rp)': price,
                    'Rating': rating,
                    'Total sold': sold,
                    'Location': location,
                }
                data.append(data_dict)

            df = pd.DataFrame(data)
            df.to_excel('result.xlsx', index=False)