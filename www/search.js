Date.prototype.getWeekNumber = function(){
  var d = new Date(Date.UTC(this.getFullYear(), this.getMonth(), this.getDate()));
  var dayNum = d.getUTCDay() || 7;
  d.setUTCDate(d.getUTCDate() + 4 - dayNum);
  var yearStart = new Date(Date.UTC(d.getUTCFullYear(),0,1));
  return Math.ceil((((d - yearStart) / 86400000) + 1)/7)
};

var petrusSearch;

PS = (function(window, document, $) {

    'use strict';

    var self, weeks;

    var construct = function() {
        self = this;
        weeks = {
            'year': 53,
            'quarter': 13,
            'month': 4
        };
        self.init();
    };

    function init() {
        $('input[type=text]').focus();
        self.info();
    };

    function toggleWeekFunction(obj) {
        $('#graph-options span.selected').removeClass('selected');
        $(obj).toggleClass('selected');
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
                    if(typeof result.items[0].ticket_type_calendar != 'undefined') {
                        self.renderTypeGraph(result.items[0].ticket_type_calendar);
                        self.renderPieChart(result.items[0].ticket_type_calendar);
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

    function darkmode() {
        $('body').toggleClass('dark');
        self.info();
    };

    function renderTypeGraph(ticket_type_calendar) {
        $('#diagram').html('');
        var max_weeks = weeks['quarter'];
        var week_function = $('#graph-options .selected').attr('data-function');
        if(week_function in weeks) {
            max_weeks = weeks[week_function];
        }
        var is_dark = $('body').hasClass('dark');
        var color = is_dark ? 'magenta' : 'beige';
        var support_color = is_dark ? 'purple' : 'lightblue';
        var week_count = Object.keys(ticket_type_calendar).length;
        var start_week = week_count - max_weeks;
        var data = [];
        var x_pos_cur = 0;
        var x_neg_cur = week_count *(-1);
        var x_start = week_count *(-1);
        var x_end = 0;
        var y_max = 0;
        for(var calendar_week in ticket_type_calendar) {
            x_pos_cur += 1;
            x_neg_cur += 1;
            if(x_pos_cur >= start_week) {
                var y_cur = 0;
                var ci_right = 0;
                var ci_left = 0;
                for(var ticket_type in ticket_type_calendar[calendar_week]) {
                    y_cur += ticket_type_calendar[calendar_week][ticket_type];
                }
                if(typeof ticket_type_calendar[calendar_week]['Bug'] != 'undefined') {
                    ci_left = ticket_type_calendar[calendar_week]['Bug'];
                }
                if(typeof ticket_type_calendar[calendar_week]['Support'] != 'undefined') {
                    ci_right = ticket_type_calendar[calendar_week]['Support'] + ci_left;
                }
                if(y_cur > y_max) {
                    y_max = y_cur;
                }
                data.push({
                    'x': x_neg_cur,
                    'y': y_cur,
                    'CI_left': ci_left,
                    'CI_right': ci_right
                });
            }
            if(x_pos_cur <= start_week) {
                x_start += 1;
            }
        }

        // set the dimensions and margins of the graph
        var margin = {top: 10, right: 30, bottom: 30, left: 60},
            width = 600 - margin.left - margin.right,
            height = 280 - margin.top - margin.bottom;

        // append the svg object to the body of the page
        var svg = d3.select("#diagram")
          .append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
          .append("g")
            .attr("transform",
                  "translate(" + margin.left + "," + margin.top + ")");

        // Add X axis --> it is a date format
        var x = d3.scaleLinear()
          .domain([x_start,x_end])
          .range([ 0, width ]);
        svg.append("g")
            .style('stroke', color)
          .attr("transform", "translate(0," + height + ")")
          .call(d3.axisBottom(x));

        // Add Y axis
        var y = d3.scaleLinear()
          .domain([0, y_max])
          .range([ height, 0 ]);
        svg.append("g")
            .style('stroke', color)
          .call(d3.axisLeft(y));

        // Show confidence interval
        svg.append("path")
          .datum(data)
          .attr("fill", support_color)
          .attr("stroke", "none")
          .attr("d", d3.area()
            .x(function(d) { return x(d.x) })
            .y0(function(d) { return y(d.CI_right) })
            .y1(function(d) { return y(d.CI_left) })
            )

        // Add the line
        svg
          .append("path")
          .datum(data)
          .attr("fill", "none")
          .attr("stroke", color)
          .attr("stroke-width", 4)
          .attr("d", d3.line()
            .x(function(d) { return x(d.x) })
            .y(function(d) { return y(d.y) })
            )

    };

    function renderPieChart(ticket_type_calendar) {
        $('#stats_graph').html('');

        var is_dark = $('body').hasClass('dark');
        var main_color = is_dark ? 'magenta' : 'beige';
        var support_color = is_dark ? 'purple' : 'lightblue';
        var bugs = 0;
        var support = 0;
        var support_percentage = 0;

        var calendar_week = new Date().getWeekNumber();
        var calendar_year = new Date().getFullYear();
        var calendar_label = calendar_year + '.' + calendar_week;
        if(typeof ticket_type_calendar[calendar_label] != 'undefined') {
            if(typeof ticket_type_calendar[calendar_label]['Bug'] != 'undefined') {
                bugs = ticket_type_calendar[calendar_label]['Bug'];
            }
            if(typeof ticket_type_calendar[calendar_label]['Support'] != 'undefined') {
                support = ticket_type_calendar[calendar_label]['Support'];
            }
        }
        if(bugs > 0 && support > 0) {
            support_percentage = Math.ceil((support / (bugs + support) * 100));
        }
        $('#stats h3').html(calendar_label + '<br />' + support_percentage + '% Support');

        // set the dimensions and margins of the graph
        var width = 200,
            height = 220,
            margin = 20;

        // The radius of the pieplot is half the width or half the height (smallest one). I subtract a bit of margin.
        var radius = Math.min(width, height) / 2 - margin;

        // append the svg object to the div called 'my_dataviz'
        var svg = d3.select("#stats_graph")
          .append("svg")
            .attr("width", width)
            .attr("height", height)
          .append("g")
            .attr("transform", "translate(" + width / 2 + "," + height / 2 + ")");

        // Create dummy data
        var data = {a: support, b: bugs}

        // set the color scale
        var color = d3.scaleOrdinal()
          .domain(data)
          .range([support_color, "#00000000"])

        // Compute the position of each group on the pie:
        var pie = d3.pie()
          .value(function(d) {return d.value; })
        var data_ready = pie(d3.entries(data))

        // Build the pie chart: Basically, each part of the pie is a path that we build using the arc function.
        svg
          .selectAll('whatever')
          .data(data_ready)
          .enter()
          .append('path')
          .attr('d', d3.arc()
            .innerRadius(0)
            .outerRadius(radius)
          )
          .attr('fill', function(d){ return(color(d.data.key)) })
          .attr("stroke", main_color)
          .style("stroke-width", "2px")
          .style("opacity", 1)
    };

    construct.prototype = {
        init: init,
        search: search,
        info: info,
        darkmode: darkmode,
        renderTypeGraph: renderTypeGraph,
        renderPieChart: renderPieChart,
        toggleWeekFunction: toggleWeekFunction
    };

    return construct;

})(window, document, jQuery);

petrusSearch = new PS();