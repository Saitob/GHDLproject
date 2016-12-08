#!/usr/bin/python
# coding=utf-8

#Used to handle command-line arguments
import sys, argparse, getopt, subprocess
from subprocess import Popen, PIPE, STDOUT
#Regular expressions
import re
#Gives access to sleep command
import time
#For checking files and directories
import os
#Part of PyGithub, used for API communication
from github import Github
from github import GithubException
from github import BadCredentialsException
from github import RateLimitExceededException
from github import BadAttributeException
#Used for ceil rounding
import math
#For getting todays date
import datetime

# Prints repository datafields to screen. Takes a repository object, not a full page
# Fields to print are: Name, Description, Owner, created at, updated at, size(MB), programming language
def printRepoToScreen(repo):
    
    print("Name:")
    try:
        print(repo.name)
    except:
        print(">>Error printing field data.<<")
                    
    print("Description:")
    try:
        print(repo.description)
    except:
        print(">>Error printing field data.<<")

    print("Owner:")
    try:
        print(repo.owner.login)
    except:
        print(">>Error printing field data.<<")
                                
    print("Created:")
    try:
        print(repo.created_at)
    except:
        print(">>Error printing field data.<<")
                    
    print("Last updated:")
    try:
        print(repo.updated_at)
    except:
        print(">>Error printing field data.<<")

    print("Size:")
    try:
        print(round(repo.size/1000), "MB")
    except:
        print(">>Error printing field data.<<")

    print("Programming language:")
    try:
        print(repo.language, '\n')
    except:
        print(">>Error printing field data.<<\n")

#Writes provided repository output to provided file path. Takes a repository object, not a full page, and a valid file path.
#Fields to print are: Name, Description, Owner, created at, updated at, size(MB), programming language
def writeRepoToFile(repo, file):

    try:
        file.write(repo.name + ';')
    except:
        file.write(">>Error printing field data.<<;")
                    
    try:
        file.write(repo.description + ';')
    except:
        file.write(">>Error printing field data.<<;")

    try:
        file.write(repo.owner.login + ';')
    except:
        file.write(">>Error printing field data.<<;")
                                
    try:
        file.write(str(repo.created_at) + ';')
    except:
        file.write(">>Error printing field data.<<;")
                    
    try:
        file.write(str(repo.updated_at) + ';')
    except:
        file.write(">>Error printing field data.<<;")

    try:
        file.write(str(round(repo.size/1000)) + "MB;")
    except:
        file.write(">>Error printing field data.<<;")

    try:
        file.write(repo.language + '\n')
    except:
        file.write(">>Error printing field data.<<\n")

#Prints out a summary of all the repository items processesed so far. Takes three ints: The total number of hits returned by the search, the total size of the repositories processed so far and the number of repositories processed
#The rounding is done because github returns the size in KB, so we round it up to MB and GB.
#Estimated fetch and pull sizes: When downloading a repo with Git, fetch or pull, it includes extra files that make it exceed the size returned by the search function.
#I have found no great way to accurately estimate these sizes so here it simply uses a rough estimate      
def printSearchSummary(totalCount, totRepoSize, idNumber):
    try:        
        print("\nTotal Nr. of repos found:\t", totalCount, "\nNr. of repos processed:\t\t", idNumber, "\nSize of counted repos:\t\t", round(totRepoSize/1000, 1), " MB (", round((totRepoSize/1000000), 2), " GB)",
                "\nEstimated fetch download size:\t", round((totRepoSize*1.2)/1000, 1), " MB (", round(((totRepoSize*1.2)/1000000), 2), " GB)",
                "\nEstimated pull download size:\t", round((totRepoSize*2.4)/1000, 1), " MB (", round(((totRepoSize*2.4)/1000000), 2), " GB)")    #Data summary
    except:
        print("Error printing search summary to screen.")
        

