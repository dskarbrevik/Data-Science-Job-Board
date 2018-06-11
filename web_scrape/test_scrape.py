# web scraping
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
chrome_options = Options()
chrome_options.set_headless(headless=False) # decides whether to show the chrome window while executing web search

# parsing web pages
from bs4 import BeautifulSoup

# allow for scraping many pages at once
import threading

# assortment of other libraries
import re
import time
import string
import pandas as pd
import numpy as np
import arrow
import sys


class glassdoor_scraper():

    def __init__(self, job_search_terms, location_search_terms, num_pages=1, all_pages=True):

        # main parameters of the web scrape
        self.job_search_terms = job_search_terms
        self.location_search_terms = location_search_terms
        self.num_pages = num_pages
        self.all_pages = all_pages

        assert(len(job_search_terms) == len(location_search_terms)) # has to be equal

        # for storing data
        self.all_job_pages = [] # contains all scraped HTML pages
        self.count_jobs = [] # total count of jobs from all scraper threads
        self.df_jobs = pd.DataFrame() # placeholder for a Pandas DataFrame


        # for storing threads
        self.job_threads = [] # hold job scraping threads
        self.parse_threads = [] # hold job parsing threads

        self.lock = threading.Lock() # avoid race conditions


    ###############################
    # main program calls directly #
    ###############################
    def search_jobs(self):
        for i in range(len(self.job_search_terms)):
            self.job_threads.append(threading.Thread(target=self.get_glassdoor_jobs,
                                                 args=(self.job_search_terms[i], self.location_search_terms[i])))
            time.sleep(5)
            self.job_threads[i].start()


    ###############################
    # main program calls directly #
    ###############################
    def parse_jobs(self):
        for i in range(len(self.job_search_terms)):
            self.parse_threads.append(threading.Thread(target=self.parse_glassdoor_jobs,
                                                       args=(self.all_job_pages[i],i)))
            time.sleep(5)
            self.parse_threads[i].start()

    ######################################
    # target for threads to get job data #
    ######################################
    def get_glassdoor_jobs(self, search_term, location_term):

        completed = False
        browser = webdriver.Chrome(chrome_options=chrome_options)

        while not completed:
            notification_blocked = False
            pages_searched = 0
            job_count = 0
            job_failures = 0
            job_pages = []
            page_count = 0

            # open website
            browser.get('https://www.glassdoor.com/index.htm')
            time.sleep(3)
            # Enter search parameters
            search_job = browser.find_element_by_name('sc.keyword')
            search_job.clear()
            time.sleep(2)
            search_job.send_keys(search_term)
            location = browser.find_element_by_id('LocationSearch')
            location.clear()
            time.sleep(2)
            location.send_keys(location_term)
            time.sleep(2)
            location.send_keys(Keys.RETURN)

            # get data from website
            while page_count < self.num_pages:

                pages_searched += 1

                time.sleep(3) # wait for new page to load

                try:
                    jobs = browser.find_elements_by_class_name('jl')
                except:
                    for i in range(5):
                        browser.refresh()
                        time.sleep(3)
                        print("Problem getting jobs from page.")
                        jobs = browser.find_elements_by_class_name('jl')
                        if len(jobs) > 1:
                            break;
                    else:
                        print("{0} - {1}: Couldn't find any more jobs on page.".format(search_term, location_term))
                        completed = True
                        break;

                ##########################################################################################################################
                # make sure you have the right search result
                no_keyword = False
                first_write = True
                for i in range(5):
                    try:
                        keyword = browser.find_element_by_name('sc.keyword').get_attribute('value')
                        if first_write:
                            first_write = False
                            with self.lock:
                                with open('./test.txt', 'a') as file:
                                    file.write("{0} - {1}: '{2}'".format(search_term, location_term, keyword))
                                    file.write("\n")
                        if (keyword.lower() == search_term.lower()):
                            break;
                        if (keyword.lower() in ['', ' ']):
                            print("{0} - {1}: keyword = '{2}'  (empty)... checking again.".format(search_term, location_term, keyword))
                            break;
                        else:
                            browser.refresh()
                            time.sleep(3)
                    except:
                        print("{0} - {1}: couldn't find keyword".format(search_term, location_term))
                        if first_write:
                            first_write = False
                            with self.lock:
                                with open('./test.txt', 'a') as file:
                                    file.write("{0} - {1}: '{2}'".format(search_term, location_term, keyword))
                                    file.write("\n")
                        time.sleep(1)
                        if i > 3:
                            no_keyword = True
                        if job_count >= 30:
                            print("no more keyword and job_count over 30!")
                            completed = True
                else:
                    if no_keyword:
                        print("{0} - {1}: No keyword found... restarting.".format(search_term, location_term))
                    else:
                        print("Wrong search term: {0} instead of {1}... restarting.".format(keyword, search_term))
                    break;
               ############################################################################################################################

                # get all jobs in a single page
                for job in jobs:
                    if not notification_blocked:
                        try:
                            wait(browser, 3)
                            close_button = browser.find_element_by_class_name('mfp-close')
                            close_button.click()
                            notification_blocked = True
                        except:
                            pass
                    try:
                        job.click()
                        job_count += 1
                    except:
                        print("Problem clicking on job.")
                        job_failures += 1

                    time.sleep(5) # wait for job description to load

                    try:
                        job_pages.append(browser.page_source) # data collection step
                    except:
                        print("Problem appending page source.")

                    time.sleep(2)

                if pages_searched % 10 == 0:
                    print("{0} - {1}: mined {2} jobs".format(search_term, location_term, job_count))

                if not self.all_pages:
                    page_count += 1

                # get the next page of search results
                for i in range(5):
                    try:
                        if browser.find_element_by_class_name('next').find_element_by_class_name('disabled'):
                            print("found disabled button")
                            browser.refresh()
                            time.sleep(3)
                    except:
                        pass

                    try:
                        next_page = browser.find_element_by_class_name('next')
                        next_page.click()
                        break;
                    except:
                        print("Problem getting next page")
                        time.sleep(2)

                else:
                    print("got to bottom completed clause!")
                    completed = True
                    break;

        browser.quit()

        with self.lock:
            self.count_jobs.append(job_count)
            self.all_job_pages.append(job_pages)
            title = "{} - {} | status: ENDED".format(search_term, location_term)
            print(title)
            print("="*len(title))
            print("Number of pages searched = {}".format(pages_searched))
            print("Number of jobs mined = {}".format(job_count))
            print("Number of failed job clicks = {}".format(job_failures))
            print("\n")

    ##########################
    # target for job parsing #
    ##########################
    def parse_glassdoor_jobs(self, job_pages, index):

        data_dict = {"company":[], "position":[], "location":[], "link":[], "description":[]}
        count = 0
        # get some data from scraped web pages
        for job in job_pages:

            soup = BeautifulSoup(job, 'html.parser')

            try:
                link = soup.find('div', class_="regToApplyArrowBoxContainer").find('a', href=True)['href']
                data_dict["link"].append("https://www.glassdoor.com{}".format(link))
            except:
                data_dict["link"].append("N/A")

            try:
                location = soup.find('div', class_="padLt padBot").findAll('span')
                if len(location) == 4:
                    data_dict["location"].append(location[3].text.split(' ' + chr(8211) + ' ')[1].strip())
                elif len(location) == 1:
                    data_dict["location"].append(location[0].text.split(' ' + chr(8211) + ' ')[1].strip())
            except:
                data_dict["location"].append("N/A")

            try:
                company = soup.find('a', class_="plain strong empDetailsLink")
                data_dict["company"].append(company.text.strip())
            except:
                data_dict["company"].append("N/A")

            try:
                position = soup.find('h1', class_="noMargTop noMargBot strong")
                data_dict["position"].append(position.text.strip())
            except:
                data_dict["position"].append("N/A")

            try:
                description = soup.find('div', id='JobDescriptionContainer')
                data_dict["description"].append(description.text.strip())
            except:
                data_dict["description"].append("N/A")

            count += 1

            if count % int(len(job_pages)/4) == 0:
                print("{0} - {1}: currently parsing job {2}".format(self.job_search_terms[index],
                                                                    self.location_search_terms[index], count))

        # package into DataFrame object
        df_tmp = pd.DataFrame.from_dict(data_dict)

        # reorder columns in more logical way
        old_cols = df_tmp.columns.tolist()
        new_cols = ['position', 'company', 'location', 'description', 'link']
        if set(old_cols) == set(new_cols):
            df_tmp = df_tmp[new_cols]

        with self.lock:
            self.df_jobs = self.df_jobs.append(df_tmp, ignore_index=True)

        print("dataframe has been appended.")

    ###############################
    # main program calls directly #
    ###############################
    def save_jobs(self, save_location="../data/test_scrapes/glassdoor-df-{}.csv".format(arrow.now().format('MM-DD-YYYY'))):
        if not self.df_jobs.empty:
            self.df_jobs.to_csv(save_location, index=False)
            print("Jobs data saved to {}.".format(save_location))
        else:
            print("Jobs DataFrame was empty and thus not saved to file.")



