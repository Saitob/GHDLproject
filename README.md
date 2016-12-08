# GHDLproject

1. Purpose
2. Usage
3. Dependencies
4. Functions
5. Additional files
6. Limitations
7. Useful links


### Purpose:

The purpose of the project is a system that can communicate with the github API, search through its repositories and download and update a large number  of repositories that match the search result.

The system is called and recives its arguments through commandline. It has 2 major operations:


* Default : Searches through github repositores based on provided search terms and returns with data on each of the matching results, along with a short summary at the end.

Providing --short at the end of the call only returns the short summary as a result of the search.

Takes --key, --datecr, --dateupd, --size, --stars, --lang, --short, --output



* -d | --download: Similar to Search but rather than returning data for each matching result it does a git clone (or git pull for already downloaded repositories) on each matching result to the provided filepath.

Takes --key, --datecr, --dateupd, --size, --stars, --lang, --output


The project is written in Python 3 and primarily intended to be used on a Linux system.


### Usage:

GHDL.py [-d <directorypath>][--key <keyword>][--datecr <date>][--dateupd <date>][--size <number>][--stars <number>][--lang <keyword>][--short][--output <filepath>]


### Options:

Default:<br>		Tells the script to do a search through github repositories and return with information about each match.<br>
			Info returned includes name, owner, date created, date last updated, programming language and size.


-d | --download:<br>	Tells the script to do a download. Searches through repositories similar to the default setting but instead
			of returning with information on each match it downloads the repository with git to the specified directory.
			Requires that you provide a valid directory path.


--key:<br>		Takes a string to use as a keyword for the repository search. The keyword is matched towards the repository 				name. Valid characters are A-Z, a-z, 0-9, '.', '_' and '-'.


--datecr:<br>		Takes a date string to filter the search results by. Format is yyyy-mm-dd. 
			Simple date shows exact date matches.
			
			Valid dates are between 1970-01-01 and 2099-12-31.
			
			Accepts  >, < and = to enhance filter when given as quoted string.
			Eg: --datecr ”>=2015-01-01”
			
			You can also provide 2 dates split by '..' to search in a range.
			Eg. --datecr ”2015-01-01..2016-01-01”


--dateupd:<br>		Takes a date string to filter the search results by. Format is yyyy-mm-dd. 
			Simple date shows exact date matches.
			
			Valid dates are between 1970-01-01 and 2099-12-31.
			
			Accepts  >, < and = to enhance filter when given as quoted string.
			Eg: --dateupd ”>=2015-01-01”
			
			You can also provide 2 dates split by '..' to search in a range.
			Eg. --dateupd ”2015-01-01..2016-01-01”


--size:<br>		Takes a number and filters the search results by files that match the given size.

			Accepts  >, < and = to enhance filter when given as quoted string.
			Eg: --size ”>=2”
			
			You can also provide 2 numbers split by '..' to search in a range.
			Eg. --size ”1..5”
			

--stars:<br>		Takes a number and filters the search results by files that match the given number of stars.

			Accepts  >, < and = to enhance filter when given as quoted string.
			Eg: --stars ”>=2”
			
			You can also provide 2 numbers split by '..' to search in a range.
			Eg. --stars ”1..5”
			

--lang:<br>		Filters the search by only listing repositories that are listed with the given programming language.
			
			
			If the ghdllang.txt file is in the same folder as the script a limited form of regex is available when entering 			
			language.
			
			ghdllang.txt contains a list of programming languages the regex will attempt to match to and only 					
			continue to run the script if a match is found.
			
			The available regex is '.' and '*' and the program will match to the first match found.
			
			ex. '.' will match 'c'. 'javasc.*' will match 'javascript'.
			
			If the file is not available it will take a simple string, limited to the characters 'A-Z', 'a-z', '0-9', '+', 				'-' and '#'. 


--short:<br>		If enabled omits the individual item data for the search operation and instead just lists the summary.


--output:<br>		If provided a valid filepath will output the search data or git output to the file.


			Note 1: Has no proper filter for valid file endings. This falls on the user.
			
			Note 2: Output for search will overwrite the contents of the target file.
			
			Note 3: The git output is somewhat messy and tricky to format to print. It is currently provided as-is.


-h | --help:<br>	Shows some brief help text for the user.


### Dependencies:

This project uses and requires PyGithub and the Github executable. These can be found here:

PyGithub:
https://github.com/PyGithub/PyGithub

Can be installed with  -  '$pip install pygithub'

