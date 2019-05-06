import os
import json

from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from mintos import JSONREQ

CONV = "https://www.exchange-rates.org/converter/{}/EUR/{}/Y"
BASE = "https://tradingeconomics.com"
URL = "/{}/wages"


def GetWage(country):
    country = country.lower()
    link = BASE + URL.format(country)
    req = Request(link, headers={'User-Agent': 'Mozilla/5.0'})
    html = urlopen(req).read()
    soup = BeautifulSoup(html, 'html.parser')

    wageRow = soup.findAll("a", {"href": URL.format(country)})[0]
    averageWage = wageRow.parent.parent.findChildren()[2].text

    return str(averageWage)


def ConvertToEUR(amount, fromCurrency):
    link = CONV.format(fromCurrency, amount)
    req = Request(link, headers={'User-Agent': 'Mozilla/5.0'})
    html = urlopen(req).read()
    soup = BeautifulSoup(html, 'html.parser')

    resultAmount = soup.findAll("span", {"id": "ctl00_M_lblToAmount"})[0].text

    return str(resultAmount)


def updateData():
    with open(JSONREQ, 'r+') as f:
        data = json.load(f)
        for loanOriginator in data["LoanOriginators"]:
            country = str(data[loanOriginator]["country"])
            currency = str(data[loanOriginator]["currency"])

            wage = GetWage(country)
            if currency != "EUR":
                wage = ConvertToEUR(wage, currency)

            data[loanOriginator]["wage"] = wage.replace(",","")

        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate() 
