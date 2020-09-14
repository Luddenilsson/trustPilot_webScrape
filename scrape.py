import requests
from requests import get
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import json
import time
import re

from time import sleep
from random import randint

# Not needed but I like a timer to see how long the code takes to run
then = time.time()

# Create empty lists to hold data
reviews = []
headings = []
stars = []
dates = []

lang = "sv"
# Set number of pages to scrape, you need to check on TrustPilot to see how many to scrape
# in this instance at the time of coding there were 287 pages to be scraped
# The first number 1 means start at 1, the number 287 means stop at 287
# the third number which is 1 means go from 1 to 287 in steps of 1
webPageList = ["https://se.trustpilot.com/review/telness.se", "https://se.trustpilot.com/review/hifi-punkten.se",
               "https://se.trustpilot.com/review/www.fyndborsen.se","https://se.trustpilot.com/review/www.cdon.se",
               "https://se.trustpilot.com/review/oljemagasinet.se","https://se.trustpilot.com/review/filmhyllan.nu?languages=sv",
               "https://se.trustpilot.com/review/petworld.se","https://se.trustpilot.com/review/hm.com",
               "https://se.trustpilot.com/review/www.spotify.com","https://se.trustpilot.com/review/verisure.se",
               "https://se.trustpilot.com/review/www.vvsochbad.se","https://se.trustpilot.com/review/vinoteket.se",
               "https://se.trustpilot.com/review/www.inkclub.com","https://se.trustpilot.com/review/teknikdelar.se",
               "https://se.trustpilot.com/review/fyndiq.se","https://se.trustpilot.com/review/advisa.se",
               "https://se.trustpilot.com/review/www.tele2.se","https://se.trustpilot.com/review/www.comhem.se",
               "https://se.trustpilot.com/review/bodylab.se","https://se.trustpilot.com/review/www.solfaktor.se",
               "https://se.trustpilot.com/review/tui.se","https://se.trustpilot.com/review/www.flygpoolen.se",
               "https://se.trustpilot.com/review/www.ticket.se"]

for webPageName in webPageList:
    webPage =requests.get(webPageName)
    soup = BeautifulSoup(webPage.text, "html.parser")
    numRev = soup.find('div', class_="reviews-overview card card--related")
    temp = numRev.script.contents[0]
    svPos = temp.find(lang)
    svRev_str = temp[(svPos+43):(svPos+50)]
    svRev = re.findall(r'\d+', svRev_str)
    if len(svRev)>1:
        svRev = int(svRev[0]+svRev[1])
    else:
        svRev = int(svRev[0])
    numPages = int(svRev/20)+1
    pages = np.arange(1, numPages, 1)

    # Create a loop to go over the reviews
    for page in pages:
        page = requests.get(webPageName + "?languages=" + lang + "&page=" + str(page))

        soup = BeautifulSoup(page.text, "html.parser")

        # Set the tag we wish to start at, this is like a parent tag where we will go in and get everything below it
        review_div = soup.find_all('div', class_="review-content")

        # Sleep is not needed but many websites will ban scraping so a random timer helps get by this
        # by using sleep we tell the code to stop between 2 and 10 seconds so it will slow the code execution down
        sleep(randint(1, 4)/100)

        # loop to iterate through each reviews
        for container in review_div:
            # Get the body of the review
            # If there is no review left by the user we will get a "-" returned by using 'if len(nv) == True else '-''
            # TrustPilot will add nothing if there is no review so there will be no tag for the code to scrape
            # It is saying if nv is True (we have a review) return the review or just put a - in
            # We now tell the code to go into the tag  'p' 'class' 'review-content__text'
            nv = container.find_all('p', attrs={'class': 'review-content__text'})
            review = container.p.text if len(nv) == True else '-'
            reviews.append(review)

            # Get the title of the review
            nv1 = container.find_all('h2', attrs={'class': 'review-content__title'})
            heading = container.a.text if len(nv1) == True else '-'
            headings.append(heading)

            # Get the star rating review given
            star = container.find("div", {"class": "star-rating star-rating--medium"}).find('img').get('alt')
            stars.append(star)

            # Get the date
      #      cont = container.find('script', {"data-initial-state": "review-dates"}).text
       #     date_json = json.loads(container.find('script').text)
        #    date = date_json['publishedDate']
         #   dates.append(date)

# Cleaning up the data, this could be done in code but I saved it to a .csv and opened it back up
# Create a DataFrame using the lists we created
TrustPilot = pd.DataFrame({'Title': headings, 'Body': reviews, 'Rating': stars})
# The review had a lot of white space on both sides so we strip that out and create a .csv with the data
TrustPilot['Body'] = TrustPilot['Body'].str.strip()
TrustPilot.to_csv('TrustPilot.csv', index=False)

# Read the csv file
data = pd.read_csv('TrustPilot.csv')

# The date is returned with date and time in same cell, we split this into 2 new columns with seperate date and time columns
#new = data["Date"].str.split("T", n=1, expand=True)
#data["Date Posted"] = new[0]
#data["Time Posted"] = new[1]
#data.drop(columns=["Date"], inplace=True)
new = data["Rating"].str.split(":", n=1, expand=True)

# Do what we done with date to stars
data["Stars"] = new[0]
data["Rated"] = new[1]
data.drop(columns=["Rating"], inplace=True)
#data['Time Posted'] = data['Time Posted'].map(lambda x: str(x)[:-4])
data['Stars'] = data['Stars'].map(lambda x: str(x)[0:1])

# Arrange the columns order and save it as a csv
data = data[['Title', 'Body', 'Stars']]
data.to_csv('TrustPilot.csv', index=False)

# Show how long the code took to complete
now = time.time()
print("It took: ", now - then, "seconds")
mins = now - then
minute = 60
totalMins = mins / minute
totalMinsRound = round(totalMins, 2)
print("It took: ", totalMinsRound, "minutes and seconds")
