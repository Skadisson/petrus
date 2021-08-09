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
Package         Version
--------------- -----------
certifi         2021.5.30
colorclass      2.2.0
cycler          0.10.0
httplib2        0.19.1
joblib          1.0.1
kiwisolver      1.3.1
lxml            4.6.3
matplotlib      3.4.2
numpy           1.21.1
oauth2          1.9.0.post1
pandas          1.3.1
Pillow          8.3.1
pip             21.2.2
pip-check       2.6
pycurl          7.43.0.5
pymongo         3.12.0
pyparsing       2.4.7
python-dateutil 2.8.2
python-docx     0.8.11
pytz            2021.1
PyYAML          5.4.1
scikit-learn    0.24.2
scipy           1.7.1
setuptools      57.4.0
six             1.16.0
sklearn         0.0
terminaltables  3.1.0
threadpoolctl   2.2.0
tlslite         0.4.9
Werkzeug        2.0.1
wheel           0.36.2
wincertstore    0.2
</pre>

Use "pip list --outdated --format=columns" to check for outdated versions.

Inspect Code:
SciKitLearn.py
Expected type 'int', got 'DataFrame' instead

___

Disclaimer: In order to reuse parts of this repository, please contact me directly on GitHub. For reasons of security you can not run this application unless you possess certain environmental and temporary folders, files and API secrets, which will not be provided in this repository.