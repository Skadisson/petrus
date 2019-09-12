var petrusSearch;

PS = (function() {

    var self;

    var construct = function() {
        self = this;
        self.init();
    };

    function init() {
        var urlParams = new URLSearchParams(window.location.search);
        var keywords = urlParams.get('keywords');
        console.log(keywords);
        $('#keywords').val(keywords);
        $('#search').on('submit', self.search);
    }

    function search(event) {

        event.preventDefault();

        var keywords = $('#keywords').val();
        var getUrl = 'http://192.168.6.152:55888/?function=Search&keywords=' + encodeURIComponent(keywords);
        var formContentType = 'application/x-www-form-urlencoded';
        try {
            var xhr = new XMLHttpRequest();
            xhr.open('GET', getUrl, true);
            xhr.setRequestHeader('Content-type', formContentType);
            xhr.onreadystatechange = function() {
                if(xhr.responseText) {
                    $('#link-list').html('');
                    result = JSON.parse(xhr.responseText).items[0].relevancy;
                    for(index in result) {
                        $('#link-list').append('<p><a href="' + result[index].link + '" target="_blank">' + result[index].title + ' (' + result[index].percentage + '%)</a></p>');
                    }
                }
            };
            xhr.send();
        } catch(e) {
            console.log(e.message);
        }
    }

    construct.prototype = {
        init: init,
        search: search
    };

    return construct;

})();

petrusSearch = new PS();