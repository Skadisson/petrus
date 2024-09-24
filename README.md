# Petrus 2+
###### Pre Estimating Ticket Rates Using SciKit-Learn v2.1

Self-sufficient Python 3 web service package using SciKit-Learn to estimate times to process and finish a ticket, calculate trends and communicates with the Jira Service Desk API.
Since september 2024 Petrus 2+ additionally includes the use of the LLM llama 3.1 via Ollama in order to provide answers out of collected and trained software documentations.

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
anyio                           4.4.0
Aspose.Email-for-Python-via-NET 23.1
async-timeout                   4.0.3
attrs                           23.2.0
backoff                         2.2.1
beautifulsoup4                  4.12.3
cached-property                 1.5.2
certifi                         2024.6.2
cffi                            1.15.1
chardet                         5.2.0
charset-normalizer              2.1.1
click                           8.1.7
colorama                        0.4.6
colorclass                      2.2.2
coloredlogs                     15.0.1
compoundfiles                   0.3
cryptography                    38.0.1
cycler                          0.11.0
dataclasses-json                0.6.7
defusedxml                      0.7.1
dnspython                       2.2.1
emoji                           2.12.1
exceptiongroup                  1.2.2
filelock                        3.15.4
filetype                        1.2.0
flatbuffers                     24.3.25
fonttools                       4.34.4
frozenlist                      1.4.1
fsspec                          2024.6.1
greenlet                        3.0.3
h11                             0.14.0
httpcore                        1.0.5
httplib2                        0.20.4
httpx                           0.27.2
huggingface-hub                 0.24.5
humanfriendly                   10.0
idna                            3.3
iopath                          0.1.10
isodate                         0.6.1
Jinja2                          3.1.4
joblib                          1.3.2
jsonpatch                       1.33
jsonpath-python                 1.0.6
jsonpointer                     3.0.0
kiwisolver                      1.4.4
langchain                       0.3.0
langchain-community             0.3.0
langchain-core                  0.3.1
langchain-text-splitters        0.3.0
langdetect                      1.0.9
langsmith                       0.1.121
layoutparser                    0.3.4
lxml                            4.9.1
MarkupSafe                      2.1.1
marshmallow                     3.21.3
marshmallow-enum                1.5.1
matplotlib                      3.5.3
mpmath                          1.3.0
multidict                       6.0.5
mypy-extensions                 1.0.0
networkx                        3.2.1
nltk                            3.8.1
ntlm-auth                       1.5.0
numpy                           1.23.1
oauth2                          1.9.0.post1
oauthlib                        3.2.0
ollama                          0.3.3
onnx                            1.16.1
onnxruntime                     1.18.1
opencv-python                   4.10.0.84
orjson                          3.10.5
outlook-msg                     1.0.0
packaging                       24.1
pandas                          1.4.3
pdf2image                       1.17.0
pdfminer                        20191125
pdfminer.six                    20231228
pdfplumber                      0.11.2
pillow                          10.3.0
pillow_heif                     0.18.0
pip                             22.1.2
pip-check                       2.7
portalocker                     2.10.1
protobuf                        5.27.2
pycparser                       2.21
pycryptodome                    3.20.0
pydantic                        2.7.4
pydantic_core                   2.18.4
pydantic-settings               2.5.2
Pygments                        2.13.0
pymongo                         4.2.0
pyparsing                       3.0.9
pypdfium2                       4.30.0
pyreadline3                     3.4.1
pytesseract                     0.3.10
python-dateutil                 2.8.2
python-docx                     0.8.11
python-dotenv                   1.0.1
python-iso639                   2024.4.27
python-magic                    0.4.27
python-multipart                0.0.9
pytz                            2022.1
pytz-deprecation-shim           0.1.0.post0
pywin32                         306
PyYAML                          6.0
rapidfuzz                       3.9.3
regex                           2023.10.3
requests                        2.28.1
requests-ntlm                   1.1.0
requests-oauthlib               1.3.1
safetensors                     0.4.3
scikit-learn                    1.4.1.post1
scipy                           1.9.0
setuptools                      61.2.0
six                             1.16.0
sklearn                         0.0
sniffio                         1.3.1
soupsieve                       2.5
SQLAlchemy                      2.0.31
sympy                           1.13.1
tabulate                        0.9.0
tenacity                        8.4.2
terminaltables                  3.1.10
threadpoolctl                   3.1.0
timm                            1.0.8
tlslite                         0.4.9
tokenizers                      0.19.1
torch                           2.4.0
torchvision                     0.19.0
tqdm                            4.66.1
transformers                    4.43.3
typing_extensions               4.12.2
typing-inspect                  0.9.0
tzdata                          2022.2
tzlocal                         4.2
unstructured                    0.14.8
unstructured-client             0.8.1
unstructured-inference          0.7.36
urllib3                         1.26.12
Werkzeug                        2.2.2
wheel                           0.37.1
wincertstore                    0.2
wrapt                           1.16.0
yarl                            1.9.4
</pre>

Use "pip list --outdated --format=columns" to check for outdated versions.

Inspect Code:
SciKitLearn.py
Expected type 'int', got 'DataFrame' instead

___

Disclaimer: In order to reuse parts of this repository, please contact me directly on GitHub. For reasons of security you can not run this application unless you possess certain environmental and temporary folders, files and API secrets, which will not be provided in this repository.