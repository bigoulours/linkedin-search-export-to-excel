Update: autocompletion is now broken since Linkedin has changed its backend for typeahead.

This tool allows any LinkedIn user to search for people or jobs with their own credentials.\
It is based on [linkedin-api](https://github.com/bigoulours/linkedin-api) which uses the LinkedIn Voyager API. Install the modified version with:
```
pip install lib/linkedin_api
```
Install dependencies with:
```
pip install -r requirements.txt
```
Each search tab offers a number of search fields similar to the LinkedIn website.\
User name can be set in `linkedInSearch.ini`. Thanks to cookies, you don't have to enter your password every time.

/!\ Beware of the LinkedIn search limit if you're using this tool with a free account! If you run a lot of searches that yield a lot of results you'll quickly be limited to 3 results until the end of the month.

![screenshot](screenshot.png)
