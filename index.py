import csv 
import json
import datetime

def dateCredit(timestamp):
    if timestamp.day<5:
        newDate=datetime.date(timestamp.year, timestamp.month, 10)
    else:
        if timestamp.month==12:
            newDate=datetime.date((timestamp.year)+1, 1, 10)
        else:
            newDate=datetime.date(timestamp.year, (timestamp.month)+1, 10)

    return newDate

def formatDate(timestamp):
    arrayDateTime = timestamp.split(" ")
    arrayDate = arrayDateTime[0].split('-')
    date =datetime.date(int(arrayDate[0]),int(arrayDate[1]),int(arrayDate[2]))
    return date

def formatPrice(price):
    arrayAuxi = price.split(" ")
    value = float(arrayAuxi[1])
    return value

def saveValues(Cashier):
    newFile = open('Cashier.jsonl', 'w')
    for dictionary in Cashier:
        value = round(Cashier[dictionary], 2)
        string = '{"date": "' + str(dictionary) + '", "value":' + str(value) + '},\n'
        newFile.write(string)

    newFile.close()

def installment(price,nPortion):
    price = round(price*100)
    cont = 0
    while((price%nPortion)!=0):
        cont += 1
        price -= 1

    valuePortion = price/nPortion
    valuePortion = round(valuePortion/100, 2)
    credit = [valuePortion, cont]
    return credit

def addCashier(date,value,cashier):
    if date in cashier:
        global dateAuxi
        dateAuxi = date
        value = round((cashier[date] + value),2)
        cashier[date] = value
    else:
        cashier[date] = value

def checkCashier(cashier):
    date = dateAuxi
    dateEnd = dateAuxi

    for key in cashier:
        if key < date:
            date = key
        elif key > dateEnd:
            dateEnd = key

    value = 0
    while date<=dateEnd:
        if date in cashier:
            value = round((cashier[date] + value),2)
            cashier[date] = value
        else:
            cashier[date] = value

        date = date + datetime.timedelta(days=1)

def paymentCredit(type, n_payments, price, timestamp, cashier):
    timestamp = dateCredit(timestamp)
    credit = installment(price,n_payments)
    vPortion = credit[0]
    over = credit[1]
    i = 0
    while(i<n_payments):
        value = vPortion
        if over!=0:
            value = round((value + 0.01), 2)
            over -= 1
        
        if type=='purchases':
            value = round(value * -1, 2)

        addCashier(timestamp, value, cashier)
        
        if timestamp.month==12:
            timestamp=datetime.date((timestamp.year)+1, 1, 10)
        else:
            timestamp=datetime.date(timestamp.year, (timestamp.month)+1, 10)
        i += 1


#init csv itens
csvDictionary = {}
csvFile = csv.reader(open('catalog.csv', 'r'))
for item in csvFile:
    if item[0] != 'id':
        price = formatPrice(item[1])
        csvDictionary[item[0]] =  price


cashier = {}

with open('purchases.jsonl') as f:
    for line in f:
        j_content = json.loads(line)
        n_payments = j_content.get("n_payments")
        payment_method = j_content.get("payment_method")
        price =  formatPrice(j_content.get("price"))
        timestamp = formatDate(j_content.get("timestamp"))

        if payment_method=='credit':
            paymentCredit('purchases', n_payments, price, timestamp, cashier)

        else:
            value = round((price * -1),2)
            addCashier(timestamp,value,cashier)

with open('sales.jsonl') as f:
    for line in f:
        j_content = json.loads(line)
        product_id = j_content.get("product_id")
        payment_method = j_content.get("payment_method")
        n_payments = j_content.get("n_payments")
        price = float(csvDictionary[product_id])
        timestamp = formatDate(j_content.get("timestamp"))

        if payment_method=='credit':
            paymentCredit('sales', n_payments, price, timestamp, cashier)

        else:
            value = price
            addCashier(timestamp,value,cashier)

checkCashier(cashier)
saveValues(cashier)