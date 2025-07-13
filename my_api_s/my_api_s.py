from rest_framework.parsers import JSONParser
from .response import status_success, status_unsuccessful
from django.http.response import JsonResponse
from rest_framework import status
import time
from rest_framework.decorators import api_view
import logging
from controller.models import *
from other_api_s.sms import send_sms
from django.http import HttpResponse
from other_api_s.charge_between import numberCheck, charge, memberNumber_check, member_check_balance
import json
import datetime


log_date = datetime.datetime.now().strftime('%Y-%m-%d')
log_file = 'log/Log_{0}'.format(log_date)
logging.basicConfig(filename=log_file + '.log', level=logging.DEBUG, format='%(asctime)s:%(levelname)s:%(message)s')

@api_view(['GET'])
def receive_sms555(request):
    sms_from = request.query_params.get('sms_from', None)
    sms_text = request.query_params.get('sms_text', None)
    logging.info(sms_from)
    logging.info(sms_text)
    print(sms_from)
    print(sms_text)
    message_in = UserMessage.objects.create(sms_from=sms_from, sms_to="555", sms_text=sms_text.lower())
    message_out = UserMessage.objects.create(sms_from="555", sms_to=sms_from)
    res_sms_text = ""
    if UserMessage.objects.filter(sms_from=sms_from, received_at__year=datetime.datetime.now().year,
                                         received_at__month=datetime.datetime.now().month, status="3").exists():
        res_sms_text = "Ta nemelt data bagc avax xuselt ilgeesen baina. Tur xuleene uu. Gmobile"
        message_in.status = "8"
    else:
        print((" " in str(sms_text)) is True)
        if (" " in str(sms_text)) is True:
            member_number = sms_text.split(' ')[0]
            bagts = sms_text.lower().split(' ')[1]
            # if bagts == "off":
            #     # automat sungalt OFF hiih
            #     res_sms_text = "{0}-n data bagcyn automat sungalt cuclagdlaa. Ta bucaan idevxjuulex bol 555 dugaart {1} sungax bagcyn dun ON gej ilgeene uu.".format(member_number, member_number)
            # elif bagts == "d":
            #     # member dugaariin uldegdeliig shalgah api duudna
            #     res_member_check_balance = member_check_balance(member_number, bagts)
            #     if res_member_check_balance == "yes":
            #         uldegdel = ""
            #         res_sms_text = "{0} dugaaryn data uldegdel {1}GB baina. Data erx duussan ch bagcyn xugacaandaa 1mbps xurdaar unegui ashiglax bolomjtoi. Gmobile".format(member_number, uldegdel)
            #     else:
            #         res_sms_text = "{0} dugaar data ashiglaagui baina.".format(member_number)
            if bagts == "add":
                # dugaaruudiig shalgaj add hiine success irsen uyed doorh sms-iig ugnu
                res_sms_text = "Ta {0} dugaartai 18 nas xurtlee unegui yarix bolomjtoi bolloo. Gmobile".format(member_number)
                # 5nd dugaar full bol
                res_sms_text = "Tany unegui yarix 5 dugaar burtgegdsen baina. Burtgegdsen dugaaruudaa shalgax bol “List” utgyg ilgeene uu. Gmobile"

            if Package.objects.filter(name__exact=bagts).exists():
                res_head_number = numberCheck(sms_from)
                logging.info("res_head_number")
                logging.info(res_head_number)
                if res_head_number["state"] == "Successful":
                    head_type = res_head_number["postpaid"]
                    if head_type == "":
                        res_sms_text = "Zuv dugaar oruulna uu."
                    elif head_type == "F":
                        res_sms_text = "Systemd burtgelgui dugaar baina."
                    elif head_type == "Y":
                        res_sms_text = "Enehuu uilchilgeeg Uridchilsan tulburt dugaaraas avah bolomjtoi."
                    else:
                        res_member_number = numberCheck(member_number)
                        logging.info("res_member_number")
                        logging.info(res_member_number)
                        if res_member_number["state"] == "Successful":
                            member_type = res_member_number["postpaid"]
                            if member_type == "":
                                res_sms_text = "Zuv dugaar oruulna uu."
                            elif member_type == "F":
                                res_sms_text = "Systemd burtgelgui dugaar baina."
                            elif member_type == "Y":
                                res_sms_text = "Gishuun hereglegchiin dugaar daraah tulburt dugaar baina."
                            else:
                                # gishuun dugaariin tolgoi dugaariig medeh, mun gishuun dugaar tolgoi dugaartaigaa holbogdson esehiig shalgana
                                res_head_check = memberNumber_check(sms_from, "1")
                                if res_head_check["state"] == "Successful":
                                    child_numbers = res_head_check["child_number"]
                                    print("child_numbers")
                                    print(child_numbers)
                                    for child in child_numbers:
                                        if child[0] == member_number:
                                            # gishuun hereglegchiin bagtsiin hugatsaa duussan esehiig shalgana
                                            res_check_package = memberNumber_check(member_number, "2")
                                            print("res_check_package")
                                            print(res_check_package)
                                            if res_check_package["state"] == "Successful":
                                                child_info = res_check_package["child_info"]
                                                exp_date = ""
                                                for i in range(len(child_info)):
                                                    if Package.objects.filter(price_plan_code=child_info[i]["PRICE_PLAN_CODE"]).exists():
                                                        exp_date = child_info[i]["ABS_EXP_DATE"]
                                                        break
                                                end_date = datetime.datetime.strptime(exp_date, '%d-%b-%y')
                                                now_date = datetime.datetime.timestamp(datetime.datetime.now())
                                                exp = datetime.datetime.timestamp(end_date)
                                                if exp < now_date:
                                                    # tolgoi hereglegchiin negjnii uldegdel shalgana
                                                    balance = res_head_number["balance"]
                                                    if int(balance) >= int(bagts):
                                                        package = Package.objects.get(name=bagts)
                                                        order = Order.objects.create(head_number=sms_from,
                                                                                     member_number=member_number,
                                                                                     amount=package.price,
                                                                                     type="manual",
                                                                                     status="not-charged")
                                                        res_charge = charge(member_number, order.pk,
                                                                            package.card_type,
                                                                            package.price)
                                                        if res_charge.status_code == 200:
                                                            res_charge = json.loads(res_charge.content)
                                                            logging.info("res_charge")
                                                            logging.info(res_charge)
                                                            if "scard" in res_charge:
                                                                order.scard = res_charge["scard"]
                                                                order.save()
                                                            if res_charge["state"] == "Successful":
                                                                order.status = "charged"
                                                                order.charged_date = datetime.datetime.now().strftime(
                                                                    '%Y-%m-%d %H:%M:%S')
                                                                order.shivelt = "1"
                                                                order.save()
                                                                sms5 = send_sms(sms_from,
                                                                                "{0}-t Enjoy kids uilchilgeenii {1}, {2} xonogiin xyazgaargui bagc amjilttai ceneglegdej tany dansnaas {3} negj xasagdlaa.".format(
                                                                                    member_number, package.speed,
                                                                                    package.duration, bagts))
                                                                sms5 = str(sms5, encoding='utf-8')
                                                                if sms5 == "0: Accepted for delivery":
                                                                    time.sleep(1)
                                                                    sms6 = send_sms(sms_from,
                                                                                    "{0}-n data bagc duusaxad Tany negjnees {1}-g suutgan sungax Automat sungalt idevxitei baina. Automat sungaltyg cuclax bol 555 dugaart OFF gej ilgeene uu.Gmobile".format(
                                                                                        member_number, bagts))
                                                                    sms6 = str(sms6, encoding='utf-8')
                                                                sms7 = send_sms(member_number,
                                                                                "{0}-s tany dugaart Enjoy kids uilchilgeenii {1}, {2} xonogiin xyazgaargui bagc idevxjuullee. Airplane mode-oo asaaj untraana uu. Gmobile".format(
                                                                                    sms_from, package.speed,
                                                                                    package.duration))
                                                                res_sms_text = "send_sms"
                                                            else:
                                                                order.status = "charge-error"
                                                                order.save()
                                                                res_sms_text = "Ceneglelt xiixed aldaa garlaa. Lavlax 3636-tai xolbogdono uu. Gmobile"
                                                        else:
                                                            res_sms_text = "Ceneglelt xiix servicetei xolbogdoxod aldaa garlaa"
                                                    else:
                                                        res_sms_text = "Tany dansny uldegdel xurelcexgui baina. Dansaa cenegleed daxin oroldono uu. Gmobile"
                                                else:
                                                    sms9 = send_sms(sms_from,
                                                                    "{0}-n data bagcyn xugacaa duusaagui tul davxarduulan ceneglex bolomjgui baina.".format(
                                                                        member_number))
                                                    sms9 = str(sms9, encoding='utf-8')
                                                    if sms9 == "0: Accepted for delivery":
                                                        time.sleep(1)
                                                        sms10 = send_sms(sms_from,
                                                                         "{0}-n data bagc duusaxad Tany negjnees {1}-g suutgan sungax Automat sungalt idevxitei baina. Automat sungaltyg cuclax bol 555 dugaart OFF gej ilgeene uu.".format(
                                                                             member_number, bagts))
                                                        sms10 = str(sms10, encoding='utf-8')
                                                    res_sms_text = "send_sms"
                                            else:
                                                sms91 = send_sms(sms_from,
                                                                "{0} gishuun dugaar bish baina.".format(
                                                                    member_number))
                                                sms91 = str(sms91, encoding='utf-8')
                                                res_sms_text = "send_sms"
                                            break
                                else:
                                    sms11 = send_sms(sms_from,
                                                     "{0} tany dugaartai xolbogdoogui baina. Ta xuuxdiin dugaaraa uuriin dugaartai xolboxyg xusvel gmobile.mn esvel lavlax 3636-s medeelel avna uu. Gmobile".format(
                                                         member_number))
                                    sms11 = str(sms11, encoding='utf-8')
                                    res_sms_text = "send_sms"
                        else:
                            res_sms_text = res_member_number["error"]
                else:
                    res_sms_text = res_head_number["error"]
            else:
                res_sms_text = "Tany ilgeesen utga buruu baina. Enjoy Kids uilchilgeenii tuxai delgerengui medeelliig gmobile.mn bolon lavlax 3636-s avna uu. Gmobile"
        else:
            member_number = sms_from
            bagts = sms_text.lower()
            if Package.objects.filter(name__exact=bagts).exists():
                res_member_number = numberCheck(member_number)
                logging.info("res_member_number")
                logging.info(res_member_number)
                if res_member_number["state"] == "Successful":
                    member_type = res_member_number["postpaid"]
                    if member_type == "":
                        res_sms_text = "Zuv dugaar oruulna uu."
                    elif member_type == "F":
                        res_sms_text = "Systemd burtgelgui dugaar baina."
                    elif member_type == "Y":
                        res_sms_text = "Gishuun hereglegchiin dugaar daraah tulburt dugaar baina."
                    else:
                        # gishuun hereglegchiin bagtsiin hugatsaa duussan esehiig shalgana
                        res_check_package = memberNumber_check(member_number, "2")
                        print("res_check_package")
                        print(res_check_package)
                        if res_check_package["state"] == "Successful":
                            child_info = res_check_package["child_info"]
                            exp_date = ""
                            head_number = ""
                            for i in range(len(child_info)):
                                if Package.objects.filter(price_plan_code=child_info[i]["PRICE_PLAN_CODE"]).exists():
                                    exp_date = child_info[i]["ABS_EXP_DATE"]
                                    head_number = child_info[i]["PARENT_NBR"]
                                    break
                            end_date = datetime.datetime.strptime(exp_date, '%d-%b-%y')
                            now_date = datetime.datetime.timestamp(datetime.datetime.now())
                            exp = datetime.datetime.timestamp(end_date)
                            if exp < now_date:
                                # hereglegchiin negjnii uldegdel shalgana
                                balance = res_member_number["balance"]
                                if int(balance) >= int(bagts):
                                    package = Package.objects.get(name=bagts)
                                    order = Order.objects.create(head_number=sms_from,
                                                                 member_number=member_number,
                                                                 amount=package.price,
                                                                 type="manual",
                                                                 status="not-charged")
                                    res_charge = charge(member_number, order.pk,
                                                        package.card_type,
                                                        package.price)
                                    if res_charge.status_code == 200:
                                        res_charge = json.loads(res_charge.content)
                                        logging.info("res_charge")
                                        logging.info(res_charge)
                                        if "scard" in res_charge:
                                            order.scard = res_charge["scard"]
                                            order.save()
                                        if res_charge["state"] == "Successful":
                                            order.status = "charged"
                                            order.charged_date = datetime.datetime.now().strftime(
                                                '%Y-%m-%d %H:%M:%S')
                                            order.shivelt = "1"
                                            order.save()
                                        res_sms_text = "{0}-t Enjoy kids uilchilgeenii {1}, {2} xonogiin xyazgaargui bagc amjilttai ceneglegdej tany dansnaas {3} negj xasagdlaa.".format(
                                            member_number, package.speed, package.duration, bagts)
                                    else:
                                        res_sms_text = "Ceneglelt xiix servicetei xolbogdoxod aldaa garlaa"
                                else:
                                    res_head_number = numberCheck(head_number)
                                    logging.info("res_head_number")
                                    logging.info(res_head_number)
                                    if res_head_number["state"] == "Successful":
                                        balance = res_head_number["balance"]
                                        if int(balance) >= int(bagts):
                                            package = Package.objects.get(name=bagts)
                                            order = Order.objects.create(head_number=sms_from,
                                                                         member_number=member_number,
                                                                         amount=package.price,
                                                                         type="manual",
                                                                         status="not-charged")
                                            res_charge = charge(member_number, order.pk,
                                                                package.card_type,
                                                                package.price)
                                            if res_charge.status_code == 200:
                                                res_charge = json.loads(res_charge.content)
                                                logging.info("res_charge")
                                                logging.info(res_charge)
                                                if "scard" in res_charge:
                                                    order.scard = res_charge["scard"]
                                                    order.save()
                                                if res_charge["state"] == "Successful":
                                                    order.status = "charged"
                                                    order.charged_date = datetime.datetime.now().strftime(
                                                        '%Y-%m-%d %H:%M:%S')
                                                    order.shivelt = "1"
                                                    order.save()
                                                res_sms_text = "{0}-t Enjoy kids uilchilgeenii {1}, {2} xonogiin xyazgaargui bagc amjilttai ceneglegdej tany dansnaas {3} negj xasagdlaa.".format(
                                                    member_number, package.speed, package.duration, bagts)
                                            else:
                                                res_sms_text = "Ceneglelt xiix servicetei xolbogdoxod aldaa garlaa"
                                        else:
                                            res_sms_text = "Tany dansny uldegdel xurelcexgui baina. Dansaa cenegleed daxin oroldono uu. Esvel tolgoi dugaaraar ceneglelt xiilguulne uu. Gmobile"
                                    else:
                                        res_sms_text = res_head_number["error"]
                            else:
                                res_sms_text = "Uildel amjiltgvi bolloo. Tany data bagcyn xugacaa yyyy/mm/dd hh:mm duusna. Umnux bagc duussan toxioldold shine bagcaar sungax bolomjtoi. Gmobile"
                        else:
                            res_sms_text = "Uuchlaarai ta Enjoy Kids uilchilgeend burtgelgui baina. Delgerengui medeelliig gmobile.mn bolon lavlax 3636-s avna uu. Gmobile"
                else:
                    res_sms_text = res_member_number["error"]
            else:
                res_sms_text = "Tany ilgeesen utga buruu baina. Enjoy Kids uilchilgeenii tuxai delgerengui medeelliig gmobile.mn bolon lavlax 3636-s avna uu. Gmobile"
    message_in.save()
    message_out.sms_text = res_sms_text
    message_out.status = "9"
    message_out.save()
    # logging.info("RESULT")
    # logging.info(result)
    if res_sms_text == "send_sms":
        return HttpResponse("")
    else:
        return HttpResponse(message_out.sms_text)

@api_view(['POST'])
def get_enjoykids_number(request):
    logging.info("get_enjoykids_number")
    if request.method == 'POST':
        data = JSONParser().parse(request)
        member_number = data["member_number"]
        head_number = data["head_number"]
        price_plan_id = data["price_plan_id"]
        price_plan_name = data["price_plan_name"]
        price_plan_code = data["price_plan_code"]
        exp_date = data["exp_date"]
        eff_date = data["eff_date"]
        completed_date = data["completed_date"]
        EnjoyKidsNumbers.objects.create(member_number=member_number, head_number=head_number, status="registered",
                                        price_plan_id=price_plan_id, price_plan_name=price_plan_name,
                                        price_plan_code=price_plan_code, exp_date=exp_date, eff_date=eff_date,
                                        completed_date=completed_date)
        response = status_success(0, "Амжилттай бүртгэсэн", "Registered")
    else:
        response = status_unsuccessful(0, "Зөвшөөрөгдөөгүй арга", "Not allowed method")
    logging.info(response)
    return JsonResponse(response, status=status.HTTP_200_OK)
