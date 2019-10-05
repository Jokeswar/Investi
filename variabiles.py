import os

def init():
    """
    Setting up the values for the global GLOBALS dictionary
    """

    global GLOBALS
    GLOBALS = {}

    GLOBALS["JSONREQ"] = os.path.join("data", "loan_originators_req.json")
    GLOBALS["LOANDATA"] = "loans.xlsx"
    GLOBALS["OUTPUTFILE"] = "loanList.txt"
    GLOBALS["BASELOGIN"] = "https://www.mintos.com/en/login"
    GLOBALS["LOANSPAGE"] = "https://www.mintos.com/en/invest-en/\
                               primary-market/?currencies[]=978&statuses[]=256\
                               &pledges[]=8&with_buyback=1&invested_in=0&\
                               sort_field=interest&sort_order=DESC&\
                               max_results=20"
    GLOBALS["CONFIRMIV"] = "https://www.mintos.com/en/review-investments/"
    GLOBALS["LENDERSID"] = os.path.join("data", "loan_originators_id.json")

    driver = os.path.abspath(os.curdir)

    # get path to drive and start chrome
    if os.name == "posix":
        driver = os.path.join(driver, "driver", "chromedriver")
    else:
        driver = os.path.join(driver, "driver", "chromedriver.exe")

    GLOBALS["DRIVER"] = driver
