import urllib2
import urllib
import re
import os
import datetime


def getMatchIDs(eventid):
    # Create an offset varibale for lists that are paginated on HLTV
    offset = 0
    # Get the HTML using getHTML()
    html = getHTML('https://www.hltv.org/results?offset=%s&event=%s' % (offset, eventid))
    # Create an array of all of the Demo URLs on the page
    matchIDs = re.findall('"(.*?000"><a href="/matches/.*?)"', html)
    # Loops trhrough the messy array and removes the pesky parts
    for i in range(0, len(matchIDs)):
        matchIDs[i] = matchIDs[i].split('/', 2)[-1]
    # If the length is = 25, offset by 25 and loop again
    if len(matchIDs) == 50:
        print "Parsed first page. Found %s IDs" % (len(matchIDs))
        # Set a boolean to close the while loop and a page variable we can increment when paginating
        morePages = True
        page = 1
        # While check is true, offset by 50
        while morePages:
            offset += 50
            # Same URL building and parsing as above
            url = 'https://www.hltv.org/results?offset=%s&event=%s' % (offset, eventid)
            html = getHTML(url)
            moreMatchIDs = re.findall('"(.*?000"><a href="/matches/.*?)"', html)
            for i in range(0, len(moreMatchIDs)):
                moreMatchIDs[i] = moreMatchIDs[i].split('/', 2)[-1]
                # Appends the new IDs to the master list
                matchIDs.append(moreMatchIDs[i])
            # Determine if there are additional page to be found, if not the while loop ends
            if len(moreMatchIDs) < 50:
                morePages = False
                page += 1
                print "Parsed page %s. Found %s IDs." % (page, len(matchIDs))
            else:
                # Prints the current page and the number of parsed IDs
                page += 1
                print "Parsed page %s. %s IDs found so far." % (page, len(matchIDs))
    elif len(matchIDs) < 50:
        print "Total demos: %s" % len(matchIDs)
    elif len(matchIDs) > 50:
        print "HLTV altered demo page layout :("
    return matchIDs


def getDemoIDs(matchIDs):
    # Tell ths user what is happening
    print "Converting Match IDs to Demo IDs"
    # Define the array of Demo IDs
    demoIDs = []
    # Create an array for Match IDs with no Demo ID
    noDemos = []
    # Create a variable to count the number of remaining Match IDs
    counter = 0
    # Loops through the array of Match IDs and gets the respective Demo IDs
    for i in range(0, len(matchIDs)):
        # Same URL building and opening as above
        html = getHTML("https://www.hltv.org/matches/%s" % (matchIDs[i]))
        demoID = re.findall('"(/download/demo/.*?)"', html)
        # Check if re.findall()'s array is empty
        # If it has an element, add that Demo ID to the demoIDs array
        if len(demoID) > 0:
            demoIDs.append(demoID[0])
        # If there is no element, print which match has no demo
        elif len(demoID) < 1:
            print "No demo found for %s (%s)" % (len(matchIDs)-counter, matchIDs[i].rsplit('/', 1)[-1])
            noDemos.append(matchIDs[i])
        # Update counter and tell the user the conversion status is
        counter += 1
        print "%s remaining to convert." % (len(matchIDs)-counter)
    # Loop through the demoIDs array and remove everything up to the last / to get the real Demo ID
    for i in range(0, len(demoIDs)):
        demoIDs[i] = demoIDs[i].rsplit('/', 1)[-1]
    # If there are errors, print them
    printErrors(noDemos)
    return demoIDs


def download(demoIDs):
    # Tell the user how many demo files will be downloaded
    print "%s demo files to retrieve." % (len(demoIDs))
    # Create a counter varibale
    counter = 0
    # Make a folder for the files to be stored in.
    # TODO eventName = raw_input("What is the event name? ")
    eventName = "Test Event - %s" % (datetime.datetime.now().time())
    directory = "./%s" % (eventName)
    os.mkdir(directory)
    # Create an array to calculate the total data transferred
    filesizes = []
    # Parse through the array of Demo IDs
    for i in range(0, len(demoIDs)):
        # Build and open the URL
        opener = urllib2.build_opener()
        opener.addheaders = [('User-Agent', 'Mozilla/5.0')]
        response = opener.open("https://www.hltv.org/download/demo/%s" % (demoIDs[i]))
        # HLTV redicrects to a .rar or .zip file
        finalurl = response.geturl()
        # Gets the filename (everything after the last trailing /)
        filename = finalurl.rsplit('/', 1)[-1]
        # Gets the Content-Length from the metadata from finalurl in bytes and convert to MB
        filesize = (int(urllib.urlopen(finalurl).info().getheaders("Content-Length")[0])/1024)/1024
        # Append the filesize to the array of filesizes
        filesizes.append(filesize)
        # Downloads the file to the directory the user enters
        urllib.urlretrieve(finalurl, directory+"/"+filename)
        counter += 1
        # Tell user the current status and file information
        print "%s demos remaining. Completed %s: %s MB." % (len(demoIDs)-counter, filename, filesize)
    print "Total data transferred: %s. Enjoy!" % (totalData(filesizes))
    return True


def totalData(filesizes):
    filesizes = filesizes
    # Create a variable to add the filesizes to when looping
    data = 0
    for i in range(0, len(filesizes)):
        data += int(filesizes[i])
    # If the data varibale is larger than 1 GB, divide it and store as a float
    if data > 1024:
        data = "%.2f GB" % (float(data) / 1024)
    # If the data variable is smaller than 1 GB, do nothing
    else:
        data = "%s MB" % (data)
    return data


def getHTML(url):
    # Get the variable passed as an argument so it can be used
    url = url
    # Open the URL
    opener = urllib2.build_opener()
    # Spoof the user agent
    opener.addheaders = [('User-Agent', 'Mozilla/5.0')]
    response = opener.open(url)
    # Read the response as HTML
    html = response.read()
    return html


def printErrors(errors):
    errors = errors
    if len(errors) == 1:
        print "%s match has no demo:" % (len(errors))
        # Reset counter varibale to count the errors
        counter = 1
        # Loop through the array of matches with no demos.
        for i in range(0, len(errors)):
            # Print URLs for the matches with no demo file
            print "%s: https://www.hltv.org/matches/%s" % (counter, errors[i])
            counter += 1
    elif len(errors) > 0:
        print "%s matches have no demo:" % (len(errors))
        # Reset counter varibale to count the errors
        counter = 1
        # Loop through the array of matches with no demos.
        for i in range(0, len(errors)):
            # Print URLs for the matches with no demo file
            print "%s: https://www.hltv.org/matches/%s" % (counter, errors[i])
            counter += 1
    else:
        print "No errors found!"
    return True


# Calls the method for a given Event ID.
# TODO eventID = raw_input("What is the event ID? ")
eventID = 2854
matchIDs = getMatchIDs(eventID)
demoIDs = getDemoIDs(matchIDs)
download(demoIDs)
