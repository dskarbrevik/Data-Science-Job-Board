import pandas as pd
import numpy as np
import arrow
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.util import ngrams
import re
from collections import Counter
import string
import time
import sys


class process_raw_scrape():

    def __init__(self, old_df, df_new):

        self.df_new = df_new
        self.df_old = old_df
        self.archive_df = pd.DataFrame()

        # used for ranking system and plotting data
        self.locations_of_interest = ['ca', 'co', 'hi', 'me', 'mi', 'ny', 'oh', 'or', 'tx', 'wa'] # +2
        self.words_of_interest = ['data'] # +1
        self.filter_words = ['senior', 'sr.', 'sr', 'director', 'manager', 'research', 'architect'] # -1
        self.good_words = "python|data science|data scientist|quantitative|analytical"
        self.data_science_words = ['python','sql','r','hadoop','spark','d3.js','hive','matlab','excel',
                                  'nosql','aws','c','java','javascript','php','scala','tableau','cassandra',
                                  'etl','javascript','mahout','redis','redshift','machine learning','deep learning',
                                  'tensorflow','keras','matplotlib','Ruby','Pig','mongodb','mysql','pandas',
                                  'numpy','scipy','linux','windows', 'postgres', 'statistics', 'statistical analysis',
                                  'rapidminer', 'talend', 'oracle', 'sql server', 'regression', 'time series', 'forecast',
                                  'classification', 'prediction', 'c++', 'julia', 'scala']


    # DONE #
    def combine_dfs(self):

        start = time.time()

        print("Removing duplicates from today's web scrape.")
        #prepare df_new
        dups = self.df_new.duplicated(subset=['position','company','location','description'])
        self.df_new = self.df_new[~dups]

        print("Merging today's web scrape with yesterday's.")
        # full outer join on old and new df (and get rid of duplicate columns)
        self.df_new = self.df_new.merge(self.df_old, on=['company','position','location','description'], how="outer", indicator=True)
        self.df_new = self.df_new.drop(columns=['link_x'])
        self.df_new = self.df_new.rename(columns= {'link_y':'link'})
        self.df_new.loc[self.df_new['strikes'].isnull(), 'strikes'] = 0

        # mark any aging jobs (but don't remove just yet)
        self.df_new.loc[self.df_new['_merge']=='right_only', 'strikes'] += 1

        # save old jobs to archive
        self.archive_df = self.df_new[self.df_new['strikes'] >= 3]
        if not self.archive_df.empty:
            self.df_new = self.df_new.drop(self.archive_df.index)
            self.archive_df.to_csv("../data/scrapes/archived_scrapes/glassdoor-df-{}.csv".format(arrow.now().format('MM-DD-YYYY')).csv,
                                   index=False)
        else:
            print("No jobs old enough to archive today.")

        # drop jobs if missing link or description
        self.df_new = self.df_new[~self.df_new['link'].isnull()]
        self.df_new = self.df_new[~self.df_new['description'].isnull()]

        # position
        self.df_new.loc[self.df_new['position'].isnull(), 'position'] = 'none'

        # location
        self.df_new.loc[self.df_new['location'].isnull(), 'location'] = 'none'

        # days_posted
        self.df_new.loc[self.df_new['_merge']=='both', 'days_posted'] += 1
        self.df_new.loc[self.df_new['days_posted'].isnull(), 'days_posted'] = 0

        # date_posted
        self.df_new.loc[self.df_new['date_posted'].isnull(), 'date_posted'] = arrow.now().format('MM-DD-YYYY')

        # applied
        self.df_new.loc[self.df_new['applied'].isnull(), 'applied'] = "No"

        # rank
        self.df_new.loc[self.df_new['rank'].isnull(), 'rank'] = 0

        # drop merge
        self.df_new = self.df_new.drop(columns=['_merge'])

        save_location = "../data/scrapes/cleaned_scrapes/glassdoor-df-{}.csv".format(arrow.now().format('MM-DD-YYYY'))
        self.df_new.to_csv(save_location, index=False)
        print("Cleaned web scrape saved to {}".format(save_location))

        end = time.time()

        print("Merging dataframes complete!")
        print("Total time: {:.2f}".format((end-start)/60))
        print("\n")

    # DONE #
    def filter_by_location(self):

        locations = self.df_new['location'].tolist()
        ranks = [0]*len(locations)

        for i,location in enumerate(locations):
            try:
                if location == 'Remote':
                    ranks[i] += 3
                    continue;
                state = location.split(',')[1].strip()
                if state.lower() in self.locations_of_interest:
                    ranks[i] += 3
            except:
                pass

        self.df_new['rank'] += ranks

    # DONE #
    def filter_by_position_title(self):

        jobs = self.df_new['position'].tolist()
        ranks = [0]*len(jobs)

        for i,job in enumerate(jobs):

            job = job.lower()

            if job == 'none':
                ranks[i] += -1

            if (re.search("scientist", job)) and not (re.search("data", job)):
                ranks[i] += -3

            first_plus = True
            first_minus = True

            job_words = job.split(" ")
            for word in job_words:
                if (first_plus) and (word in self.words_of_interest):
                    first_plus = False
                    ranks[i] += 1
                elif (first_minus) and (word in self.filter_words):
                    first_minus = False
                    ranks[i] += -1


        self.df_new['rank'] += ranks

    # DONE #
    def filter_by_description(self):

        try:
            descriptions = self.df_new['description'].tolist()
            ranks = [0]*len(descriptions)
        except:
            print("Problem extracting description info for some reason...")

        for i,description in enumerate(descriptions):
            try:
                lowered = description.lower()
            except Exception as inst:
                print("description not a string??")
                print(type(inst))
                print(inst)

            try:
                bachelor = True if re.search("bachelor|b\.?s\.?", lowered) else False
                master = True if re.search("master|ms|m\.s\.|ms\.", lowered) else False
                phd = True if re.search("doctorate|p\.?h\.?d\.?", lowered) else False
                experience_2 = True if re.search("2\+?year[s]?", lowered) else False
                experience_5 = True if re.search("5\+?year[s]?", lowered) else False
                experience_10 = True if re.search("10\+?year[s]?", lowered) else False
                good_words = True if re.search(self.good_words, lowered) else False
            except Exception as inst:
                print("Problem getting true false re search results.")
                print(type(inst))
                print(inst)

            try:
                if (experience_5 and phd) or (phd and not master) or (experience_10):
                    ranks[i] += -2
                elif (experience_2 and not phd and not master) or (experience_5 and not phd):
                    ranks[i] += -1
                elif (master and not phd and not experience_10) or (bachelor):
                    ranks[i] += 2
                if good_words:
                    ranks[i] += 2
            except Exception as inst:
                print("problem assigning ranks.")
                print(type(inst))
                print(inst)


        self.df_new['rank'] += ranks

    # DONE #
    def save_top_jobs(self):

        start = time.time()

        print("Beginning extraction of top job title data.")
        top_jobs = Counter(self.df_new['position'].tolist()).most_common(100)

        save_location = '../data/app_data/current_plot_data/top-jobs-{}.txt'.format(arrow.now().format('MM-DD-YYYY'))
        with open(save_location, 'w') as file:
            for job in top_jobs:
                if isinstance(job[0], float):
                    continue;
                elif (len(job[0]) > 45):
                    continue;
                elif job[0] == 'none':
                    continue;
                else:
                    file.write('{0};{1}'.format(job[0], job[1]))
                    file.write('\n')

        end = time.time()
        print("Finished parsing top jobs. Saved to {}".format(save_location))
        print("Total time: {:.2f} minutes.".format((end-start)/60))
        print("\n")

    # DONE #
    def save_top_terms(self):

        start = time.time()

        print("Beginning to parse descriptions for top terms.")
        descriptions = self.df_new['description'].tolist()
        stop_words = set(stopwords.words('english'))
        common_terms = []

        for description in descriptions:

            try:
                if not isinstance(description, str):
                    continue;

                words = description.strip().replace('\n', ' ').translate(string.punctuation) # strip down to words
                words = re.sub(r'[^\w\s]', '', words)
                words = words.lower()

                tokens = word_tokenize(words)
                tokens = [word for word in tokens if not word in stop_words]

                unigrams = list(ngrams(tokens, 1))
                bigrams = list(ngrams(tokens, 2))
                trigrams = list(ngrams(tokens, 3))
            except Exception as inst:
                print("problem getting ngrams")
                print(inst)
                print(type(inst))

            try:

                for unigram in unigrams:
                    common_terms.append(unigram[0])
                for bigram in bigrams:
                    common_terms.append("{0} {1}".format(bigram[0], bigram[1]))
                for trigram in trigrams:
                    common_terms.append("{0} {1} {2}".format(trigram[0], trigram[1], trigram[2]))
            except Exception as inst:
                print("problem compiling ngrams.")
                print(inst)
                print(type(inst))


        top_terms = Counter(common_terms).most_common()

        top_target_terms = []

        for top_term in top_terms:
            if top_term[0] in self.data_science_words:
                top_target_terms.append((top_term[0],top_term[1]))


        save_location = "../data/app_data/current_plot_data/top-terms-{}.txt".format(arrow.now().format('MM-DD-YYYY'))
        with open(save_location, 'w') as file:
            for word in top_target_terms:
                try:
                    file.write("{0};{1}".format(word[0], word[1]))
                    file.write("\n")
                except:
                    print("Couldn't write top term: '{0}' ({1}) to file".format(word[0], type(word[0])))
        end = time.time()
        print("Finished parsing top terms. Saved to {}".format(save_location))
        print("Total time: {:.2f} minutes".format((end-start)/60))
        print("\n")

    # DONE #
    def save_df(self):

        # save cleaned_scrape to disk
        self.df_new.to_csv("../data/scrapes/clean_filtered_scrapes/glassdoor-df-{}.csv".format(arrow.now().format('MM-DD-YYYY')), index=False)
        print("Saved cleaned and filtered web scrape.")

        # save cleaned_scrape without descriptions for app upload
        jobs_for_app = self.df_new.drop('description', axis=1)
        jobs_for_app = jobs_for_app.sort_values(by=['rank'], ascending=False)
        jobs_for_app = jobs_for_app.iloc[:100]
        jobs_for_app.to_csv("../data/app_data/jobs-for-app.csv", index=False)
        print("Saved jobs for web app.")


