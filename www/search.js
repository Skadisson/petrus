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
                    $('#keywords').attr('placeholder', '');
                    var result = JSON.parse(xhr.responseText);
                    if(typeof result.items[0].ticket_count != 'undefined') {
                        $('#keywords').attr('placeholder', result.items[0].ticket_count + " Tickets");
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
        $('#link-list').html('<p id="single">loading ...</p>').fadeIn();
        $('#search').css({'top': '50%', 'margin-top': '-100px'});
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
                            $('#search').css({'top': '50%', 'margin-top': '-100px'});
                            if(keywords != '') {
                                $('#link-list').append('<p id="single">Nothing was found</p>').fadeIn();
                            }
                            self.info();
                        } else {
                            $('#keywords').attr('placeholder', result.items[0].relevancy.length + " Results");
                            $('#search').css({'top': '0%', 'margin-top': '0px'});
                        }
                        for(var index in result.items[0].relevancy) {
                            var item = result.items[0].relevancy[index];
                            $('#link-list').append('<p><a href="' + item.link + '" target="_blank">' + item.title + ' (' + Math.round(item.percentage) + ' %)</a></p>').fadeIn();
                        }
                    } else {
                        $('#search').css({'top': '50%', 'margin-top': '-100px'});
                        var hours = result.items[0].estimation/60/60;
                        var cssClass = hours <= 2 ? 'green' : (hours <= 4 ? 'yellow' : 'red');
                        $('#link-list').append('<p id="single">Ticket "' + result.items[0].ticket.Title + '" estimate is ' + hours + ' h <span class="corner ' + cssClass + '">&nbsp;</span></p>');
                        self.info();
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