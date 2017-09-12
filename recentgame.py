import urllib.request
import datetime
import requests
from bs4 import BeautifulSoup
from contextlib import closing
from selenium.webdriver import Firefox
from selenium.webdriver.support.ui import WebDriverWait

TEAM_NAME = "Cardinals"

# Google search query that gets the little score popup
searchURL = "https://www.google.com/search?q=last+" + TEAM_NAME + "+game"

# have to pretend to be a real person or the popup will not be created by google
headers = {}
headers['User-Agent'] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36"

# retrieving html for google popup
req = urllib.request.Request(searchURL, headers=headers)
resp = urllib.request.urlopen(req)
respData = resp.read()
soup = BeautifulSoup(respData, "html.parser")

# finding link to mlb.com inside of popup html
boxscoreURL = soup.find(class_="fl osl")['href']


# mlb.com page data is generated by javascript. So a browser must be emulated in order
# to get the html data after javascript execution. Requires installation of Firefox on machine
# as well as geckodriver.exe inside the project directory

with closing(Firefox()) as browser:
    browser.get(boxscoreURL)

    WebDriverWait(browser, timeout=10).until(
        lambda x: x.find_element_by_id('text_matchup'))

    page_source = browser.page_source

# finding game results in mlb.com html
soup = BeautifulSoup(page_source, "html.parser")
score = soup.find(id="text_matchup")

#print("The most recent " + TEAM_NAME + " game result is:")
#print(score.find(class_="header").text, "ON", score.find(class_="date").text)
#print("Today is: " + now.strftime("%A, %B %d, %Y"))

now = datetime.datetime.now()

msg = "The most recent " + TEAM_NAME + " game result is:\n" + \
      score.find(class_="header").text + " ON " + score.find(class_="date").text + \
      "\nToday is: " + now.strftime("%A, %B %d, %Y")
scoreline = score.find(class_="header").text
teamscore = scoreline[scoreline.find(TEAM_NAME)+len(TEAM_NAME)+1:scoreline.find(TEAM_NAME)+len(TEAM_NAME)+2]

# Creating data to be sent in post request to groupme bot.

data = {
    'bot_id': "6a81587ced0e54086293c231e8",
    'text': msg
}

r = requests.post("https://api.groupme.com/v3/bots/post", data=data)
