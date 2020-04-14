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
--------------- -------------------
certifi         2020.4.5.1
colorclass      2.2.0
cycler          0.10.0
httplib2        0.17.2
joblib          0.14.1
kiwisolver      1.2.0
lxml            4.5.0
matplotlib      3.2.1
numpy           1.18.2
oauth2          1.9.0.post1
pandas          1.0.3
pip             20.0.2
pip-check       2.6
pyparsing       2.4.7
python-dateutil 2.8.1
python-docx     0.8.10
pytz            2019.3
PyYAML          5.3.1
scikit-learn    0.22.2.post1
scipy           1.4.1
setuptools      46.1.3.post20200330
six             1.14.0
sklearn         0.0
terminaltables  3.1.0
tlslite         0.4.9
Werkzeug        1.0.1
wheel           0.34.2
wincertstore    0.2
</pre>

Use "pip list --outdated --format=columns" to check for outdated versions.

Inspect Code:
SciKitLearn.py
Expected type 'int', got 'DataFrame' instead

___

Disclaimer: In order to reuse parts of this repository, please contact me directly on GitHub. For reasons of security you can not run this application unless you possess certain environmental and temporary folders, files and API secrets, which will not be provided in this repository.