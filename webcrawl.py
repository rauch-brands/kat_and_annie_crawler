import re
import requests
from bs4 import BeautifulSoup, SoupStrainer
import os, sys
import csv
import time


def get_links(page, soup):
    link_list = []
    for link in soup.find_all('a', class_='product-title'):
        new_link = link.get('href')
        final_link = "https://www.katandannie.com" + new_link
        link_list.append(final_link)
    return (link_list)

'''
def get_img_links(page, soup):
    img_list = []
    for link in soup.find_all('img'):
        print(link.get('src'))

    return 0
'''

def pull_sku(page, soup):
    #product-details-code
    # Pull all text from the section-body-container div
    sku_list = soup.find(class_='product-details-code') #generates list
    for sku in sku_list:
        sku = sku[13:]
        return(sku)

def pull_description(page, soup):
    description_list = soup.find(class_='product-details-desc')
    description_list = description_list.text
    description = description_list.replace("\n", " ")
    return(description)

def pull_price(page, soup):
    price_list = soup.find(class_='price price-current')
    for price in price_list:
        price = price[1:]
        return (price)

def pull_availability(page, soup):
    availability_list = soup.find(class_='text-right')
    availability_ = str(availability_list)
    availability_ = availability_.split('> ')
    availability_ = availability_[1]
    availability_ = availability_.split('<')
    availability = availability_[0]
    availability = availability.replace("In stock", "TRUE")
    availability = availability.replace("Out of stock", "FALSE")
    availability = availability.replace("Discontinued", "NULL")
    return (availability)

def pull_imageURL(page, soup):
    images_null = []
    for link in soup.find_all('img'):
        images_null.append(link.get('src'))

    imageURL_ = images_null[-1]
    imageURL = 'https://www.katandannie.com' + imageURL_
    return (imageURL)

    '''
    #image_list = soup.find(class_='ejs-slider-thumb active')
    #imageURL_ = image_list.get('src')
    #for link in soup.find_all('div', class_='product-image-rightcol'):
    #    new_link = link.get('href')
    image_list = str(image_list)
    print("2"+image_list)
    image_list = image_list.split('data')
    print("3"+image_list)
    image_list = image_list[2]
    image_list = image_list.split('"')
    imageURL_ = image_list[1]
    '''

def pull_title(page, soup):
    #title_list = soup.find(class_='span4')
    #print(title_list)
    for item in soup.find_all('h1'):
        title = item.string
        return(title)

def generate_link_list():
    page = requests.get('https://www.katandannie.com/ba') #shop all
    soup = BeautifulSoup(page.text, 'html.parser')
    links = get_links(page, soup) # returns list [product links]

    return (links) # all product links for crawler to follow

def generate_link_URL(link):
    link = link.replace("/ba", "")
    return (link)


# Print iterations progress
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = printEnd)
    # Print New Line on Complete
    if iteration == total:
        print()

# generates list x list
def generate_complete_list(links):
    #links = generate_link_list()
    PRODUCTS = [["sku", "title", "description", "price", "availability", "imageURL", "linkURL"]]
    current_place = 1
    total_products = len(links)
    #print(total_products)
    for link in links:
        page = requests.get(link)
        # Create a BeautifulSoup object
        soup = BeautifulSoup(page.text, 'html.parser')
        product_line = []

        # SKU
        sku = pull_sku(page, soup)
        product_line.append(sku)
        #print(sku)

        # TITLE
        title = pull_title(page, soup)
        product_line.append(title)
        #print(title)

        # DESCRIPTION
        description = pull_description(page, soup)
        product_line.append(description)
        #print(description)

        # PRICE
        price = pull_price(page, soup)
        product_line.append(price)
        #print(price)

        # AVAILABILITY
        availability = pull_availability(page, soup)
        product_line.append(availability)
        #print(availability)

        # IMAGE URL
        imageURL = pull_imageURL(page, soup)
        product_line.append(imageURL)
        #print(imageURL)

        # LINK URL
        link_url = generate_link_URL(link)
        product_line.append(link_url)
        #print(link)

        PRODUCTS.append(product_line)
        product_line = []
        printProgressBar (current_place, total_products, prefix = '', suffix = '', decimals = 1, length = 50, fill = '█', printEnd = "\r")
        current_place += 1

    return (PRODUCTS)

def write_csv(list):
    file = open('kaProductFeed.csv', 'w', newline='')
    with file:
        writer = csv.writer(file)
        writer.writerows(list)

def main():
    link_list = generate_link_list() # returns list of all links to follow
    final_list = generate_complete_list(link_list) # returns [[products],[products]] - multidimentional list of products on website
    write_csv(final_list)

main()
