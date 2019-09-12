var sd;

SD = (function() {

    var self;

    var construct = function() {
        self = this;
        self.requestTrend();
    };

    function refresh(response) {
        self.rotatePointer("tickets-per-hour", response["tickets-per-hour"], 4);
        self.rotatePointer("hours-total", response["hours-total"], 400);
        self.onTheRoad(response["hot-projects"]);
        self.updateTicketsTracked(response["tickets-tracked"]);
        self.updateLabel("tickets-per-hour", response["tickets-per-hour"]);
        self.updateLabel("hours-total", response["hours-total"]);
        self.updateBars(response["payed-hours"], response["un-payed-hours"]);
        self.updateProblematicTickets(response["problematic-tickets"])
    }

    function rotatePointer(key, value, max) {
        var degree = value / max * 240 - 240 / 2;
        $('[data-js="' + key + '"] .pointer').animate({deg: degree}, {step: function(now) {$('[data-js="' + key + '"] .pointer').css({"transform": "rotate(" + now + "deg)"});}, duration: 500});
    }

    function getRandomNumber(min, max, decimals) {
        return (Math.random() * (min - max) + max).toFixed(decimals);
    }

    function onTheRoad(projects) {
        $('.cyan-light').show();
        $('.red-light').hide();
        $('.blue-light').hide();
        $('.dark').css({'opacity': 0.5});

        for(var i in projects) {
            $('.road-' + i).text(projects[i][0] + " (" + self.reduceToTwoDecimals(projects[i][1]) + " h)");
            if(parseInt(projects[i][1]) >= 20) {
                $('.road-' + i).css({'color': 'Crimson'});
                $('.cyan-light').hide();
                $('.red-light').show();
                $('.blue-light').show();
                $('.dark').css({'opacity': 1});
            } else if(parseInt(projects[i][1]) >= 10) {
                $('.road-' + i).css({'color': 'SandyBrown'});
            } else if(parseInt(projects[i][1]) >= 5) {
                $('.road-' + i).css({'color': 'Moccasin'});
            } else {
                $('.road-' + i).css({'color': 'Cornsilk'});
            }
        }

    }

    function reduceToTwoDecimals(value) {

        return (parseInt(value * 100) / 100)

    }

    function requestTrend() {

        $.get( "http://192.168.6.152:55888/", "function=Trend&months=1", function(response) {
          console.log(response);
        });
        $.get( "trend.json", function(trend) {
          self.refresh(JSON.parse(trend));
        });

    }

    function updateTicketsTracked(ticketsTracked) {

        $('[data-js="tickets-tracked"] .number').text(ticketsTracked);

    }

    function updateLabel(key, value) {

        $('[data-js="' + key + '"] .label span').text(self.reduceToTwoDecimals(value));

    }

    function updateBars(support, bugfix) {

        var sum = support + bugfix;
        var supportPercent, bugfixPercent = 0;
        if(support > 0)
            supportPercent = self.reduceToTwoDecimals(support / sum * 100);
        if(bugfix > 0)
            bugfixPercent = self.reduceToTwoDecimals(bugfix / sum * 100);
        self.drawBar('support', supportPercent);
        self.drawBar('bugfix', bugfixPercent);

    }

    function updateProblematicTickets(problematic_tickets) {
        for(var i = 1; i <= 6; i++) {
            if(problematic_tickets.length >= i) {
                $('.ticket-' + i).html('<a href="https://jira.konmedia.com/browse/' + problematic_tickets[i][0] + '" target="_blank">' + problematic_tickets[i][0] + '</a>: ' + problematic_tickets[i][1] + ' h');
            }
        }
    }

    function drawBar(bartype, percentage) {
        var integer_percentage = parseInt(percentage);
        var decimals = parseInt((percentage-integer_percentage)*100);
        $('.bar.'+bartype).css("height", percentage + "%");
        $('.bar.'+bartype+' span').text(integer_percentage + "%");
        if(decimals) {
            $('.bar.'+bartype+' span').append("<br /><i>." + decimals + "</i>")
        }
        if(percentage < 50) {
            $('.bar.'+bartype).css("box-shadow", "none");
        }
    }

    construct.prototype = {
        refresh: refresh,
        rotatePointer: rotatePointer,
        getRandomNumber: getRandomNumber,
        onTheRoad: onTheRoad,
        requestTrend: requestTrend,
        updateTicketsTracked: updateTicketsTracked,
        updateLabel: updateLabel,
        reduceToTwoDecimals: reduceToTwoDecimals,
        updateBars: updateBars,
        drawBar: drawBar,
        updateProblematicTickets: updateProblematicTickets
    };

    return construct;

})();

sd = new SD();

function reloadMe() {
    window.location.reload();
}
function progressGo() {
    var $prog = $('progress');
    var value = $prog.val();
    var max = $prog.attr('max');
    if(value < max) {
        value += 1;
    }
    $prog.val(value);
    if(value >= max) {
        setTimeout(reloadMe, 1000);
    }
}
setInterval(progressGo, 100);