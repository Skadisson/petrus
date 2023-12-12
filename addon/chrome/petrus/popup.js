function onPageDetailsReceived(pageDetails) {
    document.getElementById('jira_key').value = pageDetails.jira_key;
}

var statusDisplay = null;

function estimate() {

    event.preventDefault();

    var jira_key = document.getElementById('jira_key');
    var getUrl = 'http://localhost:55888/?function=Estimate&jira_key=' + encodeURIComponent(jira_key.value);
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

function search() {

    event.preventDefault();

    document.getElementById('link-list').innerHTML = '';
    var query = document.getElementById('query');
    var getUrl = 'http://localhost:55888/?function=Search&keywords=' + encodeURIComponent(query.value);
    var formContentType = 'application/x-www-form-urlencoded';
    try {
        var xhr = new XMLHttpRequest();
        xhr.open('GET', getUrl, true);
        xhr.setRequestHeader('Content-type', formContentType);
        xhr.onreadystatechange = function() {
            if (xhr.readyState === xhr.DONE) {
                if (xhr.status === 200) {
                    var json_parsed = JSON.parse(xhr.responseText);
                    if(json_parsed && typeof json_parsed.items !== 'undefined') {
                        var parsed_list = json_parsed.items[0].relevancy;
                        document.getElementById('link-list').innerHTML = '';
                        for(var i in parsed_list) {
                            document.getElementById('link-list').innerHTML += '<p><a href="' + parsed_list[i].link + '" target="_blank">' + parsed_list[i].title + ' [' + parseInt(parsed_list[i].percentage) + '%]</a></p>';
                        }
                    }
                }
            }
        };
        xhr.send();
    } catch(e) {
        console.log(e.message);
    }

}

function ping() {
    document.getElementById('is-online').innerHTML = 'pending';
    var getUrl = 'http://localhost:55888/?function=Ping';
    var formContentType = 'application/x-www-form-urlencoded';
    try {
        var xhr = new XMLHttpRequest();
        xhr.open('GET', getUrl, true);
        xhr.setRequestHeader('Content-type', formContentType);
        xhr.onreadystatechange = function() {
            if(xhr.status == 200) {
                document.getElementById('is-online').innerHTML = 'online';
            } else {
                document.getElementById('is-online').innerHTML = 'offline';
            }
        };
        xhr.send();
    } catch(e) {
        document.getElementById('is-online').innerHTML = 'offline';
    }
}

window.addEventListener('load', function(evt) {
    ping();
    statusDisplay = document.getElementById('status-display');
    document.getElementById('update').addEventListener('submit', estimate);
    document.getElementById('search').addEventListener('submit', search);
    chrome.runtime.getBackgroundPage(function(eventPage) {
        eventPage.getPageDetails(onPageDetailsReceived);
    });
});