$.get("word_cloud.json", function(wc) {

    var links = [];
    var nodes = [];
    var existing_nodes = [];
    var max_weight = 0;
    var word_cloud = JSON.parse(wc);
    for(var i in word_cloud) {
        var relation = word_cloud[i];
        if(relation.weight > max_weight)
            max_weight = relation.weight;
        if(existing_nodes.indexOf(relation.source) == -1) {
            existing_nodes.push(relation.source);
            nodes.push({'name': relation.source, 'weight': relation.weight});
        }
        link = {
            'source': relation.source,
            'target': relation.target
        }
        links.push(link);
    }

    var canvas = document.querySelector("canvas"),
        context = canvas.getContext("2d"),
        width = canvas.width,
        height = canvas.height;

    var simulation = d3.forceSimulation()
        .force("link", d3.forceLink().id(function(d) { return d.name; }).strength(0.001))
        .force("charge", d3.forceManyBody())
        .force("center", d3.forceCenter(width / 2, height / 2));

    simulation
      .nodes(nodes)
      .on("tick", ticked);

    simulation.force("link")
      .links(links);

    function ticked() {
        context.clearRect(0, 0, width, height);

        context.beginPath();
        links.forEach(drawLink);
        context.strokeStyle = "#8df";
        context.stroke();

        context.beginPath();
        nodes.forEach(drawNode);
        context.fill();
        context.strokeStyle = "#fff";
        context.stroke();
    }

    function drawLink(d) {
      context.moveTo(d.source.x, d.source.y);
      context.lineTo(d.target.x, d.target.y);
    }

    function drawNode(d) {
      var node_size = d.weight / max_weight;
      var font_size = Math.max((node_size * 40), 10);
      context.moveTo(d.x + 3, d.y);
      context.arc(d.x, d.y, node_size, 0, 2 * Math.PI);
      context.font = font_size + "px Arial bold";
      context.fillStyle = 'rgba(0,0,0,0.75)';
      context.fillText(d.name, d.x+3, d.y+3);
    }


});