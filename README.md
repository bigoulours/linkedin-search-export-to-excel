This tool allows any LinkedIn user to search people with their own credentials.\
It is based on [linkedin-api](https://github.com/bigoulours/linkedin-api) which uses the LinkedIn Voyager API.\
Install dependencies with:
```
pip install -r requirements.txt
```
Search can be done using a specific company public ID (www[]().linkedin.com/company/\<public-id\>), thus narrowing search results.\
Company public IDs and Bing geo urn IDs can be added in the dedicated text files.\
User name can be set in `linkedInSearch.ini`. Thanks to cookies, you don't have to enter your password every time.

/!\ Beware of the LinkedIn search limit if you're using this tool with a free account! If you run a lot of searches that yield a lot of results you'll quickly be limited to 3 results until the end of the month.

![screenshot](screenshot.png)
