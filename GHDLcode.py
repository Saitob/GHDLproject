#!/usr/bin/python

#Used to handle command-line arguments
import sys, getopt
#Part of PyGithub, used for API communication
from github import Github

def main(argv):

    prepQuery = ''                  #Query to send to GitHub
    shortSummary = 0
    
    try:
        opts, args = getopt.getopt(argv,'',["key=","datecr=","dateupd=","size=","lang=", "short"])
    except getopt.GetoptError:
        print('Error: Invalid argument.')
        sys.exit(2)
        
    for opt, arg in opts:
        print(opt,arg)

        if opt == '--key':           # Too many ifs ?
            prepQuery += arg + ' '
        elif opt == '--datecr':                 #Current format "2012-07-03". Make "120703" ?
            prepQuery += "created:" + arg + ' '
        elif opt == '--dateupd':                #Current format "2012-07-03". Make "120703" ?
            prepQuery += "pushed:" + arg + ' '
        elif opt == '--size':
            prepQuery += "size:" + arg + ' '
        elif opt == '--lang':
            prepQuery += "language:" + arg + ' '
        elif opt == '--short':                  #Omit individual item data 0/1
            shortSummary = 1

    print(prepQuery)
                                   
    nrOfRepos = 0
    totRepoSize = 0
        
    g = Github()        #Prepares github object. Can pass login details.

    if shortSummary == 0:                               #Duplicate code. Nicer way to do it ?
        for repo in g.search_repositories(prepQuery):       #For each item writes out data.
            nrOfRepos += 1
            totRepoSize += repo.size
            print("Name:\n", repo.name, "\nDescription:\n", repo.description, "\nCreated:\n", repo.created_at, "\nLast updated:\n", repo.updated_at, "\nSize:\n", round(repo.size/1000), " MB", "\nProgramming language:\n", repo.language, '\n')
    else:
        for repo in g.search_repositories(prepQuery):
            nrOfRepos += 1
            totRepoSize += repo.size
            
    print("\nNr of repos found: ", nrOfRepos, "\nSize of repos: ", round(totRepoSize/1000, 1), " MB (", round((totRepoSize/1000000), 1), " GB)")    #Data summary

if __name__ == "__main__":
   main(sys.argv[1:]) # ??
