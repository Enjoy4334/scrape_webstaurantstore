import time
import csv
from datetime import datetime

import requests
import fake_useragent
from bs4 import BeautifulSoup
from multiprocessing import Pool


HOST = 'https://www.webstaurantstore.com'

user = fake_useragent.UserAgent().random
headers = {
    'user-agent': user
}


def get_html(url):
    ''' Get the html page'''
    try:
        r = requests.get(url, headers=headers, timeout=5)
        if r.ok:  # status code 200
            return r
        else:
            print('Site access error:', r.status_code)
    except requests.exceptions.ReadTimeout:
        print("\n Reconnecting to servers \n")
        time.sleep(3)


def get_page_num(url):
    ''' Parsing attached pages '''
    html = get_html(url)
    soup = BeautifulSoup(html.text, 'html.parser')
    try:
        page = soup.find('div', attrs={'id': 'paging'})
        num = page.find_all('a', attrs={'class': True})[-2]
        for page in num:
            return int(page)

    except:
        return 1


def get_list_page_product(count_url):
    ''' Getting a list of product pages url '''
    html = get_html(count_url)
    soup = BeautifulSoup(html.text, 'html.parser')
    page = soup.find('div', attrs={'id': 'product_listing'})
    ad = page.find_all('div', attrs={'class': 'ag-item gtm-product'})

    link_list = []
    for i in ad:
        ads = i.find('a', attrs={'class': 'block'})
        url = HOST + ads.get('href')
        link_list.append(url)

    return link_list


def get_page_product_data(html, url):
    ''' Parsing attached pages product'''
    soup = BeautifulSoup(html.text, 'html.parser')
    try:
        title = soup.find('h1').get_text()
        basic_price = soup.find('p', attrs={'class': 'price'}).get_text(strip=True).split('/')[0]

        try:
            unit_price = soup.findl('td').get_text(strip=True)
        except:
            unit_price = ''

        try:
            ups_code = soup.find('span', attrs={'class': 'product__stat-desc'}).get_text(strip=True)
            if len(ups_code) < 10:
                ups_code = ''
        except:
            ups_code = ''

        print(f'[PRODUCT]', url, title, unit_price, basic_price, ups_code)

        data = {
            'url': url,
            'title': title,
            'unit_price': unit_price,
            'basic_price': basic_price,
            'ups_code': ups_code,
        }

        return data

    except:
        print('Something went wrong, take a look at the file: error.txt')
        with open('error.txt', 'a', encoding="utf-8") as file:
            file.write(f'{url} \n')


def write_csv(data):
    ''' Writing the result of the file in csv  '''
    with open('input_list_url_category.txt') as file:
        lines = file.read()
        name_category = lines.split('/')[-1].split('.')[0]

    with open(datetime.strftime(datetime.now(), f"{name_category}_%d-%m-%Y.csv"), 'a', newline='') as file:
        order = ['url', 'title', 'unit_price', 'basic_price', 'ups_code']
        writer = csv.DictWriter(file, delimiter=';', fieldnames=order)
        writer.writerow(data)


def make_all(url):
    ''' Multiprocessing functions '''
    html = get_html(url)
    data = get_page_product_data(html, url)
    write_csv(data)


def main():
    with open('input_list_url_category.txt') as file:
        lines = [line.strip() for line in file.readlines()]

        for url in lines:
            last_page = get_page_num(url)

            for count in range(1, 1 + last_page):
                count_url = f'{url}?page={count}'
                url_page = get_list_page_product(count_url)

                with Pool(4) as p:
                    p.map(make_all, url_page)


if __name__ == '__main__':
    main()