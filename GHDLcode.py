import requests
import json

sTerm = -1
searchParameters = ''

while(sTerm != '0'):

    sTerm = input('Input search term: ')
    
    if(sTerm != '0'):
        searchParameters = input('Input parameters: ')

        if(sTerm != ''):
            resp = requests.get('https://api.github.com/search/repositories?q=' + sTerm + searchParameters)

        if(resp.status_code != 200):    
            print('Status code ERROR')
        else:
            print(resp.json())
    else:
        print('Exiting')
