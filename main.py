import os
import time
import json

from mintos import Loan
from mintos import analyze
from mintos import LOANDATA
from update import updateData
from getpass import getpass
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

CHROMEDRV = os.path.abspath(os.curdir)
BASELOGIN = "https://www.mintos.com/en/login"
LOANSPAGE = "https://www.mintos.com/en/available-loans/primary-market/? \
             currencies[]=978&statuses[]=256&pledges[]=8&with_buyback=1&invested_in=0& \
             sort_field=interest&sort_order=DESC&max_results=20"
CONFIRMIV = "https://www.mintos.com/en/review-investments/"
LENDERSID = "data/loan_originators_id.json"


def aproximate(number, precision):
    return float(int(number * (10 ** precision))) / (10 ** precision)


def buildLink():
    global LENDERSID
    global LOANSPAGE

    baseString = "&lender_groups[]="
    link = ""
    jsonFile = json.load(open(LENDERSID))

    for loanOriginator in jsonFile["LoanOriginators"]:
        link += baseString + str(jsonFile[loanOriginator]["id"])

    ret = LOANSPAGE + link

    return ret.replace(" ", "")


def login(driver, username, password):
    global BASELOGIN

    # get login page
    driver.get(BASELOGIN)

    # getting login fields
    loginName = driver.find_element_by_name("_username")
    loginPass = driver.find_element_by_name("_password")

    # filling login fields
    loginName.send_keys(username)
    loginPass.send_keys(password)

    # send data to server
    loginPass.send_keys(Keys.ENTER)


def getLoanBook(driver):
    # get loans page
    driver.get(buildLink())

    # get export button
    while True:
        try:
            exportBtn = driver.find_element_by_id("export-button")
            break
        except:
            time.sleep(1)

    exportBtn.click()


def investInLoan(driver, url, amount):
    # get page
    driver.get(url)

    time.sleep(1)

    # get input box
    investAmount = driver.find_element_by_id("invest-amount")
    investAmount.send_keys(Keys.LEFT_CONTROL + "a" + Keys.DELETE)
    investAmount.send_keys(str(amount))

    time.sleep(1)

    # get invest button
    investBtn = driver.find_element_by_id("invest-button")
    investBtn.click()


def confirmInvestments(driver):
    global CONFIRMIV

    # get page
    driver.get(CONFIRMIV)

    time.sleep(1)

    # get button and click it
    # confirmBtn = driver.find_element_by_id("investment-confirm-button")
    # confirmBtn.click()


def moveLoanBook():
    filename = time.strftime("%Y%m%d-primary-market.xlsx", time.gmtime())

    # build download path
    if os.name == "posix":
        pathToDownloadedFile = os.getenv("HOME") + "/Downloads/" + filename
    else:
        pathToDownloadedFile = "C:" + os.getenv("HOMEPATH") + "\\Downloads\\" + filename

    # wait for file to download
    while(os.path.isfile(pathToDownloadedFile) is False):
        time.sleep(2)

    os.rename(pathToDownloadedFile, LOANDATA)


def getBalance(driver):
    allBalance = driver.find_element_by_id("sel-header-balance")
    eurBalance = allBalance.text.split("|")[0][4:]

    return float(eurBalance)


# works with the assumption that there are more loans than investments
def invest(driver, loans):
    current = 0
    balance = getBalance(driver)
    count = int(balance / 10.0)

    # no money no investment
    if count <= 0:
        print("Not enough funds available\nProcess will terminate")
        return

    amount = balance / float(count)
    real_amount = aproximate(amount, 2) 
    rest_amount = balance - real_amount * (count - 1) # can't divide equally
    # aproximate(balance - real_amount * (count - 1), 2) <- old formula
    # aproximation seems to not work sometimes, error of 1 EuroCent
   
    # On normal basis, and being sure that there are no bugs in the software and
    # that the strategy is correct you would uncomment confirmInvestments from 
    # the for below Also in confirmInvestments you should uncomment btn.click().
    # There is a bug on mintos: sometimes you have the same amount of cash
    # invested as what shows up on your balanace(that happens when you have
    # multimple loans). A way around it is to confirm your investments on all
    # n-1 loans and separately for your last. 
    
    for loan in loans:
        if loan is not None:
            if current == count - 1:
                # if count != 1:
                    # confirmInvestments(driver)
                investInLoan(driver, loan.link, rest_amount)
                confirmInvestments(driver)
                break

            if loan.amountaAvailable > real_amount + 1:
                investInLoan(driver, loan.link, real_amount)
                current += 1


def main():
    global CHROMEDRV

    # getting userdata
    us = input("Username: ")
    ps = getpass()

    start = time.time()

    # get path to drive and start chrome
    if os.name == "posix":
        CHROMEDRV = CHROMEDRV + "/driver/chromedriver"
    else:
        CHROMEDRV = CHROMEDRV + "\\driver\\chromedriver.exe"

    driver = webdriver.Chrome(CHROMEDRV)
    driver.minimize_window()

    # log in and remove credemtials from memory
    login(driver, us, ps)
    us = ps = ''

    updateData()
    getLoanBook(driver)
    moveLoanBook()
    loans = analyze()
    invest(driver, loans)

    os.remove(LOANDATA)
    driver.maximize_window()
    # driver.quit()
    print("Execution lasted: {} s".format(time.time() - start))
    return 0


if __name__ == '__main__':
    main()
    input("Waiting for any key press to terminate....")
