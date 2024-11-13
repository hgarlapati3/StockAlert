import requests
from bs4 import BeautifulSoup
import schedule
import time
from twilio.rest import Client

from mailjet_rest import Client
import os
import json



def check_stock(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    parent_elem = soup.find('div', class_="product-form-input-block woocommerce-variation-add-to-cart variations_button")

    if parent_elem:
        stock_elem = parent_elem.find('p', class_='stock')
        if (stock_elem):
            if 'in-stock' in stock_elem['class']:
                return 'in-stock'
            else:
                return 'out-of-stock'
    return 'unknown'



def send_sms(to, name, body):

    with open('data.json', 'r') as f:
        data = json.load(f)
    

    mailjet = Client(auth=(data['api_key'], data['api_secret']), version='v3.1')

    payload = {
        'Messages': [
            {
            "From": {
                "Email": "harshikagarlapati05@gmail.com",
                "Name": "Matcha Notifier"
            },
            "To": [
                {
                "Email": to,
                "Name": name
                }
            ],
            "Subject": body[0],
            "TextPart": body[1],
            "HTMLPart": "<h3>" + body[1] + "</h3>" 
            }
        ]
    }
    result = mailjet.send.create(data=payload)
    print(result.status_code)
    print(result.json())
    




def main():
    with open('data.json', 'r') as f:
        data = json.load(f)

    global current_status
    url = "https://www.marukyu-koyamaen.co.jp/english/shop/products/1171020c1/?currency=USD"
    email_address = data['email_address']
    name = "your_name"

    new_status = check_stock(url)

    if (new_status != current_status):
        if (new_status == 'in-stock'):
            message = ["MATCHA is back in stock!", name + ", your Favorite MATCHA is back in stock!"]
        elif (new_status == 'out-of-stock'):
            message = ["OH NO! Matcha is out of stock :(", "Bad News " + name + ", your matcha is out of stock :("]
        else:
            message = 'Product status is unkown'
    
        send_sms(email_address, name, message)

    current_status = new_status

current_status = None
schedule.every(2).minutes.do(main)

while True:
    schedule.run_pending()
    time.sleep(1)
