#!/usr/bin/python
# coding=utf-8

#Used to handle command-line arguments
import sys, argparse, getopt, subprocess
#Download files   (Wasted ?)
#import urllib.request, requests
#Regular expressions
import re
#Handle base64 encoding
#import base64

#For checking files and directories
import os
#Part of PyGithub, used for API communication
from github import Github
from github import GithubException

#Used to start the git clone/pulls. Takes a repository object from pyGithub and a filepath as arguments.
def dlGitRepo(gitRepo, gitPath):
    
    gitContent = gitRepo.get_contents(gitPath)

    #If the filepath already exists and has items in it clone would fail, so instead we call a pull for the same location
    if os.path.exists("ImproperTest/" + gitRepo.full_name + "/"):
        try:
            git("-C", "ImproperTest/" + gitRepo.full_name, "pull", gitRepo.html_url)
        except(subprocess.CalledProcessError):
            print(subprocess.CalledProcessError.check_output())
    else:   # Include --bare ?
        try:
            git("clone", "--single-branch", gitRepo.clone_url, "ImproperTest/" + gitRepo.owner.login + "/" + gitRepo.name + "/")
        except(subprocess.CalledProcessError):
            print(subprocess.CalledProcessError.check_output())

#Used to call git by commandline. *args should be a list of strings ex: ["clone", "--single-branch"]
def git(*args):
    return subprocess.check_call(['git'] + list(args))

def main(argv):

    prepQuery = ''                  #Query to send to GitHub
    setSrchOrDL = 0                 #0 for search, 1 for download
    shortSummary = 0                #Should short search summary be turned on ? 1/0 yes/no
    dlDirectory = ''                #Holds the directory for the download

    #Argparse block defining how the system accepts commandline arguments. Also lets us define some useful info to print with the -h option
    parser = argparse.ArgumentParser(prog="GitHubDL.py", usage="%(prog)s [-d | -s][--key <keyword>][--datecr <date>][--dateupd <date>][--size <int>][--lang <keyword>][--short][--dldir]",
                                     description="GitHubDL has two main modes of operation: -s Will search through repositories on github and return with some data on each matching result. -d Similar to search but will instead download the matching repositories to the --dldir provided filepath. Note: Requires pyGithub library for python and github executable installed.",
                                     epilog="Dependencies can be found at: PyGithub: https://github.com/PyGithub/PyGithub Github executable at: https://desktop.github.com/")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-s", "--search", action="store_true", help="Enables search function.")      #Makes sure system can be called with either -s or -d, not both
    group.add_argument("-d", "--download", action="store_true", help="Enables download function.")
    parser.add_argument("--key", help="Filters search results by the specified keywords or phrase.")
    parser.add_argument("--datecr", help="Limits search results to only those created after the entered date.")
    parser.add_argument("--dateupd", help="Limits search results to only those last updated after the entered date.")
    parser.add_argument("--size", help="Limits the size of the repositories to the size specified(In MB).")
    parser.add_argument("--lang", help="Filters search results by the specified programming language.")
    parser.add_argument("--short", action="store_true", help="Shortens data presented when using the search function")
    parser.add_argument("--dldir", help="Specifies directory for downloading files. NOTE: Required when using the download function")  

    #Arguments recieved(Hopefully), so now we go and process them.
    args = parser.parse_args()

    if args.search:
        setSrchOrDL = 0
    if args.download:
        setSrchOrDL = 1
    if args.download is True and args.dldir is None:        #Aborts if -d is called without a --dldir path
        parser.error("Error: -d requires that you specify a --dldir")
    if args.key:
        prepQuery += args.key + ' '
    if args.datecr:
        prepQuery += "created:" + args.datecr + ' '
    if args.dateupd:
        prepQuery += "pushed:" + args.dateupd + ' '
    if args.size:
        prepQuery += "size:" + args.size + ' '
    if args.lang:
        prepQuery += "language:" + args.lang + ' '
    if args.short:
        shortSummary = 1
    if args.dldir:
        dlDirectory = args.dldir
    
    totRepoSize = 0

    #Reads user login and password from a file
    
    user = ''
    passWrd = ''
    
    if os.access("ghpylogin.txt", os.R_OK):
        with open("ghpylogin.txt", 'r') as file:
            contents = file.readlines()
            user = contents[2].strip()
            passWrd = contents[4].strip()

    g = Github(user, passWrd)      #Prepares github object. Can pass login details.

    #Creates the repository list object
    try:
        repositories = g.search_repositories(prepQuery)
    except:
        print("Error happened")
    
    if repositories.totalCount == 0:
        print("No matches found.")
    
    elif setSrchOrDL == 0:        #Search part starts here
        if shortSummary == 0:                               #Duplicate code. Nicer way to do it ?
            for repo in repositories:       #For each item writes out data.
                totRepoSize += repo.size
                try:
                    print("Name:\n", repo.name, "\nDescription:\n", repo.description, "\nCreated:\n", repo.created_at, "\nLast updated:\n", repo.updated_at, "\nSize:\n", round(repo.size/1000), " MB", "\nProgramming language:\n", repo.language, '\n')
                except:
                    print("An error has occured")
        else:
            for repo in repositories:
                totRepoSize += repo.size
        try:        
            print("\nNr of repos found:\t", repositories.totalCount, "\nSize of repos:\t\t", round(totRepoSize/1000, 1), " MB (", round((totRepoSize/1000000), 2), " GB)",
                  "\nEstimated fetch download size:\t", round((totRepoSize*1.2)/1000, 1), " MB (", round(((totRepoSize*1.2)/1000000), 2), " GB)",
                  "\nEstimated pull download size:\t", round((totRepoSize*2.4)/1000, 1), " MB (", round(((totRepoSize*2.4)/1000000), 2), " GB)")    #Data summary
        except:
            print("Error may have occured")

    elif setSrchOrDL == 1:  #DL part starts here
                
        for repo in repositories:
            totRepoSize += repo.size

            dlGitRepo(repo, dlDirectory)

        print("\nNr of repos downloaded: ", repositories.totalCount)

if __name__ == "__main__":
   main(sys.argv[1:]) # ??
