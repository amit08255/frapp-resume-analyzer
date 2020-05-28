import sys
import platform
import os
import argparse
import requests
import json
import getpass
import copy
import re

LOGIN_API_URL = "https://backbone.frapp.in/brandmanager/login"
LIST_INTERNSHIP_URL = "https://backbone.frapp.in/internship"
LIST_APPLICATIONS_URL = "https://backbone.frapp.in/application"


AUTH_TOKEN_HEADER_KEY = "x-authorization-token"
AUTH_TOKEN_REQUEST_HEADER_KEY = "authorization"
CACHED_TOKEN_PATH = "./.login08255"


headers = {'content-type': 'application/json', "origin": "https://dashboard.frapp.in", "authority": "backbone.frapp.in", "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36"}

token = None
dashboardId = ""



parser = argparse.ArgumentParser(description='Parser Data')
parser.add_argument('--autologin', dest='autologin', type=str  , help="true/false(default)", required=False)

args = parser.parse_args()

def clearScreen():

    if platform.system() == 'Linux':
        os.system("clear")
    else:
        os.system("cls")

def fetchDataFromApi(apiUrl, method, requestData, requestHeader):

    try:

        if method == "get":
            req = requests.get(apiUrl,params=requestData,headers=requestHeader)
        else:
            req = requests.post(apiUrl,data=requestData,headers=requestHeader)

    except:

        req = None

    return req


def getResponseHeaders(req):
    
    if req == None:
        return None
    else:
        return req.headers


def getResponseData(req):
    
    if req == None:
        return None
    else:
        return req.text


def addTokenToHeaders(token, headers):
    newHeaders = copy.deepcopy(headers)
    newHeaders["authorization"] = "Bearer " + token
    return newHeaders


def listAllInternships():

    global dashboardId

    req = fetchDataFromApi(LIST_INTERNSHIP_URL, "get", {}, addTokenToHeaders(token, headers))

    data = getResponseData(req)

    try:
        jsonData = json.loads(data)
        dashboardId = jsonData[0]["brand"]
        return json.dumps(jsonData, indent=4)
    except Exception as e:
        print("\n\n", str(e))
        return ""


def listAllApplications(internshipId):

    global dashboardId

    req = fetchDataFromApi(LIST_APPLICATIONS_URL + "?internship=" + internshipId + "&status=applied&populate=user&where=%7B%7D&sort=%7B%22updatedAt%22:-1%7D&skip=0&limit=100", "get", {}, addTokenToHeaders(token, headers))

    data = getResponseData(req)

    try:
        jsonData = json.loads(data)
        return json.dumps(jsonData, indent=4)
    except Exception as e:
        print("\n\n", str(e))
        return ""




def analyzeSocialProfiles(profiles):

    requiredLinks = ["github.com"]
    points = 0

    try:
        for link in profiles:
            if link.url in requiredLinks:
                points += 1
    except:
        pass

    return points


def analyzeProjects(projects):

    requiredTags = ["javascript", "reactjs", "react.js", "nodejs", "node.js", "node js", "react js"]
    points = 0

    try:
        for project in projects:
            
            title = project["title"].lower()
            description = project["description"].lower()

            for tag in requiredTags:
                
                if tag in title:
                    points += 1
                    break

                if tag in description:
                    points += 1
                    break
    except:
        pass

    return points



def analyzeExperiences(experiences):

    requiredTags = ["javascript", "reactjs", "react.js", "nodejs", "node.js", "node js", "react js", "fullstack", "full-stack", "full stack", "frontend", "front-end", "front end", "web developer", "web designer"]
    points = 0

    try:
        for project in experiences:
            
            title = project["title"].lower()
            description = project["description"].lower()

            for tag in requiredTags:
                
                if tag in title:
                    points += 1
                    break

                if tag in description:
                    points += 1
                    break
    except:
        pass

    return points


def analyzeCandidate(candidateList):

    finalList = []

    for candidate in candidateList:
        
        resume = None

        try:
            resume = candidate["user"]["resume"]
        except:
            resume = None

        if resume == None:
            continue

        try:
            social = resume["sociallinks"]
        except:
            social = []
        
        try:
            projects = resume["projects"]
        except:
            projects = []
        
        try:
            experience = resume["newexperience"]
        except:
            experience = []

        user = candidate["user"]
        resumeId = candidate["id"]
        candidateName = user["firstname"] + " " + user["lastname"]
        mobile = user["mobile"]
        email = user["email"]

        socialScore = analyzeSocialProfiles(social)

        projectScore = analyzeProjects(projects)

        experienceScore = analyzeExperiences(experience)

        score = socialScore + projectScore + experienceScore

        finalList.append({"name": candidateName, "mobile": mobile, "email": email, "score": score, "experienceScore": experienceScore, "projectScore": projectScore, "socialScore": socialScore, "resumeLink": "https://dashboard.frapp.in/applicant-resume/" + resumeId + "?mission=false"})

    sortedList = sorted(finalList, key=lambda k: (k["projectScore"], k["experienceScore"], k["score"]), reverse=True)

    return sortedList



def loginUser(username, password):

    global token

    data = {"email": username, "password": password}

    req = fetchDataFromApi(LOGIN_API_URL, "post", json.dumps(data), headers)

    header = getResponseHeaders(req)

    try:
        token = header['X-Authorization-Token']

        if args.autologin == "true":
            fout = open(CACHED_TOKEN_PATH, "w")
            fout.write(token)
            fout.close()

    except Exception as e:
        print("\n\n", str(e))
        token = None


if args.autologin == "true" and os.path.exists(CACHED_TOKEN_PATH):
    fin = open(CACHED_TOKEN_PATH, "r")
    token = fin.read()
    fin.close()
else:
    emailId = input("Enter email Id: ")
    emailId = emailId.strip()
    password = getpass.getpass(prompt='Enter password: ')
    
    loginUser(emailId, password)



if token == None:
    print("\n\nFailed to get token")
    sys.exit(0)


dashboardMainScreen = '''
================================= Welcome to Frapp =======================

         1.  List Internships
         2.  List Internship applications
         3.  Analyze applications
         0.  Exit

===============================================================================
'''

option = None

while option !="0":

    clearScreen()
    print(dashboardMainScreen)
    option = input("\n\nPlease choose option: ")
    option = option.strip()

    if option == "1":
        print("\n\n", listAllInternships())

    if option == "2":
        internshipId = input("\n\nEnter internship ID: ")
        internshipId = internshipId.strip()

        print("\n\n", listAllApplications(internshipId))

    if option == "3":
        internshipId = input("\n\nEnter internship ID: ")
        internshipId = internshipId.strip()
        applications = listAllApplications(internshipId)
        applicationsJson = json.loads(applications)

        candidates = json.dumps(analyzeCandidate(applicationsJson), indent=4)

        print("\n\n", candidates)

        fout = open("candidates.txt", "w")
        fout.write(candidates)
        fout.close()

    if option != "0":
        input("\n\nPress any key to continue...")