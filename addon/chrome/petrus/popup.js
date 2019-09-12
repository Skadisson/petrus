function onPageDetailsReceived(pageDetails) {
    document.getElementById('jira_key').value = pageDetails.jira_key;
}

var statusDisplay = null;

function estimate() {

    event.preventDefault();

    var jira_key = document.getElementById('jira_key');
    var getUrl = 'http://192.168.6.152:55888/?function=Estimate&jira_key=' + encodeURIComponent(jira_key.value);
    var formContentType = 'application/x-www-form-urlencoded';
    try {
        var xhr = new XMLHttpRequest();
        xhr.open('GET', getUrl, true);
        xhr.setRequestHeader('Content-type', formContentType);
        xhr.onreadystatechange = function() {
            statusDisplay.innerHTML = 'Done.';
        };
        xhr.send();
    } catch(e) {
        statusDisplay.innerHTML = e.message;
    }
    statusDisplay.innerHTML = 'Saving...';
}

window.addEventListener('load', function(evt) {
    statusDisplay = document.getElementById('status-display');
    document.getElementById('update').addEventListener('submit', estimate);
    chrome.runtime.getBackgroundPage(function(eventPage) {
        eventPage.getPageDetails(onPageDetailsReceived);
    });
});