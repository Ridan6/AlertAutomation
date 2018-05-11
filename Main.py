from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoAlertPresentException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
import tkinter as tk
from selenium import webdriver
from pprint import pprint as pprint
import sys
import pandas as pd
import winsound
import time
import msvcrt
import re

live = 'https://sem.wdf.sap.corp/sap/hana/uis/clients/ushell-app/shells/fiori/FioriLaunchpad.html?siteId=sap.secmon.ui.mobile.launchpad|ETDLaunchpad&sap-language=en#AlertsList-show&/?orderBy=creationDate&orderDesc=true&status=OPEN&measureContext=Alert,Log&timeSelectionType=relative&timeLast=&timeType=days&uistate=id-1520962806818-186&lastNav=20180313174007'
test = 'https://sem.wdf.sap.corp/sap/hana/uis/clients/ushell-app/shells/fiori/FioriLaunchpad.html?siteId=sap.secmon.ui.mobile.launchpad|ETDLaunchpad&sap-language=en#AlertsList-show&/?orderBy=creationDate&orderDesc=false&status=OPEN,INVESTIG_TRIGGERED&measureContext=Alert,Log&timeSelectionType=relative&timeLast=1&timeType=hours&uistate=id-1524314696471-110&lastNav=20180421124509'

class AlertHandler():
    sleeptime = 5
    refresh_count = 0

    def __init__(self):
        print('--Initializing Driver--')
        options = webdriver.ChromeOptions()
        options.add_argument('--ignore-certificate-errors')
        options.add_argument("--test-type")

        self.driver = webdriver.Chrome(r'C:\Users\c5266897\Downloads\chromedriver.exe', options=options)
        #--------URL----------
        self.driver.get(live)
        self.driver.maximize_window()

        self.dwaittime = 30

        AlertHandler.elements_loader(self)
    def driver_wait_time_incresor(self):

        if self.dwaittime == 100:
            print('Wait time long, check if system operational')
            AlertHandler.page_refresher(self)
        else:
            self.dwaittime = self.dwaittime + 10
            print('wait time = ' + str(self.dwaittime))
            AlertHandler.elements_loader(self)

    def elements_loader(self):
        print('--Element Loader init--')

        try:
            self.driver.switch_to_alert().dismiss()
            print('Alert Dismissed')
        except NoAlertPresentException:
            pass

        print('Waiting for Page load --' + str(self.dwaittime))

        try:
            WebDriverWait(self.driver, self.dwaittime).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="__button9-content"]')))
            self.num = self.driver.find_element_by_xpath('//*[@id="__button9-content"]')
            print('Page Loaded')
            self.dwaittime = 20

        except NoSuchElementException:
            print("No such element was located, Critical Error")

        except TimeoutException:
            print("Loading took too much time!")
            AlertHandler.driver_wait_time_incresor(self)

        AlertHandler.alert_refresh(self)

    def alert_refresh(self):
        print('--Alert Refresher--')

        i = 1
        while i == 1:
            WebDriverWait(self.driver, 120).until_not(EC.presence_of_element_located((By.XPATH, '//*[@class="sapUiLocalBusyIndicatorAnimation"]')))
            if self.driver.find_element_by_xpath('//*[@id="__xmlview7--alertsTable"]').text == 'No data':
                #print('no data')
                time.sleep(2)
                self.driver.find_element_by_xpath('//*[@id="__button9-content"]').click()
            elif self.num.text == 'Alerts (0)':
                print(self.num.text + 'Resetting')
                time.sleep(3)
            else:
                i = 2
                print(self.num.text + ' alert found ')
                winsound.Beep(440, 220)
                AlertHandler.alert_scrapper(self)

    def alert_scrapper(self):
        print('--Alert Scrapper Init--')

        self.invname = ''
        clonecss = self.driver.find_elements_by_css_selector('tr')
        patternxpath = self.driver.find_elements_by_xpath('//*[@class="sapMLnk sapMLnkMaxWidth sapMLnkWrapping"]')
        triggerxpath = self.driver.find_elements_by_xpath('//*[@class="sapMLIB sapMLIB-CTX sapMLIBShowSeparator sapMLIBTypeInactive sapMListTblRow sapMListTblRowMiddle"]')

        triggerxpath = list(filter(None, triggerxpath))

        clone = [x.get_attribute('id') for x in clonecss if x.get_attribute('id') not in ('__xmlview7--alertsTableFixed-tblHeader', '__xmlview7--alertsTable-tblHeader')]
        pattern = [y.text for y in patternxpath if y.text not in ('1')]
        trigger = [i.text for i in triggerxpath]
        acting = []
        actor = []
        targeted = []

        pprint(targeted)

        for l in trigger:
            try:
                acting.append(re.search("Acting' = '(.+?)'", l).group(1))
            except AttributeError:
                acting.append('N/A')
            try:
                actor.append(re.search("Actor' = '(.+?)'", l).group(1))
            except AttributeError:
                actor.append('N/A')
            try:
                targeted.append(re.search("Targeted' = '(.+?)'", l).group(1))
            except AttributeError:
                targeted.append('N/A')


        for clones in clone:
            if clones == '__xmlview7--alertsTable-nodata':
                print('__xmlview7--alertsTable-nodata is populating clone list -- Resetting')
                clone = []
                time.sleep(5)
                AlertHandler.alert_refresh(self)
            else:
                pass

        patternset = set(pattern)
        self.patternlist = list(patternset)
        self.alertnum = len(self.patternlist)

        self.df = pd.DataFrame({'pattern': pattern,
                                'clone': clone,
                                'actor': actor,
                                'acting': acting,
                                'targeted': targeted,
                                'trigger': trigger}, columns=['pattern', 'clone', 'actor', 'acting', 'targeted', 'trigger'])
        pd.set_option('display.max_colwidth', -1)
        print(self.df.to_string())
        print('Alerts Scrapped finished')


        if self.alertnum >= 0:
            AlertHandler.investigation_luncher(self)
        else:
            AlertHandler.alert_refresh(self)

    def investigation_luncher(self):
        print('--Investigation Luncher--')
        print('Number of unique alerts = ' + str(self.alertnum))

        if self.alertnum != 0:
            for x in self.patternlist:
                print(self.patternlist)
                if x == 'Z:01.015.01_Linux_repeatattack_loginsource_S012.1' or x == 'Z:01.016.01_Linux_repeatattack_logintarget_S012.2':
                    print('HANDLING -- Z:01.016.01_Linux_repeatattack_logintarget_S012.X')
                    self.alertnum = self.alertnum - 1
                    AlertHandler.linux_alert_handler(self)
                elif x == 'Z:06.001.01_Background Jobs with Locked Dialog Users':
                    print('HANDLING -- Z:06.001.01_Background Jobs with Locked Dialog Users')
                    self.alertnum = self.alertnum - 1
                    self.patternlist.pop(0)
                    AlertHandler.backround_jobs_handler(self)
                elif x == 'Z:P05.013.01_USB_Server_mass_storage_linux_S123':
                    print('HANDLING -- Z:P05.013.01_USB_Server_mass_storage_linux_S123')
                    self.alertnum = self.alertnum - 1
                    AlertHandler.USB_alert_handler(self)
                elif x == 'Z:01.025.01_allowed_SNMP':
                    print('Strating Z:01.025.01_allowed_SNMP')
                    self.alertnum = self.alertnum - 1
                    AlertHandler.allowed_snmp_handler(self)
                elif x == 'Z:02.011.01_SAL Directory Traversal1':
                    print('Strating Z:02.011.01_SAL Directory Traversal1')
                    self.alertnum = self.alertnum - 1
                    AlertHandler.SAL_Directory_Traversal1(self)
                elif x == 'Z:01.004.01_SAL User locked':
                    print('Strating Z:01.004.01_SAL User locked')
                    self.alertnum = self.alertnum - 1
                    AlertHandler.User_locked(self)
                elif x == 'Z:05.009.01_SCP-DomainDB-Unauthorized user' or x == 'Z:01.031.01_SCP-HTML5ApplicationRuntime-Failed Logon':
                    print('Z:05.009.01_SCP-DomainDB-Unauthorized user')
                    self.alertnum = self.alertnum - 1
                    AlertHandler.scp_DomainDB(self)
                elif x == 'Z:02.027.01_UserAccount_changed_linux_S122':
                    print('Z:02.027.01_UserAccount_changed_linux_S122')
                    self.alertnum = self.alertnum - 1
                    AlertHandler.UserAccount_changed(self)
                else:
                    self.patternlist.pop(0)
                    print('removed first alert -- unknown pattern')
                    self.alertnum = self.alertnum - 1
                    AlertHandler.investigation_luncher(self)

        print('alerts have reached 0 -- Refreshing')
        time.sleep(10)
        self.driver.find_element_by_xpath('//*[@id="__button9-content"]').click()
        AlertHandler.alert_refresh(self)

    def investigations_table_scrapper(self):
        print('--Scrapping Investigation Table--')
        print('INVNAME ======= ' + self.invname)

        time.sleep(1)
        addToInvestBtn = WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="__xmlview7--addToInvestBtn-content"]')))
        addToInvestBtn.click()
        WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@id="__xmlview7--investigationsTable-tblBody"]//tr//td[2]//span')))


        """
        if self.invname == 'USB Server mass storage linux S123':
            print('==Scrolling Down==')
            element_inside_popup = self.driver.find_element_by_xpath('//*[@id="__xmlview7--investigationsTable-listUl"]')
            element_inside_popup.send_keys(Keys.END)
            time.sleep(2)
        """

        self.investigation = [row.text for row in self.driver.find_elements_by_xpath('//*[@id="__xmlview7--investigationsTable-tblBody"]//tr//td[2]//span')]


        for row in self.investigation:
            if row == self.invname:
                self.driver.find_element_by_xpath("//*[text()='" + self.invname + "']").click()
                time.sleep(1)
                # ----------------KEEP DISABLED FOR TESTING-------------------
                self.driver.find_element_by_xpath('//*[@id="__xmlview7--addAndReturnButton-content"]').click()

        AlertHandler.page_refresher(self)

    def USB_alert_handler(self):
        print('--USB alert handler--')

        df = self.df
        for index, row in df.iterrows():
            if row['pattern'] == 'Z:P05.013.01_USB_Server_mass_storage_linux_S123':
                self.invname = 'USB Server mass storage linux S123'
                print(row['pattern'], row['clone'])

                xpath = '//*[@id="' + row['clone'] + '-selectMulti-CbBg"]'
                print(xpath)
                try:
                    print('waiting for element clicable')
                    WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.XPATH, xpath)))
                    self.driver.find_element_by_xpath(xpath).click()
                except TimeoutException:
                    print('xpath not clicable -- critical error')
                    AlertHandler.page_refresher(self)
                print('//CHECK FOR ERRORS// Pattern -' + row['pattern'] + '-added to--' + self.invname)
            else:
                print('not usb alert')
        AlertHandler.investigations_table_scrapper(self)
    def allowed_snmp_handler(self):
        print('--allowed_SNMP handler--')

        df = self.df
        self.invname = 'Z:01.025.01_allowed_SNMP_rt-hec04-101'
        for index, row in df.iterrows():
            if row['pattern'] == 'Z:01.025.01_allowed_SNMP' and row['actor'] == 'rt-hec04-101':
                print(row['pattern'], row['actor'])

                xpath = '//*[@id="' + row['clone'] + '-selectMulti-CbBg"]'
                try:
                    WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.XPATH, xpath)))
                    self.driver.find_element_by_xpath(xpath).click()
                except WebDriverException:
                    print('xpath not clicable')
                    AlertHandler.allowed_snmp_handler(self)

                print('//CHECK FOR ERRORS// Pattern -' + row['pattern'] + row['actor'] + '-added to--' + self.invname)
            else:
                print('allowed_SNMP_rt-hec04-101 alert handler couldnt finish--Critical Error ')
        AlertHandler.investigations_table_scrapper(self)
    def linux_alert_handler(self):
        print('--Linux alert handler--')

        df = self.df
        for x in self.patternlist:
            print(x)
            if x == 'Z:01.015.01_Linux_repeatattack_loginsource_S012.1':
                self.invname = 'Linux_repeatattack_loginsource_S012.1_Generic'
                print(self.invname)
                self.patternlist.pop(0)
                for index, row in df.iterrows():
                    if row['pattern'] == 'Z:01.015.01_Linux_repeatattack_loginsource_S012.1':
                        print('linux 012.1 detected')
                        xpath = '//*[@id="' + row['clone'] + '-selectMulti-CbBg"]'
                        try:
                            WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.XPATH, xpath)))
                            self.driver.find_element_by_xpath(xpath).click()
                            print('//CHECK FOR ERRORS// Pattern --' + row['pattern'] + '--added to---' + self.invname)
                        except TimeoutException:
                            print('xpath not clicable -- critical error')
                AlertHandler.investigations_table_scrapper(self)

            elif x == 'Z:01.016.01_Linux_repeatattack_logintarget_S012.2':
                self.invname = 'Linux_repeatattack_logintarget_S012.2_Generic'
                print(self.invname)
                for index, row in df.iterrows():
                    if row['pattern'] == 'Z:01.016.01_Linux_repeatattack_logintarget_S012.2':
                        print('linux s012.2 detected')
                        xpath = '//*[@id="' + row['clone'] + '-selectMulti-CbBg"]'
                        self.driver.find_element_by_xpath(xpath).click()
                        print('//CHECK FOR ERRORS// Pattern --' + row['pattern'] + '--added to---' + self.invname)
                AlertHandler.investigations_table_scrapper(self)
            else:
                print('error no linux found')
    def backround_jobs_handler(self):

        df = self.df

        for index, row in df.iterrows():
            if row['pattern'] == 'Z:06.001.01_Background Jobs with Locked Dialog Users' and row[
                'actor'] == 'ICD/000' and row['acting'] == 'WHHNZRN-55425':
                self.invname = ''
                xpath = '//*[@id="' + row['clone'] + '-selectMulti-CbBg"]'
                self.driver.find_element_by_xpath(xpath).click()

            elif row['pattern'] == 'Z:06.001.01_Background Jobs with Locked Dialog Users' and row[
                'actor'] == 'ISD/000' and row['acting'] == 'OKKPNYM-37616':
                self.invname = ''
                xpath = '//*[@id="' + row['clone'] + '-selectMulti-CbBg"]'
                self.driver.find_element_by_xpath(xpath).click()

            elif row['pattern'] == 'Z:06.001.01_Background Jobs with Locked Dialog Users' and row[
                'actor'] == 'F1T/000' and row['acting'] == 'NLFJIVP-67854':
                self.invname = ''
                xpath = '//*[@id="' + row['clone'] + '-selectMulti-CbBg"]'
                self.driver.find_element_by_xpath(xpath).click()
    def SAL_Directory_Traversal1(self):
        print('--sal started--')
        df = self.df

        for index, row in df.iterrows():
            print(row)
            if row['pattern'] == 'Z:02.011.01_SAL Directory Traversal1' and row['actor'] == 'I4T/001':
                print('sal user I4T/001')
                self.invname = 'SAL Directory Traversal_I4*'
                xpath = '//*[@id="' + row['clone'] + '-selectMulti-CbBg"]'
                self.driver.find_element_by_xpath(xpath).click()
                print('//CHECK FOR ERRORS// Pattern -' + row['pattern'] + '-added to--' + self.invname)
            elif row['pattern'] == 'Z:02.011.01_SAL Directory Traversal1' and row['actor'] == 'ISP/001':
                print('sal user isp')
                self.invname = 'SAL Directory Traversal1_IS*'
                xpath = '//*[@id="' + row['clone'] + '-selectMulti-CbBg"]'
                self.driver.find_element_by_xpath(xpath).click()
                print('//CHECK FOR ERRORS// Pattern -' + row['pattern'] + '-added to--' + self.invname)
            elif row['pattern'] == 'Z:02.011.01_SAL Directory Traversal1' and row['actor'] == 'PI1/001':
                print('sal user PI')
                self.invname = 'SAL Directory Traversal1_PI*'
                xpath = '//*[@id="' + row['clone'] + '-selectMulti-CbBg"]'
                self.driver.find_element_by_xpath(xpath).click()
                print('//CHECK FOR ERRORS// Pattern -' + row['pattern'] + '-added to--' + self.invname)
            elif row['pattern'] == 'Z:02.011.01_SAL Directory Traversal1' and row['actor'] == 'IPD/001':
                print('sal user IP')
                self.invname = 'SAL Directory Traversal1_IP*'
                xpath = '//*[@id="' + row['clone'] + '-selectMulti-CbBg"]'
                self.driver.find_element_by_xpath(xpath).click()
                print('//CHECK FOR ERRORS// Pattern -' + row['pattern'] + '-added to--' + self.invname)
            elif row['pattern'] == 'Z:02.011.01_SAL Directory Traversal1' and row['actor'] == 'I4P/001':
                print('sal user I4P/001 ')
                self.invname = 'SAL Directory Traversal_I4*'
                xpath = '//*[@id="' + row['clone'] + '-selectMulti-CbBg"]'
                self.driver.find_element_by_xpath(xpath).click()
                print('//CHECK FOR ERRORS// Pattern -' + row['pattern'] + '-added to--' + self.invname)
            elif row['pattern'] == 'Z:02.011.01_SAL Directory Traversal1' and row['actor'] == 'ISD/001':
                print('sal user ISD/001')
                self.invname = 'SAL Directory Traversal1_IS*'
                xpath = '//*[@id="' + row['clone'] + '-selectMulti-CbBg"]'
                self.driver.find_element_by_xpath(xpath).click()
                print('//CHECK FOR ERRORS// Pattern -' + row['pattern'] + '-added to--' + self.invname)
            elif row['pattern'] == 'Z:02.011.01_SAL Directory Traversal1' and row['actor'] == 'IPP/001':
                print('sal user IPP/001')
                self.invname = 'SAL Directory Traversal1_IP*'
                xpath = '//*[@id="' + row['clone'] + '-selectMulti-CbBg"]'
                self.driver.find_element_by_xpath(xpath).click()
                print('//CHECK FOR ERRORS// Pattern -' + row['pattern'] + '-added to--' + self.invname)
            else:
                print('No criteria was met')
                print(row['pattern'] + row['actor'])
                AlertHandler.page_refresher(self)

        AlertHandler.investigations_table_scrapper(self)
    def User_locked(self):
        print('--User Locked--')

        df = self.df
        for index, row in df.iterrows():
            print(row['pattern'] + row['actor'])
            if row['pattern'] == 'Z:01.004.01_SAL User locked' and row['actor'] != 'W72/001':
                print('sal user locked =! w72')
                print(row['pattern'], row['clone'])
                xpath = '//*[@id="' + row['clone'] + '-selectMulti-CbBg"]'
                self.invname = 'creating new sal user locked'
                try:
                    self.driver.find_element_by_xpath(xpath).click()
                    self.driver.find_element_by_xpath('//*[@id="__xmlview7--startInvestBtn-content"]').click()
                    time.sleep(1)
                    self.driver.find_element_by_xpath('//*[@id="__item109"]').click()
                    time.sleep(2)

                    des = self.driver.find_element_by_xpath('//*[@id="__xmlview7--description-inner"]')
                    des.send_keys('SAL User locked_' + row['actor'] + '_' + row['targeted'])

                    self.driver.find_element_by_xpath('//*[@id="__select1-label"]').click() #status
                    self.driver.find_element_by_xpath('//*[@id="__item114-__select1-1"]').click()
                    self.driver.find_element_by_xpath('//*[@id="__select1-label"]').click()  # status
                    time.sleep(1)

                    self.driver.find_element_by_xpath('//*[@id="__button13-img"]').click()  # cuser

                    self.driver.find_element_by_xpath('//*[@id="__select0-label"]').click() #severity
                    self.driver.find_element_by_xpath('//*[@id="__item112-__select0-3"]').click() #low
                    self.driver.find_element_by_xpath('//*[@id="__select0-label"]').click()  # severity
                    time.sleep(1)

                    self.driver.find_element_by_xpath('//*[@id="__select2-label"]').click() #attack
                    self.driver.find_element_by_xpath('//*[@id="__item115-__select2-3"]').click()
                    self.driver.find_element_by_xpath('//*[@id="__select2-label"]').click()
                    time.sleep(1)

                    self.driver.find_element_by_xpath('//*[@id="__select3-label"]').click()  #management
                    self.driver.find_element_by_xpath('//*[@id="__item116-__select3-13"]').click()
                except StaleElementReferenceException:
                    print('Stale element reference -- critical error resetting')
                    AlertHandler.page_refresher(self)
                except WebDriverException:
                    print('Element not clicable -- critical error reesetting')
                    AlertHandler.page_refresher(self)

            elif row['pattern'] == 'Z:01.004.01_SAL User locked' and row['actor'] == 'W72/001':

                print('sal user w72 handler')

                self.invname = 'SAL User Locked_W72/001_Generic'
                print(row['pattern'], row['clone'])

                xpath = '//*[@id="' + row['clone'] + '-selectMulti-CbBg"]'
                self.driver.find_element_by_xpath(xpath).click()
                print('//CHECK FOR ERRORS// Pattern -' + row['pattern'] + '-added to--' + self.invname)
                AlertHandler.investigations_table_scrapper(self)
            else:
                print('no sal user locked handler was found')

            time.sleep(5)

            try:
                self.driver.find_element_by_xpath('//*[@id="__button15-content"]').click() #add and return
            except NoSuchElementException:
                pass
            else:
                pass
        time.sleep(10)
        AlertHandler.page_refresher(self)
    def scp_DomainDB(self):
        print('--SCP handler--')

        df = self.df
        for index, row in df.iterrows():
            if row['pattern'] == 'Z:05.009.01_SCP-DomainDB-Unauthorized user':
                print(row['pattern'], row['clone'])
                xpath = '//*[@id="' + row['clone'] + '-selectMulti-CbBg"]'
                self.invname = 'SCP'
                deskey = 'SCP-DomainDB-Unauthorized user'

                try:
                    print('waiting for element clicable')
                    WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.XPATH, '//*[@class="sapMCbActiveStateOff sapMCbBg sapMCbHoverable sapMCbMark"]')))
                    self.driver.find_element_by_xpath(xpath).click()
                except WebDriverException:
                    print('xpath not clicable')
                    AlertHandler.scp_DomainDB(self)

            elif row['pattern'] == 'Z:01.031.01_SCP-HTML5ApplicationRuntime-Failed Logon':
                print(row['pattern'], row['clone'])
                xpath = '//*[@id="' + row['clone'] + '-selectMulti-CbBg"]'
                deskey = 'SCP-HTML5ApplicationRuntime-Failed Logon'
                self.invname = 'SCP'

            elif row['pattern'] == 'Z:05.008.01_SCP-Metering_Service-Unauthorized access':
                print(row['pattern'], row['clone'])
                xpath = '//*[@id="' + row['clone'] + '-selectMulti-CbBg"]'
                deskey = 'SSCP-Metering_Service-Unauthorized access'
                self.invname = 'SCP'

                try:
                    WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.XPATH, xpath)))
                except WebDriverException:
                    print('xpath not clicable')
                    AlertHandler.scp_DomainDB(self)

                self.driver.find_element_by_xpath(xpath).click()
            else:
                deskey = 'SCP pattern'

        try:
            self.driver.find_element_by_xpath('//*[@id="__xmlview7--startInvestBtn-content"]').click()
            self.driver.find_element_by_xpath('//*[@id="__item109-txt"]').click()
            time.sleep(2)

            des = self.driver.find_element_by_xpath('//*[@id="__xmlview7--description-inner"]')
            des.send_keys(deskey)

            self.driver.find_element_by_xpath('//*[@id="__button13-img"]').click()
            self.driver.find_element_by_xpath('//*[@id="__select1-label"]').click()
            self.driver.find_element_by_xpath('//*[@id="__item114-__select1-1"]').click()
            self.driver.find_element_by_xpath('//*[@id="__select0-label"]').click() #severity
            self.driver.find_element_by_xpath('//*[@id="__item112-__select0-2"]').click() #medium

            com = self.driver.find_element_by_xpath('//*[@id="__area0-inner"]')
            com.send_keys('As no agreement on the handover of alerts has been reached yet, this investigation is closed without any further action.')

            self.driver.find_element_by_xpath('//*[@id="__select3-label"]').click() #management
            self.driver.find_element_by_xpath('//*[@id="__item116-__select3-13"]').click()

        except WebDriverException:
            print('couldnt find element clicable')

        time.sleep(15)
        AlertHandler.page_refresher(self)
    def UserAccount_changed(self):
        print('--UserAccount_changed--')

        df = self.df
        for index, row in df.iterrows():
            if row['pattern'] == 'Z:02.027.01_UserAccount_changed_linux_S122':
                self.invname = 'UserAccount_changed_linux_S122'
                print(row['pattern'], row['clone'])

                xpath = '//*[@id="' + row['clone'] + '-selectMulti-CbBg"]'
                print(xpath)
                try:
                    print('waiting for element clicable')
                    WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.XPATH, xpath)))
                    self.driver.find_element_by_xpath(xpath).click()
                except TimeoutException:
                    print('xpath not clicable -- critical error')
                    AlertHandler.page_refresher(self)
                print('//CHECK FOR ERRORS// Pattern -' + row['pattern'] + '-added to--' + self.invname)
            else:
                print('UserAccount_changed_linux_S122 not alert')
        AlertHandler.investigations_table_scrapper(self)

    def page_refresher(self):

        stime = str(self.sleeptime)
        print('Refreshing in ' + stime + ' sec')
        time.sleep(self.sleeptime)
        self.driver.refresh()
        AlertHandler.elements_loader(self)

    def driver_url_return(self):

        self.driver.get(live)



if __name__ == '__main__':
    main = AlertHandler()