#Used to start the git clone/pulls. Takes a repository object from pyGithub and a file path as arguments.
def dlGitRepo(gitRepo, dirPath, outputDir):

    codeReturned = 0
    
    try:
        gitContent = gitRepo.get_contents('')

        #If the filepath already exists and has items in it clone would fail, so instead we call a pull for the same location
        if os.path.exists(os.path.join(dirPath, gitRepo.full_name)):

            codeReturned = git("-C", os.path.join(dirPath, gitRepo.full_name), "pull", gitRepo.html_url, output = outputDir)
                
        else:   # Include --bare ?
            codeReturned = git("clone", "--single-branch", gitRepo.clone_url, os.path.join(os.path.join(dirPath, gitRepo.owner.login), gitRepo.name), output = outputDir)

        if codeReturned != 0 and outputDir != '':
            with open(outputDir, 'a') as out:
                out.write("Failed writing to: ", os.path.join(dirPath, gitRepo.full_name))
            
            
    except subprocess.CalledProcessError as e:
        print(e.output)
        print(e.returncode)
    except OSError as e:
        print(e)
        exit()
    except KeyboardInterrupt:
        print("Exited with keyboard interrupt")
        exit()
    except:
        print("Unknown exception in dlGitRepo")
        exit()

    # 0 is success, anything else an error.
    return codeReturned

#Used to call git with a subprocess call to commandline. *args should be a list of strings ex: ["clone", "--single-branch"], output should be a valid filepath
def git(*args, output):

    #0 is success, anything else an error
    codeToReturn = 0
    if output == '':
        return subprocess.check_call(['git'] + list(args))        
    else:
        p = Popen(['git'] + list(args), stdout = PIPE, stderr = STDOUT, bufsize = 1, universal_newlines = True)
        with open(output, 'a') as out:
            for line in p.stdout:
                print(line, end='')
                out.write(line)

        p.wait()
        return p.returncode
    
    
