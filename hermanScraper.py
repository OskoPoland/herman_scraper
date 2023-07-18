#Python webscraper using selenium that will help me find a Herman Miller Mirras/Aeron chair for a steal by scraping new entries
#every 5hrs then formatting fitting entries into emails using
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from dotenv import load_dotenv

chromeDriverPath = "C:\\Users\\Vinr5\\OneDrive\\Documents\\Repositories\\pyscraper\\chromedriver"

#Obtain the current chromedriver version being used
options = webdriver.ChromeOptions().add_argument("--headless")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
link = "https://www.facebook.com/marketplace/105578279475150/search?minPrice=100&maxPrice=250&sortBy=price_ascend&query=%22herman%20miller%20aeron%22&exact=false"

#Get site information
wait = WebDriverWait(driver,10)
driver.get(link)
get_url = driver.current_url

#Wait until page is loaded using the link as the desired URL
wait.until(EC.url_to_be(link))
if (get_url == link):
    #extract the source HTML for the page
    print('at site')
    page_source = driver.page_source

#Parsing HTML
soup = BeautifulSoup(page_source, features="html.parser")
div_list_itemNames = soup.find_all('div', class_= "xyqdw3p x4uap5 xjkvuk6 xkhd6sd", limit=10)
div_list_itemPrices = soup.find_all('div', class_ = "x78zum5 x1q0g3np x1iorvi4 x4uap5 xjkvuk6 xkhd6sd", limit=10)

items = []
prices = []
flag_price = 150
flag = False

for div in div_list_itemNames:
    items.append(div.find('span', 'x193iq5w xeuugli x13faqbe x1vvkbs x1xmvt09 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x xudqn12 x3x7a5m x6prxxf xvq8zen xo1l8bm xzsf02u').text)

for div in div_list_itemPrices:
    price = div.find('span', 'x193iq5w xeuugli x13faqbe x1vvkbs x1xmvt09 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x xudqn12 x676frb x1lkfr7t x1lbecb7 x1s688f xzsf02u').text
    prices.append(price)
    if int(price[1:len(price)-1]) <= flag_price:
        flag = True
#Zip together into dictionary
scraped = dict(zip(items, prices))

#Creating and formatting the email
sender = "vinr567@gmail.com"
reciever = "vinr567@gmail.com"

#generate message container
msg_container = MIMEMultipart('alternative')
if flag:
    msg_container['Subject'] = "DISCOUNT PRESENT CHECK ASAP " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") 
else:
    msg_container['Subject'] = "Herman Scrape" + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
msg_container['From'] = os.getenv('email')
msg_container['To'] = os.getenv('reciever')

#Creating Body of Message
body_string = ""
for item in scraped.keys():
    body_string += "{price} {item} \n".format(price=scraped.get(item), item=item)

print(body_string)

#Create plain text and html of email
out_text ="Current Scrapes Obtained From {link} \n".format(link=link) + body_string 
out_html = """
<html>
    <head>
        <title>Current Scrapes Obtained From: {link}</title>
    </head>
    <body>
        {body_string}
    </body>
</html
""".format(link=link, body_string=body_string)

#Create MIME portions of text and html
p_text = MIMEText(out_text, 'plain')
p_html = MIMEText(out_html, 'html')

#Attach MIME parts to msg
msg_container.attach(p_text)
msg_container.attach(p_html)

#Send message using localhosted server
load_dotenv()
user = os.getenv('sender')
pcode = os.getenv('pass')
reciever = os.getenv('reciever')

print(user + ' ' + pcode)

s = smtplib.SMTP('smtp.gmail.com', 587)
s.starttls()
s.login(user,  pcode)
s.sendmail(sender, reciever, msg_container.as_string())
s.close()
driver.quit()
