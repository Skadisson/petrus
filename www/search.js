var petrusSearch;

PS = (function(window, document, $) {

    'use strict';

    var self;

    var construct = function() {
        self = this;
        self.init();
    };

    function init() {
        $('input[type=text]').focus();
        self.info();
    };

    function info() {
        var getUrl = 'http://192.168.6.152:55888/?function=Info';
        var formContentType = 'application/x-www-form-urlencoded';
        try {
            var xhr = new XMLHttpRequest();
            xhr.open('GET', getUrl, true);
            xhr.setRequestHeader('Content-type', formContentType);
            xhr.onreadystatechange = function() {
                if(xhr.responseText) {
                    $('#ticket-count').html('');
                    var result = JSON.parse(xhr.responseText);
                    if(typeof result.items[0].ticket_count != 'undefined') {
                        $('#ticket-count').html(result.items[0].ticket_count);
                    }
                }
            };
            xhr.send();
        } catch(e) {
            console.log(e.message);
        }
    };

    function search() {
        $('body').css('cursor', 'wait');
        $('#link-list').html('<p>loading ...</p>').fadeIn();
        $('#search').css({'top': '50%', 'margin-top': '-200px'});
        var keywords = $('#keywords').val();
        var getUrl = 'http://192.168.6.152:55888/?function=Search&keywords=' + encodeURIComponent(keywords);
        var formContentType = 'application/x-www-form-urlencoded';
        try {
            var xhr = new XMLHttpRequest();
            xhr.open('GET', getUrl, true);
            xhr.setRequestHeader('Content-type', formContentType);
            xhr.onreadystatechange = function() {
                if(xhr.responseText) {
                    $('body').css('cursor', 'auto');
                    $('#link-list').html('');
                    var result = JSON.parse(xhr.responseText);
                    if(typeof result.items[0].relevancy != 'undefined') {
                        if(result.items[0].relevancy.length == 0) {
                            $('#search').css({'top': '50%', 'margin-top': '-200px'});
                            if(keywords != '') {
                                $('#link-list').append('<p>Nothing was found</p>').fadeIn();
                            }
                            self.info();
                        } else {
                            $('#ticket-count').html(result.items[0].relevancy.length);
                            $('#search').css({'top': '0%', 'margin-top': '0px'});
                        }
                        for(var index in result.items[0].relevancy) {
                            var item = result.items[0].relevancy[index];
                            $('#link-list').append('<p><a href="' + item.link + '" target="_blank">' + item.title + ' (' + Math.round(item.percentage) + ' %)</a></p>').fadeIn();
                        }
                    } else {
                        $('#search').css({'top': '50%', 'margin-top': '-200px'});
                        $('#link-list').append('<p>Ticket "' + result.items[0].ticket.Title + '" estimate is ' + (result.items[0].estimation/60/60) + ' h</p>');
                    }
                }
            };
            xhr.send();
        } catch(e) {
            console.log(e.message);
        }
    };

    construct.prototype = {
        init: init,
        search: search,
        info: info
    };

    return construct;

})(window, document, jQuery);

petrusSearch = new PS();