# main program to run from terminal/command-line
if __name__ == '__main__':

    # get today's and yesterday's web scrapes ready
    old_df = pd.read_csv("../data/scrapes/cleaned_scrapes/glassdoor-df-06-06-2018.csv",
                         encoding="ISO-8859-1")
    new_df = pd.read_csv("../data/scrapes/raw_scrapes/glassdoor-df-06-08-2018.csv",
                         encoding="ISO-8859-1")


    ######################################
    # STEP 1: initialize processor class #
    ######################################
    try:
        job_processor = process_raw_scrape(old_df, new_df)
    except:
        print("Issue initializing processor class. Shutting down.")
        sys.exit()


    ######################################
    # STEP 2: compare yesterday to today #
    ######################################
    try:
        job_processor.combine_dfs()
    except:
        print("Issue in combine_dfs(). Shutting down.")
        sys.exit()


    ###################################################
    # STEP 3: set rankings and remove irrelevant jobs #
    ###################################################
    try:
        job_processor.filter_by_location()
    except:
        print("Issue in filter_by_location(). Shutting down.")
        sys.exit()
    try:
        job_processor.filter_by_position_title()
    except:
        print("Issue in filter_by_position_title(). Shutting down.")
        sys.exit()
    try:
        job_processor.filter_by_description()
    except:
        print("Issue in filter_by_description(). Shutting down.")
        sys.exit()


    #########################
    # STEP 4: get plot data #
    #########################
    try:
        job_processor.save_top_jobs()
    except:
        print("Issue in save_top_jobs(). Shutting down.")
        sys.exit()

    try:
        job_processor.save_top_terms()
    except:
        print("Issue in save_top_terms(). Shutting down.")
        sys.exit()


    ###########################
    # STEP 5: save cleaned df #
    ###########################
    try:
        job_processor.save_df()
    except:
        print("Issue in save_df(). Shutting down.")
        sys.exit()

    # we made it to the end!
    print("RAW WEB SCRAPE FULLY PROCESSED!")
