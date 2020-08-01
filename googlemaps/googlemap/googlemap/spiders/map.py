# -*- coding: utf-8 -*-
import scrapy
import time
import os
from scrapy.selector import Selector
from scrapy_selenium import SeleniumRequest
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class MapSpider(scrapy.Spider):
    name = 'map'

    keyword=['KEYWORD','RANK']
    rank=[5,7]

    def start_requests(self):
        index = 0
        yield SeleniumRequest(
            url="https://www.google.com/maps",
            wait_time=1000,
            screenshot=True,
            callback=self.parse,
            meta={'index': index},
            dont_filter=True
        )

    def parse(self, response):

        index = response.meta['index']

        driver = response.meta['driver']

        firstinput = os.path.abspath(os.curdir) + "\Businessinfo.txt"
        f = open(firstinput, "r")
        business_info = f.read().splitlines()

        secondinput = os.path.abspath(os.curdir) + "\Business.txt"
        f = open(secondinput, "r")
        business_name = f.read().splitlines()

        length = len(business_info)
        if (index < length):
            driver.find_element_by_xpath("//*[@id='searchboxinput']").clear()
            search_input1 = driver.find_element_by_xpath("//*[@id='searchboxinput']")


            search_input1.send_keys(business_info[index])

            search_button=driver.find_element_by_xpath('//*[@id="searchbox-searchbutton"]')
            search_button.click()



        # business_name='NYU College of Dentistry'

        # if(index<length):
            driver = response.meta['driver']
            print('\n' * 2)
            print('url',driver.current_url)
            print('\n' * 2)
            # WebDriverWait(driver, 1000).until(
            #     EC.presence_of_element_located((By.CLASS_NAME, "section-result-title"))
            # )
            time.sleep(3)
            rank=0
            id=index
            index += 1
            yield SeleniumRequest(
                url=driver.current_url,
                wait_time=1000,
                screenshot=True,
                callback=self.parse_page,
                meta={'index': index,'business_name':business_name[0],'rank':rank,'business_info':business_info[id]},
                dont_filter=True
            )
        else:
            scope = ['https://www.googleapis.com/auth/documents.readonly', "https://www.googleapis.com/auth/drive.file",
                     "https://www.googleapis.com/auth/drive"]

            path = os.path.abspath(os.curdir) + "\client_secret.json"
            creds = ServiceAccountCredentials.from_json_keyfile_name(path, scope)

            DOCUMENT_ID = ''

            service = build('docs', 'v1', credentials=creds,cache_discovery=False)

            document = service.documents().get(documentId=DOCUMENT_ID).execute()

            row = length+1
            col = 2
            requests = [
                {
                    "insertTable":
                        {
                            "rows": row,
                            "columns": col,
                            "location":
                                {
                                    "index": 1
                                }
                        }
                },
            ]

            result = service.documents().batchUpdate(documentId=DOCUMENT_ID, body={'requests': requests}).execute()


            # lis = [12, 10, 7, 5]
            # arr = ['B2', 'A2', 'RANK', 'KEYWORD']
            cells = row * col
            cells = cells-2
            cells = cells // 2
            a=5
            for cell in range(2,cells+2):
                # a = a * (cell + 1)
                self.rank.append(a*cell)
                self.rank.append(a*cell+2)


            self.rank.reverse()
            self.keyword.reverse()

            print('\n'*2)
            print(self.keyword)
            print(self.rank)
            print('\n' * 2)

            for idx, l in enumerate(self.rank):
                requests = [
                    {
                        "insertText":
                            {
                                "text": self.keyword[idx],
                                "location":
                                    {
                                        "index": l
                                    }
                            }
                    }
                ]
                result = service.documents().batchUpdate(documentId=DOCUMENT_ID, body={'requests': requests}).execute()

            # lis = [12, 10, 7, 5]
            # arr = ['B2', 'A2', 'RANK', 'KEYWORD']
            # for idx, l in enumerate(lis):
            #     requests = [
            #         {
            #             "insertText":
            #                 {
            #                     "text": arr[idx],
            #                     "location":
            #                         {
            #                             "index": l
            #                         }
            #                 }
            #         }
            #     ]
            #
            #     result = service.documents().batchUpdate(documentId=DOCUMENT_ID, body={'requests': requests}).execute()
            print(result)
            print('\n'*2)
            print('finished')
            print('\n' * 2)

    def parse_page(self,response):
        driver=response.meta['driver']
        business_name=response.meta['business_name']
        business_info = response.meta['business_info']
        index = response.meta['index']
        rank=response.meta['rank']
        print('\n' * 2)
        print('scroll pages')
        print('\n' * 2)

        # details=response.xpath('//*[@id="pane"]/div/div[1]/div/div/div[4]/div[1]/div/div[1]/div[1]/div[1]/div[1]/div[2]')
        # flag=0
        # for detail in details:
        #     name=detail.xpath('.//h3/span/text()').get()
        #     print()
        #     print()
        #     print(name,business_name)
        #     print()
        #     rank += 1
        #     if(business_name == name):
        #         flag=1
        #         break


        page = 1
        flag = 0
        while(page <= 4):
            html = driver.page_source
            response_obj = Selector(text=html)
            details = response_obj.xpath('//*[@id="pane"]/div/div[1]/div/div/div[4]/div[1]/div/div[1]/div[1]/div[1]/div[1]/div[2]')

            for detail in details:
                name = detail.xpath('.//h3/span/text()').get()
                print('\n' * 2)
                print(name, business_name)
                print('\n' * 2)
                rank += 1
                if (business_name == name):
                    flag = 1
                    break
            page += 1
            if(flag==1):
                print('\n' * 2)
                print('found')
                print('\n' * 2)
                break
            try:
                next_button = driver.find_element_by_xpath('//*[@id="n7lv7yjyC35__section-pagination-button-next"]')
                next_button.click()
                time.sleep(3)
                # driver.implicitly_wait(100)
                # WebDriverWait(driver, 1000).until(
                #     EC.presence_of_element_located((By.CLASS_NAME, "section-result-title"))
                # )
            except:
                break

        if(flag==1):
            print('\n' * 2)
            print(business_name,'at rank',rank)
            self.keyword.append(business_info)
            self.keyword.append(str(rank))
            print('\n' * 2)
        else:
            self.keyword.append(business_info)
            self.keyword.append('NA')
            print('\n'*2)
            print('Not found')
            print('\n' * 2)


        yield SeleniumRequest(
            url='https://www.google.com/maps',
            wait_time=1000,
            screenshot=True,
            callback=self.parse,
            meta={'index': index},
            dont_filter=True
        )


