# Main starts here!
def main(argv):

    prepQuery = ''                  #Query to send to GitHub
    setSrchOrDL = 0                 #0 for search, 1 for download
    shortSummary = 0                #Should short search summary be turned on ? 1/0 yes/no
    outputDir = ''                  #Holds the directory for the output
    dlDir = ''                      #Holds the directory for the download
    rateLimitDivider = 15           #For handling the rate limit. 15 default for logged in users         
    regExPattern = ''               #Stores a regular expression pattern for use in input validation
    totRepoSize = 0                 #Stores the total size of repositores scanned so far
    totalCount = 0                  #Used to hold the total number of repositories found in the search
    idNumber = 0                    #The number of repositories processed by the search
    earliestDate = 2007-10-29       #The earliest date for a repository uploaded to github
    currentDate = datetime.date.today() #Todays date
    user = ''                       #Holds username to be sent to github
    passwrd = ''                    #Holds password to be sent to github
    nrOfFailedDownloads = 0         #Tracks the number of failed downloads

    #Argparse block defining how the system accepts commandline arguments. Also lets us define some useful info to print with the -h option
    parser = argparse.ArgumentParser(prog="GHDL.py", usage="%(prog)s [-d <path to directory>][--key <keyword>][--datecr <date>][--dateupd <date>][--size <int>][--stars <int>][--lang <keyword>][--short][--output <directory>][--help]",
                                     description="GitHubDL has two main modes of operation: By default it will search through repositories on github and return with some data on each matching result. The second mode, -d will instead download the matching repositories to the provided directory path, or attempt to update them if they already exist. Note: Requires pyGithub library for python and github executable installed.",
                                     epilog="Requires PyGithub and Github executable. Dependencies can be found at: PyGithub: https://github.com/PyGithub/PyGithub Github executable: https://desktop.github.com/")
    parser.add_argument("-d", "--download", help="Enables download function. Requires that you include a valid directory path for the download.")
    parser.add_argument("--key", help="Filters search results by matching the specified keywords or phrase to the names of repositories on github. Github supports the following characters in repository names: A-Z, a-z, 0-9, '.', '_', '-'.")
    parser.add_argument("--datecr", help="Limits search results to those created on the entered date. Format is yyyy-mm-dd. When entered as quoted string supports <, >, = and a range with .. to further specify results. Eg: --datecr \">=2015-01-01\" and --datecr \"2015-01-01..2016-01-01\"")
    parser.add_argument("--dateupd", help="Limits search results to those last updated on the entered date. Format is yyyy-mm-dd. When entered as quoted string supports <, >, = and a range with .. to further specify results. Eg: --dateupd \">=2015-01-01\" and --dateupd \"2015-01-01..2016-01-01\"")
    parser.add_argument("--size", help="Limits the size of the repositories in the search to the size specified(In MB). When entered as quoted string supports <, >, = and a range with .. to further specify results. Eg: --size \">=2\" and --size \"2..5\"")
    parser.add_argument("--lang", help="Filters search results by the specified programming language. Supported characters are A-Z, a-z, 0-9, '+', '-', '#'. Has limited regex support for * and . if the ghdllang.txt file is provided.")
    parser.add_argument("--stars", help="Filters search results by the number of stars held. When entered as quoted string supports <, >, = and a range with .. to further specify results. Eg: --stars \">=2\" and --stars \"2..5\"")
    parser.add_argument("--short", action="store_true", help="Shortens data presented when using the search function")
    parser.add_argument("--output", help="Outputs the printed data to the specified file. The parameter must be a valid file path.")

    #Arguments recieved(Hopefully), so now we go and process them.
    args = parser.parse_args()

    #Below all the options and arguments recieved by the parser are validated in turn
    
    if args.download:       # -d. Checks to see if the directory path provided is valid. Switches on dl by setting variable to 1.
        if os.path.lexists(args.download) and os.path.isdir(args.download):
            dlDir = args.download
            setSrchOrDL = 1
        else:
            print("Invalid directory path for download.")
            exit()
    if args.key:            # --key. Regex matches letters, numbers and '.', '_', '-'
        regExPattern = re.compile("^[A-Za-z0-9._-]*$")
        if regExPattern.match(args.key):    
            prepQuery += args.key + ' '
        else:
            print("Invalid key parameter. Check --help for suggestions on valid formats.")
            exit()
    if args.datecr:         # --datecr. Will match dates 1900-01-01 to 2099-12-31. Month limit to 1-12, day limit to 1-31. See --help section for further regex explanation.
        regExPattern = re.compile("^((19|20)\d\d-(0[1-9]|1[012])-(0[1-9]|[12][0-9]|3[01])$)|((19|20)\d\d-(0[1-9]|1[012])-(0[1-9]|[12][0-9]|3[01])\.\.(19|20)\d\d-(0[1-9]|1[012])-(0[1-9]|[12][0-9]|3[01])$)|([<>]=?(19|20)\d\d-(0[1-9]|1[012])-(0[1-9]|[12][0-9]|3[01])$)")
        if regExPattern.match(args.datecr):
            prepQuery += "created:" + args.datecr + ' '
        else:
            print("Invalid date parameter for datecr. Check --help for suggestions on valid formats.")
            exit()
    if args.dateupd:        # --dateupd. Will match dates 1900-01-01 to 2099-12-31. Month limit to 1-12, day limit to 1-31. See --help section for further regex explanation.
        regExPattern = re.compile("^((19|20)\d\d-(0[1-9]|1[012])-(0[1-9]|[12][0-9]|3[01])$)|((19|20)\d\d-(0[1-9]|1[012])-(0[1-9]|[12][0-9]|3[01])\.\.(19|20)\d\d-(0[1-9]|1[012])-(0[1-9]|[12][0-9]|3[01])$)|([<>]=?(19|20)\d\d-(0[1-9]|1[012])-(0[1-9]|[12][0-9]|3[01])$)")
        if regExPattern.match(args.dateupd):
            prepQuery += "pushed:" + args.dateupd + ' '
        else:
            print("Invalid date parameter for dateupd. Check --help for suggestions on valid formats.")
            exit()
    if args.size:           # --size. See --help section for regex explanation.
        regExPattern = re.compile("^([0-9]*$)|([0-9]*\.\.[0-9]*$)|([<>]=?[0-9]*$)")
        if regExPattern.match(args.size):
            prepQuery += "size:" + args.size + ' '
        else:
            print("Invalid size parameter. Check --help for suggestions on valid formats.")
            exit()
    if args.lang:           # --lang, If the file below exists the user can submit a little bit of regex('.', '*' only) to match the languages in the file. If no match we exit.
        if os.access("ghdllang.txt", os.R_OK):
            try:                #User can submit a string to act as regex, but this code escapes all the operators except '.' and '*' to limit crashing
                regExPattern = re.compile("^" + re.sub(r'([\+ \{ \} \[ \] \\ \^ \$ \? \" \'])', r'\\\1', args.lang.lower()) + "$")
            except:
                print("Invalid parameter for --lang. Check --help for suggestions on valid formats.")
                exit()
            matchFound = 0      #Checks through the file for matching strings. Breaks loop if match found.
            with open("ghdllang.txt", 'r') as file:
                contents = file.readlines()
                matchFound = 0
                for cont in contents:
                    if regExPattern.match(cont.lower()):
                        prepQuery += "language:" + cont + ''
                        matchFound = 1
                        break
                if matchFound == 0:
                    print("The parameter provided for --lang does not match any of the stored languages.")
                    exit()
        else:               #Simple regex for letters, numbers and '+', '#', '-'
            regExPattern = re.compile("^[A-Za-z0-9+#-]*$")
            if regExPattern.match(args.lang):
                prepQuery += "language:" + args.lang + ' '
            else:
                print("Invalid parameter for --lang. Check --help for suggestions on valid formats.")
                exit()
    if args.stars:          # --stars. Check the --help section for details on the regex
        regExPattern = re.compile("^([0-9]*$)|([0-9]*\.\.[0-9]*$)|([<>]=?[0-9]*$)")
        if regExPattern.match(args.stars):
            prepQuery += "stars:" + args.stars + ' '
        else:
            print("Invalid stars parameter. Check --help for suggestions on valid formats.")
            exit()
    if args.short:          # --short. Turns short summary on: 1 or off: 0
        shortSummary = 1
    if args.output:         # --output. First checks if file exists and is writable, if not it tries to open a file in that location and immediately removes it if succesful
        if  os.path.exists(args.output) and os.access(args.output, os.W_OK):
            outputDir = args.output
        else:
            if not os.access(args.output, os.W_OK):
                try:
                    open(args.output, 'w').close()
                    os.unlink(args.output)
                    outputDir = args.output
                except OSError as e:
                    print(e)
                    print("Invalid file path parameter for output. Check --help for suggestions on valid formats.")
                    exit()

    if prepQuery == '':
        print("Error: Must provide atleast one field for the search")
        exit()

    #Reads user login and password from a file
    
    user = ''
    passWrd = ''
    
    if os.access("ghpylogin.txt", os.R_OK):
        with open("ghpylogin.txt", 'r') as file:
            for index, line in enumerate(file):
                if index == 2:
                    user = line.strip()
                if index == 4:
                    passWrd = line.strip()       

    #Prepares github object. Can pass login details.
    #If username and password was read, use the top one, if not the bottom one.
    #per_page sets the number of items github returns per page. 20 is default.
    if(user != '' or passWrd != ''):
        g = Github(login_or_token=user, password=passWrd, per_page=100)
    else:
        g = Github(per_page=100)
    
    #Creates the repository list object
    repositories = g.search_repositories(prepQuery)
        
    print("Searching...")

    #First contact with github. Error checks to make sure everything went ok.
    #Sets totalCount to the total number of hits returned by the search.
    try:
        totalCount = repositories.totalCount
    except BadCredentialsException as e:
        print("Github error code: ", e.status, ", ", e.data['message'])
        print("Bad user credentials provided.")
        exit()
    except RateLimitExceededException as e:
        print("Github error code: ", e.status, ", ", e.data['message'])
        print("Unexpectedly encountered rate limit")
        exit()
    except BadAttributeException as e:
        print("Github error code: ", e.status, ", ", e.data['message'])        
        exit()
    except GithubException as e:
        print("Github error code: ", e.status, ", ", e.data['message'])
        if 'message' in e.data['errors'][0]:
            print(e.data['errors'][0]['message'])
        exit()
    except OSError as e:
        print(e)
        print("Error establishing connection to Github")
        exit()
    except:
        print("Encountered unexpected error.")
        exit()

    #If there are no matches for the search we exit.    
    if totalCount == 0:
            print("No matches found.")
            exit()
    elif setSrchOrDL == 0:        #Search part starts here

        #If an output file is set we write the header to the file here.
        if(outputDir != ''):
            try:
                with open(outputDir, 'w') as file:
                    file.write("Id;Name;Description;Owner;Created;Lastupdated;Size;Language\n")
            except OSError as e:
                print(e)
                print("Error opening outputfile")
                exit()

        #Repositores is given a paginated list of repository objects. These are further split into 'pages' of 20 to 100 entries per page
        #The below code is to iterate through the paginated list
        for i in range(0, int(math.ceil(repositories.totalCount/100))):    #The number divided by should match the number of entries recived per page

            #Check the level of the rate limit
            print("Rate limit: ", g.rate_limiting, "\nWaiting...")

            #The rate limit is 30 per minute. Every minute it will shoot back up to 30, so we make sure we never exceed it.
            if g.rate_limiting[0] < 5:
                time.sleep(10)
            elif g.rate_limiting[0] < 2:
                time.sleep(20)

            #Keeps the call from timing out by re-paging it every couple of items. I think...    
            if(i%3 == 0):
                repositories = g.search_repositories(prepQuery)

            #Tries to load a new repository page for processing. A page has 20..100 entries, editable in the call.
            try:
                repoPage = repositories.get_page(i)

                #Checks through every item in a page
                for repo in repoPage:

                    #If short summary is not enabled we print the individual item data to the screen
                    if shortSummary == 0:
                        printRepoToScreen(repo)         #Takes a repository item

                    #If an output path is set we print the item data to file
                    if(outputDir != ''):
                        with open(outputDir, 'a') as file:
                            file.write(str(idNumber) + ';')       #Writes an index number to the file along with a seperator
                            writeRepoToFile(repo, file)         #Takes a repository item and a valid file path

                    #Counts up the number of items processed so far and the total size returned by the items.
                    idNumber += 1
                    totRepoSize += repo.size                    
                    
            except RateLimitExceededException as e:             #Incase we hit the rate limit
                print("Github error code: ", e.status, ", ", e.data['message'])
                print("Unexpectedly encountered rate limit. Waiting 60 seconds to ensure limit is reset.")
                time.sleep(60)
                i -= i
            except GithubException as e:                #There are several GithubExceptions, not all have the same output
                print("Github error code: ", e.status, ", ", e.data['message'])
                if(idNumber == 1000):
                    print("The items returned by the search exceed 1000. Github has a limit of 1000 items returned per search query.\nPlease modify your search parameters so that the Nr. of items returned does not exceed 1000.\n")
                    printSearchSummary(totalCount, totRepoSize, idNumber)
                    exit()
                else:
                    if 'message' in e.data['errors'][0]:
                        print(e.data['errors'][0]['message'])
                    exit()
            except OSError as e:
                print(e)
                print("Connection error. Could not connect to Github.")
                exit()
            except BadAttributeException as e:
                print("Github error code: ", e.status, ", ", e.data['message'])
                print("Unexpected value returned by github.")
                exit()
            except KeyboardInterrupt:
                print("Exited with keyboard interrupt.")
                exit()
            except:
                print("Unknown error encountered in search function.")
                exit()

        #Prints a summary of the data gathered from all the repository items. Takes three ints, the total number of hits returned by the search, the total size of the processed items and the number of processed items
        printSearchSummary(totalCount, totRepoSize, idNumber)

    elif setSrchOrDL == 1:  #DL part starts here
                
        #Repositores is given a paginated list of repository objects. These are further split into 'pages' of 20 to 100 entries per page
        #The below code is to iterate through the paginated list
        for i in range(0, int(math.ceil(repositories.totalCount/100))):    #The number divided by should match the number of entries recived per page

            #Check the level of the rate limit
            print("Rate limit: ", g.rate_limiting, "\nWaiting...")

            #The rate limit is 30 per minute. Every minute it will shoot back up to 30, so we make sure we never exceed it.
            if g.rate_limiting[0] < 5:
                time.sleep(10)
            elif g.rate_limiting[0] < 2:
                time.sleep(20)

            #Keeps the call from timing out by re-paging it every couple of items. I think...    
            if(i%3 == 0):
                repositories = g.search_repositories(prepQuery)

            #Tries to load a new repository page for processing. A page has 20..100 entries, editable in the call.
            try:
                repoPage = repositories.get_page(i)

                #Checks through every item in a page
                for repo in repoPage:

                    if(outputDir != ''):
                        with open(outputDir, 'a') as file:
                            file.write(str(idNumber) + ';')       #Writes an index number to the file along with a seperator

                    #Recieves a return code from dlGitRepo. 0 is a success, anything else is an error in the download.
                    codeReturned = 0
                    codeReturned = dlGitRepo(repo, dlDir, outputDir)
                    if codeReturned != 0:
                        nrOfFailedDownloads +=1
                        
              #Counts up the number of items processed so far and the total size returned by the items.
                    idNumber += 1
                    totRepoSize += repo.size                    
                    
            except RateLimitExceededException as e:             #Incase we hit the rate limit
                print("Github error code: ", e.status, ", ", e.data['message'])
                print("Unexpectedly encountered rate limit. Waiting 60 seconds to ensure limit is reset.")
                time.sleep(60)
                i -= i
            except GithubException as e:                #There are several GithubExceptions, not all have the same output
                print("Github error code: ", e.status, ", ", e.data['message'])
                if(idNumber == 1000):
                    print("The items returned by the search exceed 1000. Github has a limit of 1000 items returned per search query.\nPlease modify your search parameters so that the Nr. of items returned does not exceed 1000.\n")
                    printSearchSummary(totalCount, totRepoSize, idNumber)
                    exit()
                else:
                    if 'message' in e.data['errors'][0]:
                        print(e.data['errors'][0]['message'])
                    exit()
            except OSError as e:
                print(e)
                print("Connection error. Could not connect to Github.")
                exit()
            except BadAttributeException as e:
                print("Github error code: ", e.status, ", ", e.data['message'])
                print("Unexpected value returned by github.")
                exit()
            except KeyboardInterrupt:
                print("Exited with keyboard interrupt.")
                exit()
            #except:
                print("Unknown error encountered in download function.")
                exit()

        #Prints a summary of the data gathered from all the repository items. Takes three ints, the total number of hits returned by the search, the total size of the processed items and the number of processed items
        printSearchSummary(totalCount, totRepoSize, idNumber)
        print("Failed downloads:\t\t", nrOfFailedDownloads)

if __name__ == "__main__":
    try: 
       main(sys.argv[1:])
    except KeyboardInterrupt:
        print("Exited with keyboard interrupt.")
        try:
            sys.exit()
        except SystemExit:
            os._exit(0)
