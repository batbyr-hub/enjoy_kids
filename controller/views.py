import threading
import time
from controller.models import *
import datetime
from other_api_s.charge_between import numberCheck, charge
import json


# Create your views here.
def automat_charge(n=46800):
    # 46800 sec buyu 13 tsag
    while True:
        time.sleep(n)

        # start_date = datetime.date(2005, 1, 1)
        # end_date = datetime.date(2005, 3, 31)
        # kids_number = EnjoyKidsNumbers.objects.get(status="registered", created_at__range=(start_date, end_date))
        kids_number = EnjoyKidsNumbers.objects.filter(status="registered", created_at__range=datetime.date.today())
        for i in range(len(kids_number)):
            end_date = datetime.datetime.strptime(kids_number[i].exp_date, '%d-%b-%y')
            now_date = datetime.datetime.timestamp(datetime.datetime.now())
            exp = datetime.datetime.timestamp(end_date)
            if exp < now_date:
                # hereglegchiin negjnii uldegdel shalgana
                res_member_number = numberCheck(kids_number[i].member_number)
                print("res_member_number")
                print(res_member_number)
                if res_member_number["state"] == "Successful":
                    member_balance = res_member_number["balance"]
                    if int(member_balance) >= int(kids_number[i].package):
                        package = Package.objects.get(name=kids_number[i].package)
                        order = Order.objects.create(head_number=kids_number[i].head_number,
                                                     member_number=kids_number[i].member_number,
                                                     amount=package.price,
                                                     type="automat",
                                                     status="not-charged")
                        res_charge = charge(kids_number[i].member_number, order.pk,
                                            package.card_type,
                                            package.price)
                        if res_charge.status_code == 200:
                            res_charge = json.loads(res_charge.content)
                            print("res_charge")
                            print(res_charge)
                            if "scard" in res_charge:
                                order.scard = res_charge["scard"]
                                order.save()
                            if res_charge["state"] == "Successful":
                                kids_number[i].status = "charged"
                                order.status = "charged"
                                order.charged_date = datetime.datetime.now().strftime(
                                    '%Y-%m-%d %H:%M:%S')
                                order.shivelt = "1"
                                order.save()
                            else:
                                order.status = "charge-error"
                                order.save()
                                kids_number[i].status = "charge-error"
                        else:
                            order.status = "charge-error"
                            order.save()
                            kids_number[i].status = "charge-error"
                    else:
                        res_head_number = numberCheck(kids_number[i].head_number)
                        print("res_head_number")
                        print(res_head_number)
                        if res_head_number["state"] == "Successful":
                            head_balance = res_head_number["balance"]
                            if int(head_balance) >= int(kids_number[i].package):
                                package = Package.objects.get(name=kids_number[i].package)
                                order = Order.objects.create(head_number=kids_number[i].head_number,
                                                             member_number=kids_number[i].member_number,
                                                             amount=package.price,
                                                             type="automat",
                                                             status="not-charged")
                                res_charge = charge(kids_number[i].member_number, order.pk,
                                                    package.card_type,
                                                    package.price)
                                if res_charge.status_code == 200:
                                    res_charge = json.loads(res_charge.content)
                                    print("res_charge")
                                    print(res_charge)
                                    if "scard" in res_charge:
                                        order.scard = res_charge["scard"]
                                        order.save()
                                    if res_charge["state"] == "Successful":
                                        kids_number[i].status = "charged"
                                        order.status = "charged"
                                        order.charged_date = datetime.datetime.now().strftime(
                                            '%Y-%m-%d %H:%M:%S')
                                        order.shivelt = "1"
                                        order.save()
                                    else:
                                        order.status = "charge-error"
                                        order.save()
                                        kids_number[i].status = "charge-error"
                                else:
                                    order.status = "charge-error"
                                    order.save()
                                    kids_number[i].status = "charge-error"
                            else:
                                kids_number[i].status = "insufficient unit"
                        else:
                            kids_number[i].status = res_head_number["error"]
                else:
                    kids_number[i].status = res_member_number["error"]
            else:
                kids_number[i].status = "not expired package date"
            kids_number[i].save()


thread = threading.Thread(target=automat_charge)
thread.start()
