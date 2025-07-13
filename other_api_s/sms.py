import requests
import urllib.parse


def send_sms(number, text):
    print("send_sms")
    text = urllib.parse.quote(text)
    url = "http://sms-special.gmobile.mn/cgi-bin/sendsms?username=enjoy&password=kids&from=555&to=" + str(
        number) + "&text=" + str(text)
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("GET", url, headers=headers)
    print(response.content)
    return response.content
