import requests
import re
import sys
from bs4 import BeautifulSoup
from csv import writer


def getFileName():
    # Get name of file to write to
    while True:
        csvName = input("Please enter filename to write to: ")
        if csvName.endswith(".csv"):
            break
        else:
            print("Please enter a valid file name. Example : rentals.csv")

    return csvName


def getURL():
    # Get URL to scrape from user
    while True:
        url = input("Please enter the Kijiji URL for your search : ")

        # Regex to parse input URL and extract the search query
        matches = re.search(r"^(https?://)?(www\.)?kijiji\.ca(.+)$", url, re.IGNORECASE)
        if matches:  # If URL is a kijiji URL
            query = matches.group(3)
            break
        else:
            print(
                "Please enter a valid URL. \nExample : https://www.kijiji.ca/b-apartments-condos/city-of-toronto/c37l1700273"
            )
    return query


def createCSV(filename):
    # Create .csv file and add headers
    with open(filename, "w", encoding="utf8", newline="") as file:
        csv_writer = writer(file)
        header = ["Title", "Location", "Price", "Date", "URL"]
        csv_writer.writerow(header)


def parseApartments(soup, csvName):
    try:
        # Get apartment information
        apartmentInfo = soup.find_all("div", class_="info-container")

        # Write apartment information to CSV file
        with open(csvName, "a", encoding="utf8", newline="") as file:
            csv_writer = writer(file)
            for apartment in apartmentInfo:
                title = apartment.find("div", class_="title").text.strip()
                price = apartment.find("div", class_="price").text.strip()
                date = apartment.find("span", class_="date-posted").text.strip()
                location = apartment.find("span").text.strip()
                url = kijiji + (apartment.find("a")).get("href")
                information = [title, location, price, date, url]
                csv_writer.writerow(information)
    except:
        print("Parsing failed")


# Get the URL to scrape and name of CSV to write to
kijiji = "https://www.kijiji.ca"
query = getURL()
searchURL = kijiji + query
csvName = getFileName()

# Request page. Exit if request is not status 200.
page = requests.get(searchURL)
if page.status_code != 200:
    print(page)
    sys.exit("Double check URL provided")

# Create CSV file to write results to
createCSV(csvName)

# Scrape all pages
while True:
    # Create HTML Parser with BeautifulSoup and scrape for information
    soup = BeautifulSoup(page.content, "html.parser")
    print(f"(Scraping : {searchURL}")
    parseApartments(soup, csvName)

    # Check to see if there's more pages to scrape
    navigationInfo = soup.find_all("div", class_="pagination")

    try:
        # Get next URL
        for element in navigationInfo:
            searchURL = kijiji + element.find("a", title="Next").get("href")
        # Request next page
        page = requests.get(searchURL)

    except:
        # No next button; job done
        break

print(f"All pages scraped. Results sent to {csvName}")