if __name__ == '__main__':

    job_terms = ['Data Scientist', 'Data Analyst']
    location_terms = ['California', 'United States']

    # if not sys.argv[1]:
    #     raise Exception('Need to provide a text file of search terms to scrape from. See documentation for details.')
    #
    # # get search parameters from file
    # try:
    #     with open(sys.argv[1]) as file:
    #         job_searches = file.readlines()
    #
    #         for job_search in job_searches:
    #             keywords = job_search.split("-")
    #             job_terms.append(keywords[0].strip())
    #             location_terms.append(keywords[1].strip())
    # except:
    #     print("Issue reading {}. Be sure path is correct and format is correct. See documentation for details.".format(sys.argv[1]))


    scraper = glassdoor_scraper(job_search_terms=job_terms, location_search_terms=location_terms)

    # get job data from glassdoor



    scraper.search_jobs()
    for thread in scraper.job_threads:
        thread.join()

    # parse job data into Pandas DataFrame
    scraper.parse_jobs()
    for thread in scraper.parse_threads:
        thread.join()

    print("\n")
    print("Total of {} jobs scraped.".format(np.sum(scraper.count_jobs)))


    # save DataFrame to file
    scraper.save_jobs()

    print("\n")
    print("JOB SCRAPE IS COMPLETE!")
