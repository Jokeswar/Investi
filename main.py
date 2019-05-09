import os
import time
import json
from variabiles import *

from mintos import Loan
from mintos import analyze
from mintos import LOANDATA
from update import updateData
from getpass import getpass
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


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
    # might need for the javascript to finish loading 
    # all loans for the button to apear
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

    # NOTE:
    # Not ready for fully automated investment confirmation

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
   
    # NOTE: 
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

            if loan.amountAvailable > real_amount + 1:
                investInLoan(driver, loan.link, real_amount)
                current += 1


def main():
    global CHROMEDRV

    # Function that assings global variabiles their correct values
    setVars()

    # getting userdata
    username = input("Username: ")
    password = getpass()

    start = time.time()    

    # starting chrome on automation mode
    driver = webdriver.Chrome(CHROMEDRV, service_log_path = os.devnull)
    driver.minimize_window()

    # log in and remove credemtials from memory
    login(driver, username, password)
    del username
    del password

    # if the account has no money there is no need to continue the process
    currentBallance = getBalance(driver)
    if currentBallance <= 0.0:
        print("Your balance is 0\n Process will terminate")

    updateData()
    getLoanBook(driver)
    moveLoanBook()
    loans = analyze()
    invest(driver, loans)

    # clean-up
    os.remove(LOANDATA)

    # NOTE: 
    # When the program will be fully capable of a well tested investment
    # strategy maximize_windonw will be deleted. This is because at the moment 
    # confirmations will be manual for verfication purpouses

    driver.maximize_window()
    # driver.quit()

    print("Execution lasted: {} s".format(time.time() - start))


if __name__ == '__main__':
    main()
    input("Waiting for any key press to terminate....")