Github executable:
https://desktop.github.com/

#### Recommended:

Login:

Included with the project is a text file storing username and password for a github account, named ghpylogin.txt. The username should be written under the line that says 'Username:' and password should be written under the line 'Password:. 
The script will read off this file and use the credentials to authenticate with the github servers.
This gives a higher rate limit for the search API connection and allows the download to go much faster.


### Functions:

#### Main:

Starts off by  defining 'argparse' arguments and gathering user input from the commandline call.

If the ghpylogin.txt file is detected the script will try to read username and password from the file to use for the call to github.

Makes a call to the github API using PyGithub with parameterers set by the parser.

The repositories are recieved by the call as a paginated list of repositories.

Paginated list: (http://pygithub.readthedocs.io/en/latest/utilities.html#github.PaginatedList.PaginatedList)

We then iterate through the list and decide on an action depending on if it's a search or download operation.

##### Search:
Print information gathered from each repository object to the screen. Gather a summary of the total size of all the repositories so far.

**A note on the repository size returned by the search**

The search will return 3 different sizes:

###### Repository size:
This is the size of the repository returned by the Github search API. It shows the size of all the files belonging to the repository.

###### Fetch/Bare size and Pull size:

When git downloads a repository it includes a number of extra files belonging to the git executable into each repository. These files add extra size ontop of the repository size. There's no exact way to measure those sizes added to the project yet. The current representation is simply a rough estimate calculated as such:

Fetch/Bare: Repository size * 1.2

Pull: Repository size * 2.4

##### Download:
Pass the repository object onward to dlGitRepo to start downloading.

After this we print a short summary of the result, and done.


#### dlGitRepo(gitRepo, gitPath, outputDir):

Takes a repository (link below) object and two filepaths, the download directory and an output directory for the text data.

Checks to see if a directory already exists for the repository name. If true passes arguments for a git pull to git(*args), if false it instead passes a git clone.

Repository object: (http://pygithub.readthedocs.io/en/latest/github_objects/Repository.html)



#### git(*args, output):

Takes a list of arguments as strings and passes them to a subprocess commandline call to 'git' (ex: pull, clone).
Second argument can be a filepath for output of the git data stream.

Returns after executing the subprocess call. 0 is a succesful call, anything else is an error.


#### printRepoToScreen(repo):

Takes a repository object as an argument.

Prints the datafields it can gather from the repository to the screen.


#### writeRepoToFile(repo, file):

Takes a repository object and file path as arguments.

Writes out the datafields it can gather from the repository to the file.


#### printSearchSummary(totalCount, totRepoSize, idNumber):

Takes as arguments: The total number of hits recieved by the repository size, the total size of the repositories processed so far
and the number of items processed so far.

Prints out a summary of the data gathered from the search to the screen.


### Additional files:

The project has two extra text files that provide some functions:


ghpylogin.txt is a text file storing username and password for a github account. The username should be written under the line that says 'Username:' and password should be written under the line 'Password:. 
The script will read off this file and use the credentials to authenticate with the github servers.
This gives a higher rate limit for the search API connection and allows the download to go much faster.


ghdllang.txt has a list of programming languages that the script will read from if they are located in the same directory. This enables some basic regex functionality for the --lang option. See the --lang explanation further up to see how to use it.


### Limitations:

#### Rate limit:

The search function for Github's API has a request limit of 30 requests per minute, meaning every 60 seconds it will shoot back up to 30
and then decrease by 1 every time it recieves a request. For this script that means on every page request, and with multiple requests and a fast connection it is very possible to run into the limit.
The script includes safeguards to throttle the requests if it starts approaching the rate limit, so it should (in theory) never encounter it, but be aware that this throttling is a necessary limitation put on the script.

#### Limit on items returned:

Github's search API has a limit on 1000 items returned in a search. This means that if a search returns 10 000 repositories, only the data on the first 1000 will be available. Getting around this requires the use of most, if not all, of the search parameters in combination with multiple calls.
For example, searching for all projects upploaded on 2015-01-01, updated on 2015-01-01, with 0 stars, written in Java, will still return more than 1000 repositories.

This script currently has no built in functionality to get around this problem, other than the user calling the script multiple times with different parameters.


### Useful links:

PyGithub documentation:

(http://pygithub.readthedocs.io/en/latest/introduction.html)

Github page:
(https://github.com/PyGithub/PyGithub)

Github API documentation:
(https://developer.github.com/v3/)
