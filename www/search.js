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

    var self, weeks, mode, networkNodes, networkLinks;

    var construct = function() {
        self = this;
        weeks = {
            'year': 53,
            'half': 26,
            'quarter': 13,
            'month': 4
        };
        mode = 'opened';
        networkNodes = [];
        networkLinks = [];
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

    function toggleGraphMode(obj) {
        $('#graph-modes span.selected').removeClass('selected');
        $(obj).toggleClass('selected');
        self.info();
    };

    function info() {
        var getUrl = 'http://localhost:8100/?function=Info';
        var formContentType = 'application/x-www-form-urlencoded';
        try {
            var xhr = new XMLHttpRequest();
            xhr.open('GET', getUrl, true);
            xhr.setRequestHeader('Content-type', formContentType);
            xhr.onreadystatechange = function() {
                if(xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200 && xhr.responseText) {
                    $('#keywords').attr('placeholder', '');
                    var result = JSON.parse(xhr.responseText);
                    if(typeof result.items[0].ticket_count != 'undefined') {
                        $('#keywords').attr('placeholder', result.items[0].ticket_count + " Tickets");
                    }
                    var graph_mode = $('#graph-modes .selected').attr('data-function');
                    if(graph_mode == 'opened') {
                        $('#graph h3 b').text('New Tickets per Week');
                        if(typeof result.items[0].ticket_opened_calendar != 'undefined') {
                            self.renderTypeGraph(result.items[0].ticket_opened_calendar);
                            self.renderPieChart(result.items[0].ticket_opened_calendar);
                        }
                    } else if(graph_mode == 'closed') {
                        $('#graph h3 b').text('Closed Tickets per Week');
                        if(typeof result.items[0].ticket_closed_calendar != 'undefined') {
                            self.renderTypeGraph(result.items[0].ticket_closed_calendar);
                            self.renderPieChart(result.items[0].ticket_closed_calendar);
                        }
                    } else {
                        $('#graph h3 b').text('Hours per Week');
                        if(typeof result.items[0].ticket_effort_calendar != 'undefined') {
                            self.renderTypeGraph(result.items[0].ticket_effort_calendar);
                            self.renderPieChart(result.items[0].ticket_effort_calendar);
                        }
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
        var $keywordLogEntry = $('<li>' + keywords + '</li>');
        $('.keywords').append($keywordLogEntry);
        var getUrl = 'http://localhost:8100/?function=Search&keywords=' + encodeURIComponent(keywords);
        var formContentType = 'application/x-www-form-urlencoded';
        try {
            var xhr = new XMLHttpRequest();
            xhr.open('GET', getUrl, true);
            xhr.setRequestHeader('Content-type', formContentType);
            xhr.onreadystatechange = function() {
                if(xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200 && xhr.responseText) {
                    $keywordLogEntry.fadeOut('slow', function() {
                        $(this).remove();
                    });
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
                            $('#search').css({'top': '30%', 'margin-top': '0px'});
                        }
                        for(var index in result.items[0].relevancy) {
                            var item = result.items[0].relevancy[index];
                            var date = new Date(item.creation * 1000);
                            var $a = $('<a href="' + item.link + '" target="_blank">');
                            var $p = $('<p data-jira-id="' + item.jira_id + '">');
                            $p.append('<span class="date">' + date.getFullYear() + '/' + date.getMonth() + '/' + date.getUTCDay() + '</span>');
                            $p.append('<span class="title">' + item.title + '</span>');
                            //$p.append('<span class="relevancy">' + Math.round(item.percentage) + '%</span>');
                            $p.append('<span class="time_spent">' + Math.round(item.time_spent) + ' Stunden</span>');
                            $p.append('<span class="keywords">' + item.hits.join(', ') + '</span>')
                            $a.append($p);
                            $('#link-list').append($a);
                            $p.fadeIn();
                        }
                    } else {
                        $('#search').css({'top': '50%', 'margin-top': '-100px'});
                        var hours = Math.round(result.items[0].estimation/60/60);
                        var days_to_go = result.items[0].days_to_go;
                        var new_score = result.items[0].score.today;
                        var diff = parseInt(new_score) - parseInt($('#score').text());
                        var high_score = result.items[0].score.highest_score;
                        var highest_day = result.items[0].score.highest_day;
                        var monthly_score = result.items[0].score.monthly_score;
                        var top_month_score = result.items[0].score.top_month_score;
                        var is_positive = diff > 0;
                        for(var calendar_month in monthly_score) {
                            var month_score = monthly_score[calendar_month];
                            var month_relation = month_score / top_month_score;
                            var image_height = parseInt(50 * month_relation);
                            $('#monthly-scores').prepend('<div class="score"><img width="3" height="' + image_height + '" /><p>' + calendar_month + ':' + month_score + '</p></div>');
                        }
                        $('#scored').text((is_positive ? "+" : "") + ("" + diff + "").padStart(4, '0'));
                        if(diff != 0) {
                            if(is_positive) {
                                $('#scored').removeClass('negative');
                                $('#scored').addClass('positive');
                            } else {
                                $('#scored').addClass('negative');
                                $('#scored').removeClass('positive');
                            }
                            $('#scored').css({'opacity': 1}).animate({'opacity': 0}, 3000);
                        }
                        $('#score').text(new_score.padStart(10, '0'));
                        $('#high-score').text(highest_day + ':' + high_score.padStart(10, '0'));
                        var cssClass = hours <= 2 ? 'green' : (hours <= 4 ? 'yellow' : 'red');
                        if(days_to_go > 0) {
                            $('#link-list').append('<p id="single">Ticket '+result.items[0].ticket.Key+' "' + result.items[0].ticket.Title + '" estimate is ' + hours + ' h and might take up to ' + days_to_go + ' days till completion <span class="corner ' + cssClass + '">&nbsp;</span></p>');
                        } else {
                            $('#link-list').append('<p id="single">Ticket '+result.items[0].ticket.Key+' "' + result.items[0].ticket.Title + '" estimate is ' + hours + ' h <span class="corner ' + cssClass + '">&nbsp;</span></p>');
                        }
                        self.updateNetworkGraph(result.items[0].ticket.Key, result.items[0].similar_keys);
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

    function renderTypeGraph(ticket_calendar) {
        $('#diagram').html('');
        var max_weeks = weeks['quarter'];
        var week_function = $('#graph-options .selected').attr('data-function');
        if(week_function in weeks) {
            max_weeks = weeks[week_function];
        }
        var is_dark = $('body').hasClass('dark');
        var color = is_dark ? 'magenta' : 'beige';
        var support_color = is_dark ? 'purple' : 'lightblue';
        var week_count = Object.keys(ticket_calendar).length;
        var start_week = week_count - max_weeks;
        var data = [];
        var x_pos_cur = 0;
        var x_neg_cur = week_count *(-1);
        var x_start = week_count *(-1);
        var x_end = 0;
        var y_max = 0;
        for(var calendar_week in ticket_calendar) {
            x_pos_cur += 1;
            x_neg_cur += 1;
            if(x_pos_cur >= start_week) {
                var y_cur = 0;
                var ci_right = 0;
                var ci_left = 0;
                for(var ticket_type in ticket_calendar[calendar_week]) {
                    y_cur += ticket_calendar[calendar_week][ticket_type];
                }
                if(typeof ticket_calendar[calendar_week]['Bug'] != 'undefined') {
                    ci_left = ticket_calendar[calendar_week]['Bug'];
                }
                if(typeof ticket_calendar[calendar_week]['Support'] != 'undefined') {
                    ci_right = ticket_calendar[calendar_week]['Support'] + ci_left;
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

    function renderPieChart(ticket_calendar) {
        $('#stats_graph').html('');

        var is_dark = $('body').hasClass('dark');
        var main_color = is_dark ? 'magenta' : 'beige';
        var support_color = is_dark ? 'purple' : 'lightblue';
        var bugs = 0;
        var support = 0;
        var support_percentage = 0;

        var calendar_week = new Date().getWeekNumber();
        if(calendar_week < 10)
          calendar_week = '0' + calendar_week;
        var calendar_year = new Date().getFullYear();
        var calendar_label = calendar_year + '.' + calendar_week;
        if(typeof ticket_calendar[calendar_label] != 'undefined') {
            if(typeof ticket_calendar[calendar_label]['Bug'] != 'undefined') {
                bugs = ticket_calendar[calendar_label]['Bug'];
            }
            if(typeof ticket_calendar[calendar_label]['Support'] != 'undefined') {
                support = ticket_calendar[calendar_label]['Support'];
            }
        }
        support_percentage = 0
        if(bugs > 0 || support > 0) {
            support_percentage = bugs == 0 ? 100 : (support == 0 ? 0 : (Math.ceil((support / (bugs + support) * 100))));
        }
        var this_weeks_percentage = support_percentage + '% Support';
        $('#stats h3').html(calendar_label + '<br />' + this_weeks_percentage);

        // set the dimensions and margins of the graph
        var width = 200,
            height = 200,
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

    function downloadPNG() {
        $('.download').remove();
        var svgs = document.getElementsByTagName("svg");
        for(var i in svgs) {
            var svg = svgs[i];
            if(typeof svg == 'object') {
                var serializer = new XMLSerializer();
                var source = serializer.serializeToString(svg);
                if(!source.match(/^<svg[^>]+xmlns="http\:\/\/www\.w3\.org\/2000\/svg"/)){
                    source = source.replace(/^<svg/, '<svg xmlns="http://www.w3.org/2000/svg"');
                }
                if(!source.match(/^<svg[^>]+"http\:\/\/www\.w3\.org\/1999\/xlink"/)){
                    source = source.replace(/^<svg/, '<svg xmlns:xlink="http://www.w3.org/1999/xlink"');
                }
                source = '<?xml version="1.0" standalone="no"?>\r\n' + source;
                var url = "data:image/svg+xml;charset=utf-8,"+encodeURIComponent(source);
                $(svg).wrap('<a class="download" href="' + url + '"></a>');
            }
        }
    };

    function updateNetworkGraph(source_label, target_labels) {
        if(typeof source_label != 'undefined') {
            var labels = target_labels;
            labels.push(source_label);
            self.updateNetworkNodes(labels);
            self.updateNetworkLinks(source_label, target_labels);
            self.renderNetwork();
        }
    };

    function updateNetworkNodes(labels) {
        for(var i = 0; i < labels.length; i++) {
            var label = labels[i];
            var foundID, maxID;
            [foundID, maxID] = self.searchNetworkNodeID(label);
            if(foundID == 0) {
                networkNodes.push({
                    "id": maxID+1,
                    "name": label
                });
            }
        }
    };

    function updateNetworkLinks(source_label, target_labels) {
        var sourceID, maxID;
        [sourceID, maxID] = self.searchNetworkNodeID(source_label);
        for(var i = 0; i < target_labels.length; i++) {
            var target_label = target_labels[i];
            var targetID, maxID;
            [targetID, maxID] = self.searchNetworkNodeID(target_label);
            self.updateNetworkLink(sourceID, targetID);
        }
    };

    function searchNetworkNodeID(label) {
        var foundID = 0;
        var maxID = 0;
        for(var j = 0; j < networkNodes.length; j++) {
            var networkNode = networkNodes[j];
            if(networkNode.id > maxID) {
                maxID = networkNode.id;
            }
            if(networkNode.name == label) {
                foundID = networkNode.id;
            }
        }

        return [foundID, maxID];
    };

    function updateNetworkLink(sourceID, targetID) {
        var found = false;
        for(var i = 0; i < networkLinks.length; i++) {
            var networkLink = networkLinks[i];
            if(sourceID == networkLink.source && targetID == networkLink.target) {
                found = true;
            }
        }
        if(!found) {
            networkLinks.push({
                "source": sourceID,
                "target": targetID
            });
        }
    };

    function renderNetwork() {
        // https://d3-graph-gallery.com/graph/network_basic.html

        // set the dimensions and margins of the graph
        var margin = {top: 30, right: 30, bottom: 30, left: 30},
          width = window.innerWidth - margin.left - margin.right,
          height = parseInt(window.innerHeight / 2) - margin.top - margin.bottom;

        // append the svg object to the body of the page
        $('#network svg').remove();
        var svg = d3.select("#network")
        .append("svg")
          .attr("width", width + margin.left + margin.right)
          .attr("height", height + margin.top + margin.bottom)
        .append("g")
          .attr("transform",
                "translate(" + margin.left + "," + margin.top + ")");

        if(networkNodes.length > 0) {

          // Initialize the links
          var link = svg
            .selectAll("line")
            .data(networkLinks)
            .enter()
            .append("line")
              .style("stroke", "white");

          // Initialize the nodes
          var node = svg
            .selectAll("text")
            .data(networkNodes)
            .enter()
            .append("text")
              .attr("width", 120)
              .attr("height", 40)
              .attr("font-family", "Courier New")
              .attr("font-weight", "bold")
              .attr("font-size", "14px")
              .style("fill", "black");

          // Let's list the force we wanna apply on the network
          var simulation = d3.forceSimulation(networkNodes)                 // Force algorithm is applied to data.nodes
              .force("link", d3.forceLink()                               // This force provides links between nodes
                    .id(function(d) { return d.id; })                     // This provide  the id of a node
                    .links(networkLinks)                                    // and this the list of links
              )
              .force("charge", d3.forceManyBody().strength(-400))         // This adds repulsion between nodes. Play with the -400 for the repulsion strength
              .force("center", d3.forceCenter(width / 2, height / 2))     // This force attracts nodes to the center of the svg area
              .on("end", ticked);

          // This function is run at each iteration of the force algorithm, updating the nodes position.
          function ticked() {
            link
                .attr("x1", function(d) { return d.source.x; })
                .attr("y1", function(d) { return d.source.y; })
                .attr("x2", function(d) { return d.target.x; })
                .attr("y2", function(d) { return d.target.y; });

            node
                 .attr("x", function (d) { return d.x-60; })
                 .attr("y", function(d) { return d.y; })
                 .text(function(d) { return d.name; });
          }


        }
    };

    construct.prototype = {
        init: init,
        search: search,
        info: info,
        darkmode: darkmode,
        renderTypeGraph: renderTypeGraph,
        renderPieChart: renderPieChart,
        toggleWeekFunction: toggleWeekFunction,
        toggleGraphMode: toggleGraphMode,
        downloadPNG: downloadPNG,
        updateNetworkGraph: updateNetworkGraph,
        updateNetworkNodes: updateNetworkNodes,
        updateNetworkLinks: updateNetworkLinks,
        searchNetworkNodeID: searchNetworkNodeID,
        updateNetworkLink: updateNetworkLink,
        renderNetwork: renderNetwork
    };

    return construct;

})(window, document, jQuery);

petrusSearch = new PS();