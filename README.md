# Petrus 2
###### Pre Estimating Ticket Rates Using SciKit-Learn v2

Self-sufficient Python 3 web service package using SciKit-Learn to estimate times to process and finish a ticket, calculate trends and communicates with the Jira Service Desk API.

![Screenshot](src/screenshot.png "Petrus 2 Screenshot")

This application is running on Conda environments, provided by the Anaconda Machine Learning Framework.

https://docs.atlassian.com/jira-servicedesk/REST/3.6.2/

___

![Petrus 2 Flow Chart](src/petrus_v2.png "Petrus 2 Flow Chart")

___

pip list -l
<pre>
Package                         Version
------------------------------- -----------
aiohttp                         3.9.5
aiosignal                       1.3.1
annotated-types                 0.7.0
Aspose.Email-for-Python-via-NET 23.1
async-timeout                   4.0.3
attrs                           23.2.0
cached-property                 1.5.2
certifi                         2022.6.15
cffi                            1.15.1
charset-normalizer              2.1.1
click                           8.1.7
colorama                        0.4.6
colorclass                      2.2.2
compoundfiles                   0.3
cryptography                    38.0.1
cycler                          0.11.0
defusedxml                      0.7.1
dnspython                       2.2.1
fonttools                       4.34.4
frozenlist                      1.4.1
greenlet                        3.0.3
httplib2                        0.20.4
idna                            3.3
isodate                         0.6.1
joblib                          1.3.2
jsonpatch                       1.33
jsonpointer                     3.0.0
kiwisolver                      1.4.4
langchain                       0.2.6
langchain-core                  0.2.10
langchain-text-splitters        0.2.2
langsmith                       0.1.82
lxml                            4.9.1
MarkupSafe                      2.1.1
matplotlib                      3.5.3
multidict                       6.0.5
nltk                            3.8.1
ntlm-auth                       1.5.0
numpy                           1.23.1
oauth2                          1.9.0.post1
oauthlib                        3.2.0
orjson                          3.10.5
outlook-msg                     1.0.0
packaging                       24.1
pandas                          1.4.3
Pillow                          9.2.0
pip                             22.1.2
pip-check                       2.7
pycparser                       2.21
pydantic                        2.7.4
pydantic_core                   2.18.4
Pygments                        2.13.0
pymongo                         4.2.0
pyparsing                       3.0.9
python-dateutil                 2.8.2
python-docx                     0.8.11
pytz                            2022.1
pytz-deprecation-shim           0.1.0.post0
PyYAML                          6.0
regex                           2023.10.3
requests                        2.28.1
requests-ntlm                   1.1.0
requests-oauthlib               1.3.1
scikit-learn                    1.4.1.post1
scipy                           1.9.0
setuptools                      61.2.0
six                             1.16.0
sklearn                         0.0
SQLAlchemy                      2.0.31
tenacity                        8.4.2
terminaltables                  3.1.10
threadpoolctl                   3.1.0
tlslite                         0.4.9
tqdm                            4.66.1
typing_extensions               4.12.2
tzdata                          2022.2
tzlocal                         4.2
urllib3                         1.26.12
Werkzeug                        2.2.2
wheel                           0.37.1
wincertstore                    0.2
yarl                            1.9.4
</pre>

Use "pip list --outdated --format=columns" to check for outdated versions.

Inspect Code:
SciKitLearn.py
Expected type 'int', got 'DataFrame' instead

___

Disclaimer: In order to reuse parts of this repository, please contact me directly on GitHub. For reasons of security you can not run this application unless you possess certain environmental and temporary folders, files and API secrets, which will not be provided in this repository.