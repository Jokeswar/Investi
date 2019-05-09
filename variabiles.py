import os

CHROMEDRV = ""
LENDERSID = ""
BASELOGIN = "https://www.mintos.com/en/login"
LOANSPAGE = "https://www.mintos.com/en/available-loans/primary-market/? \
             currencies[]=978&statuses[]=256&pledges[]=8&with_buyback=1&invested_in=0& \
             sort_field=interest&sort_order=DESC&max_results=20"
CONFIRMIV = "https://www.mintos.com/en/review-investments/"

def setVars():
    """ 
    Setting up the values for some global variabiles
    """

    global LENDERSID
    global CHROMEDRV
    
    LENDERSID = os.path.join("data", "loan_originators_id.json")
    CHROMEDRV = os.path.abspath(os.curdir)

    # get path to drive and start chrome
    if os.name == "posix":
        CHROMEDRV = os.path.join(CHROMEDRV, "driver", "chromedriver")
    else:
        CHROMEDRV = os.path.join(CHROMEDRV, "driver", "chromedriver.exe")