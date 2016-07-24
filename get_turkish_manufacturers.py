#!/usr/bin/env ipython
import requests
from bs4 import BeautifulSoup

url_pref = 'http://www.turkish-manufacturers.com'

def get_num_pages(request):
    try:
        num_pages = int(BeautifulSoup(request.text, 'lxml').
            find('div', class_='pages_nav').
            findChildren()[-2].
            text)
    except AttributeError:
        num_pages = 1
    return num_pages


def get_sublinks(links):
    urls = []
    names = []
    for link in links:
        urls.append(url_pref + link.attrs['href'])
        names.append(link.text)
    return urls, names

def get_categories(url_field):
    r_field = requests.get(url_field)
    soup_categories = BeautifulSoup(r_field.text, 'lxml')

    links_categories = soup_categories.find(class_='kategs').findChildren('a')
    url_categories, name_categories = get_sublinks(links_categories)
    return url_categories, name_categories


def get_products(url_category, seen_products):
    r_category = requests.get(url_category)
    res_url_prd = []
    res_name_prd = []
    num_pages = get_num_pages(r_category)
    print('page numbers of products: ', num_pages)

    for num_page in range(1, num_pages + 1):
        soup_prd = BeautifulSoup(r_category.text, 'lxml')
        url_next = '{}_pg-{}.html'.format(url_category[:-5], num_page+1)

        try:
            links_prd = soup_prd.find(class_='prds').findChildren('a')

            urls_prd, names_prd = get_sublinks(links_prd)
            res_url_prd.extend(urls_prd)
            res_name_prd.extend(names_prd)

        except AttributeError as e:
            # print('Product:', e)
            # print(r_category.url)
            pass

        r_category = requests.get(url_next)

    res_url_prd_fin = []
    res_name_prd_fin = []
    if res_url_prd:
        for (url_prd, name_prd) in zip(res_url_prd, res_name_prd):
            if name_prd not in seen_products:
                # print(name_prd)
                res_url_prd_fin.append(url_prd)
                res_name_prd_fin.append(name_prd)
        seen_products.update(name_prd)

    return res_url_prd_fin, res_name_prd_fin, seen_products

# should considered with seen_firms for acceleration
# def get_firms(url_product, seen_firms):
def get_firms(url_product):
    r_product = requests.get(url_product)
    firms_final = []
    num_pages = get_num_pages(r_product)

    product_name_url = url_product.split('/')[-1].split('-turkey')[0]

    try:
        product_name = BeautifulSoup(r_product.text, 'lxml').find(class_='page-title').text.strip()
    except AttributeError as e:
        product_name = product_name_url.title().replace('-', ' ')
        # print('Product Name:', e)
        # print(r_product.url)

    # print('page numbers of firms: ', num_pages)

    for num_page in range(1, num_pages+1):
        soup_firms = BeautifulSoup(r_product.text, 'lxml')
        url_next = '{}/turkey/{}_page-{}.html'.format(url_pref, product_name_url , num_page+1)
        try:
            firms_list = soup_firms.find('ul', class_='firms').findChildren('div', class_='r-c') 
            for firm in firms_list:
                # print(firm)
                firm_name = firm.findChild('div', class_='title').text
                
                # if firm_name in seen_firms:
                #     continue
                # else:
                #     seen_firms.add(firm_name)

                firm_link = url_pref + firm.findChild('a', class_='firma-link').attrs['href']
                firm_address = firm.find('div', class_='address').text
                firm_keys = firm.find('div', class_='keys').text
                firms_final.append([firm_name, firm_link, firm_address, 
                    firm_keys, product_name, r_product.url])

        # sometimes pages are missed
        except AttributeError as e:
            # print('exception:', e)
            # print('product:', product_name)
            # print('page_number:', num_page)
            # print('firm_name:', firm_name)
            # print('url_next:', url_next)
            pass
        r_product = requests.get(url_next)

    return firms_final


def get_firm_pages(url_product):
    r_product = requests.get(url_product)
    firm_pages = [url_product]
    num_pages = get_num_pages(r_product)

    product_name_url = url_product.split('/')[-1].split('-turkey')[0]
    print('page numbers of firms: ', num_pages)

    for num_page in range(1, num_pages):
        url_next = '{}/turkey/{}_page-{}.html'.format(url_pref, product_name_url , num_page+1)
        firm_pages.append(url_next)

    return firm_pages


def get_firms_uniq(url_firm_page, seen_firms):
    try:
        r_firm_page = requests.get(url_firm_page)
    except (TypeError, TimeoutError) as e: 
        print(e)
        print(url_firm_page)
        r_firm_page = requests.get(url_firm_page)

    firms_final = []

    soup_firms = BeautifulSoup(r_firm_page.text, 'lxml')
    try:
        firms_list = soup_firms.find('ul', class_='firms').findChildren('div', class_='r-c') 
        for firm in firms_list:
            firm_name = firm.findChild('div', class_='title').text
            
            if firm_name in seen_firms:
                continue
            else:
                seen_firms.update([firm_name])

            firm_link = url_pref + firm.findChild('a', class_='firma-link').attrs['href']
            firm_address = firm.find('div', class_='address').text
            firm_keys = firm.find('div', class_='keys').text
            firms_final.append([firm_name, firm_link, firm_address, 
                firm_keys, r_firm_page.url])

    # sometimes pages are missed
    except AttributeError as e:
        # print('exception:', e)
        # print('product:', product_name)
        # print('page_number:', num_page)
        # print('firm_name:', firm_name)
        # print('url_next:', url_next)
        pass
    return firms_final
