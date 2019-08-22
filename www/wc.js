function tick() {
  path.attr("d", linkArc);
  circle.attr("transform", transform);
  text.attr("transform", transform);
}

function linkArc(d) {
  var dx = d.target.x - d.source.x,
    dy = d.target.y - d.source.y,
    dr = Math.sqrt(dx * dx + dy * dy);
  return "M" + d.source.x + "," + d.source.y + "A" + dr + "," + dr + " 0 0,1 " + d.target.x + "," + d.target.y;
}

function transform(d) {
  return "translate(" + d.x + "," + d.y + ")";
}

$.get("word_cloud.json", function(wc) {

    var links = [];
    var nodes = {};
    var word_cloud = JSON.parse(wc);
    for(word in word_cloud.word_relations) {
        related_words = word_cloud.word_relations[word];
        for(rel_index in related_words) {
            if(word && related_words[rel_index]) {
                var word_weight = word_cloud.word_count[word];
                var related_word = related_words[rel_index];
                var related_weight = word_cloud.word_count[related_word]
                link = {
                    'source': word,
                    'target': related_word,
                    'weight': word_weight
                }
                links.source = nodes[link.source] || (nodes[link.source] = {name: link.source, weight: link.weight});
                links.target = nodes[link.target] || (nodes[link.target] = {name: link.target, weight: related_weight});
                links.push(link);
            }
        }
    }

    var width = window.innerWidth,
      height = window.innerHeight;

    var force = d3.layout.force()
      .nodes(d3.values(nodes))
      .links(links)
      .size([width, height])
      .linkDistance(100)
      .charge(-300)
      .on("tick", tick)
      .start();

    return;

    var svg = d3.select(".diagram").append("svg")
      .attr("width", width)
      .attr("height", height)
      .attr('id', 'svg')
      .call(d3.behavior.zoom().on("zoom", function () {
        svg.attr("transform", "translate(" + d3.event.translate + ")" + " scale(" + d3.event.scale + ")")
      }));

    svg.append("defs").selectAll("marker")
      .data(["suit", "licensing", "resolved"])
      .enter().append("marker")
      .attr("id", function (d) {
        return d;
      })
      .attr("viewBox", "0 -5 10 10")
      .attr("refX", 15)
      .attr("refY", -1.5)
      .attr("markerWidth", 6)
      .attr("markerHeight", 6)
      .attr("orient", "auto")
      .append("path")
      .attr("d", "M0,-5L10,0L0,5");

    var path = svg.append("g").selectAll("path")
      .data(force.links())
      .enter().append("path")
      .attr("class", "link");

    var circle = svg.append("g").selectAll("circle")
      .data(force.nodes())
      .enter().append("circle")
      .attr("r", function (d) {
        var minRadius = 0.2;
        return minRadius + (d.weight * 1.1);
      })
      .call(force.drag);

    var text = svg.append("g").selectAll("text")
      .data(force.nodes())
      .enter().append("text")
      .attr("x", 8)
      .attr("y", ".31em")
      .text(function (d) {
        return d.name;
      });

});