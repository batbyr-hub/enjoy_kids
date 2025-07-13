import requests
import json
from datetime import datetime, timedelta


basic_url = "https://charge.gmobile.mn/api/"
username = "enjoyKids_batbayr_local"
password = "KDj&9@kdf^&78/LKDj88"


def checkLogin():
    print("checkLogin")
    url = basic_url + "login_check"
    headers = {
        'Content-Type': 'application/json'
    }

    data = {
        "username": username,
        "password": password
    }
    result = requests.post(url, data=json.dumps(data), headers=headers)
    result = json.loads(result.content)

    dt = datetime.strptime(str(datetime.now()), '%Y-%m-%d %H:%M:%S.%f')
    expired = dt + timedelta(minutes=50)  # JWT expired 1 tsag uchir jwt avsan tsag deeree 50min nemj  bna.
    return result

def numberCheck(number):
    print("numberCheck")
    # serviceName = access.access_name
    check_login = checkLogin()
    token = check_login["token"]

    url = basic_url + "number/check"

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer {0}'.format(token)
    }

    data = {
        # "serviceName": serviceName,
        "number": number
    }

    result = requests.post(url, data=json.dumps(data), headers=headers)
    result = json.loads(result.content)
    return result

def memberNumber_check(number, tipo):
    print("memberNumber_check")
    # serviceName = access.access_name
    check_login = checkLogin()
    token = check_login["token"]

    url = basic_url + "memberNumber/check"

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer {0}'.format(token)
    }

    data = {
        "number": number,
        "type": tipo
    }

    result = requests.post(url, data=json.dumps(data), headers=headers)
    result = json.loads(result.content)
    return result

def member_check_balance(number, tipo):
    print("check_balance")
    # serviceName = access.access_name
    check_login = checkLogin()
    token = check_login["token"]

    url = basic_url + "memberNumber/check"

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer {0}'.format(token)
    }

    data = {
        "number": number,
        "type": tipo
    }

    result = requests.post(url, data=json.dumps(data), headers=headers)
    result = json.loads(result.content)
    return result

def charge(number, order_id, cardType, amount):  # unit bol 0, cash bol 1
    print("charge_number")
    # print(order_id)
    # order = Order.objects.get(transaction_id=order_id)
    # access = ChargeAccess.objects.get(ip_address=ip_address, channel_id=order.channel_id)
    # serviceName = access.access_name
    # if access.expired_at is not None:
    #     if access.expired_at.astimezone(pytz.timezone('Asia/Ulaanbaatar')).strftime(
    #             '%Y-%m-%d %H:%M:%S') < datetime.now().strftime('%Y-%m-%d %H:%M:%S'):
    #         check_login = self.new_service.checkLogin(order.channel_id)
    #         token = check_login["token"]
    #     else:
    #         token = access.token
    # else:
    #     check_login = self.new_service.checkLogin(order.channel_id)
    #     token = check_login["token"]

    check_login = checkLogin()
    token = check_login["token"]

    # if ppd == "unit" or ppd == "gov":
    #     ppd = "prepaid" + "/charge"
    # elif ppd == "data" or ppd == "smart_package":
    #     ppd = "priceplan" + "/charge"
    # elif ppd == "nemelt_data":
    #     ppd = "unlimited/add/data"
    # elif ppd == "post":
    #     ppd = "postpaid" + "/charge"
    url = basic_url + "priceplan/charge"

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer {0}'.format(token)
    }
    data = {
        "chargeNumber": number,
        "serviceName": "enjoy_kids",
        "partyCode": "28485",
        "transactionId": order_id,
        "cardType": cardType,
        "amount": amount,
        "channel": "1"
    }
    print("data")
    print(data)
    result = requests.post(url=url, data=json.dumps(data), headers=headers)
    # print(result)
    print(json.loads(result.content))
    return result
