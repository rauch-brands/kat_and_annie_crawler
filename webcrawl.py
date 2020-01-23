# STANDARD LIBRARY MODULES
import re
import requests
import os, sys
import csv
import time

# BEAUTIFUL SOUP
from bs4 import BeautifulSoup, SoupStrainer

# SELENIUM
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

### https://medium.com/ymedialabs-innovation/web-scraping-using-beautiful-soup-and-selenium-for-dynamic-page-2f8ad15efe25

def pull_sku(page, soup):
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

def pull_title(page, soup):
    #title_list = soup.find(class_='span4')
    #print(title_list)
    for item in soup.find_all('h1'):
        title = item.string
        return(title)

# returns [list] of all links to follow on page
def generate_link_list(url):
    page = requests.get(url) #shop all
    soup = BeautifulSoup(page.text, 'html.parser')
    links = get_links(page, soup) # returns list [product links]
    return (links) # all product links for crawler to follow

def generate_link_URL(link):
    link = link.replace("/ba", "")
    return (link)

def generate_link_list_from_text(text_doc):
    soup = BeautifulSoup(text_doc, 'html.parser')
    link_list = []
    for link in soup.find_all('a', class_='product-title'):
        new_link = link.get('href')
        final_link = "https://www.katandannie.com" + new_link
        link_list.append(final_link)
    return (link_list)


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


def expand_more_button():
    url = "https://www.katandannie.com/ba"
    options = webdriver.ChromeOptions()
    options.add_argument("start-maximized")
    options.add_argument('disable-infobars')
    options.add_argument("window-size=550,500") # sets sie of pop up window

    # chrome borwser will pop up
    browser = webdriver.Chrome(chrome_options=options, executable_path=r'C:\webdrivers\chromedriver.exe')
    """
    BROWSER OPTIONS
        - firefox browse phantom will not pop up
        - browser = webdriver.PhantomJS(service_args=['--ignore-ssl-errors=true'])
    """
    browser.get(url)

    count = 1
    more_clicks = True
    while (more_clicks == True):
        try:
            elm = browser.find_element_by_class_name('btn-view-more')
            # progress bar
            page_text_count = "gathering page " + str(count)
            printProgressBar (count, 16, prefix = page_text_count, suffix = '', decimals = 1, length = 50, fill = '█', printEnd = "\r")
            time.sleep(3) # keep as sleep(3), anything < 3 creates too many click events
            elm.click()
            count += 1

        except:
            more_clicks = False
            break

    # returns <class 'str' >
    src = browser.page_source
    #print(type(src))

    #browser.quit()
    return (src)

# generates list x list
def generate_complete_list(links):
    #links = generate_link_list()
    PRODUCTS = [["sku", "title", "description", "price", "availability", "imageURL", "linkURL"]]
    current_place = 1
    total_products = len(links)
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
        printProgressBar (current_place, total_products, prefix = 'creating csv file', suffix = '', decimals = 1, length = 50, fill = '█', printEnd = "\r")
        current_place += 1

    return (PRODUCTS)

def write_csv(list):
    file = open('kaProductFeed.csv', 'w', newline='')
    with file:
        writer = csv.writer(file)
        writer.writerows(list)

def main():
    src = expand_more_button()
    link_list = generate_link_list_from_text(src)
    final_list = generate_complete_list(link_list) # returns [[products],[products]] - multidimentional list of products on website
    write_csv(final_list)

main()



### backups ###
'''
def expand_more_button2():
    ### infinate clicks

    url = "https://www.katandannie.com/ba"
    options = webdriver.ChromeOptions()
    options.add_argument("start-maximized")
    options.add_argument('disable-infobars')
    browser = webdriver.Chrome(chrome_options=options, executable_path=r'C:\webdrivers\chromedriver.exe')
    browser.get(url)

    count = 1

    while True:
        try:
            elm = browser.find_element_by_class_name('btn-view-more')

            time.sleep(2)
            print(str(count) + "click")
            count += 1



        except:
            print("No more Buttons")
            break
            browser.quit()


        if 'inactive' in elm.get_attribute('class'):
            print("nope")
            break;
        elm.click()

    browser.quit()
    return (0)

def expand_more_button():
    # enable pages
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--incognito')
    options.add_argument('--headless')
    driver = webdriver.Chrome("/webdrivers/chromedriver", chrome_options=options)

    # get product pages
    driver.get("https://www.katandannie.com/ba")
    more_buttons = driver.find_elements_by_class_name("btn btn-primary btn-view-more span12")
    while True:
        try:

        except NoSuchElementException:
            print("BREAK ##")
            break

    ## could be shorter
    for x in range(len(more_buttons)):
      if more_buttons[x].is_displayed():
          driver.execute_script("arguments[0].click();", more_buttons[x])
          print("button clicked")
          time.sleep(1)
    page_source = driver.page_source

    ## END
    driver.quit()
    ## end
    return()
def expand_page():
    url = "https://www.katandannie.com/ba"
    options = webdriver.ChromeOptions()
    options.add_argument("start-maximized")
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--incognito')
    options.add_argument('--headless')
    options.add_argument('disable-infobars')
    browser = webdriver.Chrome(options=options, executable_path=r'C:\webdrivers\chromedriver.exe')
    browser.get(url)
    while True:
        try:
            browser.find_element_by_link_text('View More').click()

            # Wait till the container of the products gets loaded
            # after load more is clicked.
            time.sleep(5)

            #recipe_container = browser.find_element_by_id("recipeListing")

            if 'No Record Found' in recipe_container.text:
                break

        except (NoSuchElementException, WebDriverException) as e:
            break

def expand_more_button4():
    url = "https://www.katandannie.com/ba"
    options = webdriver.ChromeOptions()
    options.add_argument("start-maximized")
    options.add_argument('disable-infobars')
    browser = webdriver.Chrome(options=options, executable_path=r'C:\webdrivers\chromedriver.exe')
    browser.get(url)
    while True:
        try:

            elm = browser.find_element_by_class_name('btn-view-more')
            time.sleep(5)
            elm.click()
            print(str(count) + "click")
            count += 1
            #name? :#ListingViewMore
            browser.execute_script("return arguments[0].scrollIntoView(true);", WebDriverWait(browser,20).until(EC.visibility_of_element_located((By.XPATH, "//button[@class='btn' and contains(.,'View More')]"))))
            browser.execute_script("arguments[0].click();", WebDriverWait(browser,20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "btn btn-primary btn-view-more span12[name='#ListingViewMore']"))))

            print("Button clicked")
        except:
            print("No more Buttons")
            break
    browser.quit()

def get_links(page, soup):
    link_list = []
    for link in soup.find_all('a', class_='product-title'):
        new_link = link.get('href')
        final_link = "https://www.katandannie.com" + new_link
        link_list.append(final_link)
    return (link_list)
'''
