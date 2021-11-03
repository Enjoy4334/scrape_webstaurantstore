from bs4 import BeautifulSoup
import requests
import fake_useragent
import time
import csv

HOST = 'https://www.webstaurantstore.com'

user = fake_useragent.UserAgent().random
headers = {
    'user-agent': user
}


def get_html(url):
    r = requests.get(url, headers=headers, timeout=5)
    if r.ok:  # 200
        return r
    else:
        print('Ошибка доступа к сайту, советую проверить VPN:', r.status_code)


def get_list_page(html):
    soup = BeautifulSoup(html.text, 'html.parser')
    ads = soup.find_all('a', attrs={'class': 'block font-semibold text-sm-1/2 leading-none mb-3 first:mt-8 max-h-10 hover:max-h-full min-h-10 overflow-hidden hover:overflow-visible md:mb-3 mt-0 md:mt-1-1/2'})

    link_list = []
    for i in ads:
        url = HOST + i.get('href')
        link_list.append(url)

    return link_list


def get_page_num(html):
    soup = BeautifulSoup(html.text, 'html.parser')
    page = soup.find('div', attrs={'id': 'paging'})
    num = page.find_all('a', attrs={'class': True})[-2]
    for page in num:
        return int(page)


def write_csv(data):
    with open('webstaurantstore.csv', 'a', newline='') as f:
        order = ['url', 'title', 'unit_price', 'basic_price', 'ups_code', 'mfr']
        writer = csv.DictWriter(f, delimiter=';', fieldnames=order)
        writer.writerow(data)


def get_category_page(html, url):
    soup = BeautifulSoup(html.text, 'html.parser')
    title = soup.find('h1').get_text()
    basic_price = soup.find('p', attrs={'class': 'price'}).get_text(strip=True).split('/')[0]
    try:
        mfr = soup.find('span', attrs={'class': 'mfr-number suffix_meta'}).get_text(strip=True).split(':')[1]
    except:
        mfr = ''

    try:
        unit_price = soup.findl('td').get_text(strip=True)
    except:
        unit_price = ''
    try:
        ups_code = soup.find('span', attrs={'class': 'product__stat-desc'}).get_text(strip=True)
    except:
        ups_code = ''

    print(url, title, unit_price, basic_price, ups_code, mfr)

    data = {
        'url': url,
        'title': title,
        'unit_price': unit_price,
        'basic_price': basic_price,
        'ups_code': ups_code,
        'mfr': mfr
    }
    write_csv(data)


def main():
    with open('input_list_words.txt') as file:
        lines = [line.strip() for line in file.readlines()]

        for line in lines:
            url_num = f"https://www.webstaurantstore.com/search/{line}"
            html = get_html(url_num)
            last_page = get_page_num(html)
            for i in range(1, 1 + last_page):
                url = f"https://www.webstaurantstore.com/search/{line}.html?page={i}"
                print(f'[INFO] Парсим {line} /Cтраницу {i}')
                html = get_html(url)
                page = get_list_page(html)
                for url in page:
                    html = get_html(url)
                    time.sleep(1)
                    page = get_category_page(html, url)


if __name__ == '__main__':
    main()

