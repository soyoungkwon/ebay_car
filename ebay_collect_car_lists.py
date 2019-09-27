# ebay-kleinanzeiger website scrap,
# get used-car info--> save it as pandas structure

# Car model extraction + simplification
# functions: main-pd-multi-pages, car-list&link-by-page, clean-pd
# extract title name (car model + alpha), website, price,
# To extract car model, load the car model info.
# Check whether model name is in the title, if exists, simplify the model name
# Then, to extract info ( miles), color from title or content
# if color info is not written, use cv2 to extract color information from the jpeg file

# Change categorical info to OneHotEncoder

# Apply Linear Regression

# This gets a user defined price prediction

# To see whether it is sold,

# load libraries
import pandas as pd
from bs4 import BeautifulSoup
import requests
import os
import collections
from sklearn.preprocessing import LabelEncoder, OneHotEncoder

path_curr = os.getcwd()
url = 'https://www.ebay-kleinanzeigen.de/s-auto-rad-boot/berlin/'
max_pages = 10
# page = 1

def main(url, max_pages):
    for page in range(max_pages):
        main_carlist_by_page(page)

# main function
def main_carlist_by_page(page):

    # create weblinks, eventlists as LIST
    weblinks, carlists, pricelists, postlists = trade_spider(url, page)

    # change into pandas
    car_data = {'Model': carlists}
    car_pd = pd.DataFrame(car_data)
    car_pd.insert(1, 'Link', weblinks)
    car_pd.insert(2, 'Price', pricelists)
    car_pd.insert(3, 'Post', postlists)

    # add name & number
    namelists, numberlists = extract_car(weblinks)
    car_pd.insert(4, 'Name', namelists)
    car_pd.insert(5, 'Number', numberlists)
    car_pd = car_info_clean(car_pd)
    car_pd.to_csv(path_curr + '/car_by_page' + str(page+1).zfill(2) +'.csv', encoding = 'utf-8', index=False)

    return car_pd

# collect car websites for each page
def trade_spider(url, page):
    weblist = []
    carlist = []
    pricelist = []
    timelist = []

    # extract html sources
    full_url = url + 'seite:'+ str(page+1) + '/auto-vw/k0l3331'
    source_code = requests.get(full_url)
    plain_text = source_code.text
    soup = BeautifulSoup(plain_text, "html.parser")
    # extract link & car_soup
    big_carsoup = soup.findAll('article', {'class': 'aditem'})
    carsoup = soup.findAll('a', {'class': 'ellipsis'})

    # href_link, car_name extract
    for link in range(len(carsoup)-1):
        # links extract
        href_unicode = carsoup[link].get('href')
        href = href_unicode.encode('ascii', 'ignore')
        weblist.append(href)

        # car_name extract
        car_unicode = carsoup[link].text
        car_name_orig = car_unicode.encode('ascii','ignore')# remove ascii coding
        carlist.append(car_name_orig)

        # car price
        cardiv = big_carsoup[link].findAll('div', {'class':'aditem-details'})
        carstrong = cardiv[0].findAll('strong')
        car_price = carstrong[0].text
        pricelist.append(car_price)

        # time stamps
        timesoup = big_carsoup[link].findAll('div', {'class', 'aditem-addon'})
        post_time = timesoup[0].text
        timelist.append(post_time)

    # print(eventlist)
    return weblist, carlist, pricelist, timelist

def extract_car(weblinks):
    price_list = []
    name_list = []
    number_list = []
    n_car = len(weblinks)
    for car in range(n_car):
        url_eachcar = 'https://www.ebay-kleinanzeigen.de/' + weblinks[car]
        webhtml = requests.get(url_eachcar)
        soup = BeautifulSoup(webhtml.content, 'lxml')#html.parser')

        # price
        price_obj = soup.find('h2', {'class': 'articleheader--price'})
        price_text = price_obj.text
        # name
        name_obj = soup.find('span', {'class':'text-bold text-bigger text-force-linebreak'})
        name_text = name_obj.text
        # number
        number_obj = soup.find('span', {"id": "viewad-contact-phone"})
        if isinstance(number_obj, type(None)):
            number_text = 'NaN'
        else:
            number_text = number_obj.text

        name_list.append(name_text)
        number_list.append(number_text)

    return name_list, number_list

def car_info_clean(car_pd):
    car_pd['Model'] = car_pd['Model'].str.replace('\n', '')
    car_pd['Post'] = car_pd['Post'].str.replace('\n', '')
    car_pd['Name'] = car_pd['Name'].str.replace('\n', '')
    return car_pd
