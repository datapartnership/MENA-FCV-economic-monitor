// First undefine 'chordDiagram' so we can easily reload this file.
require.undef("chordDiagram");

define("chordDiagram", ["d3"], function (d3) {
  function draw(container, data, width, height, labels) {
    width = width || 800;
    height = height || 800;
    labels = labels || data.map((_, i) => `Group ${i}`);

    // Clear any existing content
    d3.select(container).selectAll("*").remove();

    var margin = { top: 20, right: 20, bottom: 20, left: 20 };
    var innerWidth = width - margin.left - margin.right;
    var innerHeight = height - margin.top - margin.bottom;
    var outerRadius = Math.min(innerWidth, innerHeight) * 0.5 - 40;
    var innerRadius = outerRadius - 30;

    var svg = d3
      .select(container)
      .append("svg")
      .attr("width", width)
      .attr("height", height);

    var g = svg
      .append("g")
      .attr("transform", `translate(${width / 2}, ${height / 2})`);

    // Color scale
    var color = d3.scaleOrdinal(d3.schemeCategory10);

    // Create chord layout
    var chord = d3.chord().padAngle(0.05).sortSubgroups(d3.descending);

    // Create arc generator
    var arc = d3.arc().innerRadius(innerRadius).outerRadius(outerRadius);

    // Create ribbon generator
    var ribbon = d3.ribbon().radius(innerRadius);

    // Process data - expect matrix format or convert simple data
    var matrix;
    if (Array.isArray(data) && Array.isArray(data[0])) {
      // Data is already a matrix
      matrix = data;
    } else {
      // Convert simple data to matrix format
      var nodes = [...new Set(data.flatMap((d) => [d.source, d.target]))];
      matrix = nodes.map(() => nodes.map(() => 0));

      data.forEach((d) => {
        var sourceIndex = nodes.indexOf(d.source);
        var targetIndex = nodes.indexOf(d.target);
        if (sourceIndex !== -1 && targetIndex !== -1) {
          matrix[sourceIndex][targetIndex] = d.value || 1;
        }
      });
    }

    var chords = chord(matrix);

    // Add tooltip
    var tooltip = d3
      .select("body")
      .append("div")
      .attr("class", "chord-tooltip")
      .style("position", "absolute")
      .style("visibility", "hidden")
      .style("background", "rgba(0, 0, 0, 0.8)")
      .style("color", "white")
      .style("padding", "8px")
      .style("border-radius", "4px")
      .style("font-size", "12px")
      .style("pointer-events", "none")
      .style("z-index", "1000");

    // Add groups (arcs)
    var group = g
      .append("g")
      .attr("class", "groups")
      .selectAll("g")
      .data(chords.groups)
      .enter()
      .append("g");

    group
      .append("path")
      .style("fill", function (d) {
        return color(d.index);
      })
      .style("stroke", "#000")
      .style("stroke-width", "1px")
      .style("opacity", 0.8)
      .attr("d", arc)
      .on("mouseover", function (event, d) {
        // Highlight connected chords
        g.selectAll(".ribbons path").style("opacity", function (ribbon) {
          return ribbon.source.index === d.index ||
            ribbon.target.index === d.index
            ? 0.8
            : 0.1;
        });

        tooltip
          .style("visibility", "visible")
          .html(
            `${labels[d.index]}<br/>Total Flow: ${d.value.toLocaleString()}`
          );
      })
      .on("mousemove", function (event) {
        tooltip
          .style("top", event.pageY - 10 + "px")
          .style("left", event.pageX + 10 + "px");
      })
      .on("mouseout", function () {
        // Reset opacity
        g.selectAll(".ribbons path").style("opacity", 0.7);
        tooltip.style("visibility", "hidden");
      })
      .transition()
      .duration(1000)
      .attrTween("d", function (d) {
        var i = d3.interpolate({ startAngle: 0, endAngle: 0 }, d);
        return function (t) {
          return arc(i(t));
        };
      });

    // Add group labels
    group
      .append("text")
      .each(function (d) {
        d.angle = (d.startAngle + d.endAngle) / 2;
      })
      .attr("dy", ".35em")
      .attr("transform", function (d) {
        return (
          "rotate(" +
          ((d.angle * 180) / Math.PI - 90) +
          ")" +
          "translate(" +
          (outerRadius + 10) +
          ")" +
          (d.angle > Math.PI ? "rotate(180)" : "")
        );
      })
      .style("text-anchor", function (d) {
        return d.angle > Math.PI ? "end" : null;
      })
      .style("font-size", "12px")
      .style("fill", "#333")
      .text(function (d, i) {
        return labels[i];
      });

    // Add ribbons (chords)
    var ribbons = g
      .append("g")
      .attr("class", "ribbons")
      .selectAll("path")
      .data(chords)
      .enter()
      .append("path")
      .attr("d", ribbon)
      .style("fill", function (d) {
        return color(d.source.index);
      })
      .style("stroke", "#000")
      .style("stroke-width", "0.5px")
      .style("opacity", 0.7)
      .on("mouseover", function (event, d) {
        d3.select(this).style("opacity", 1);

        tooltip
          .style("visibility", "visible")
          .html(
            `From: ${labels[d.source.index]}<br/>` +
              `To: ${labels[d.target.index]}<br/>` +
              `Migrants: ${d.source.value.toLocaleString()}`
          );
      })
      .on("mousemove", function (event) {
        tooltip
          .style("top", event.pageY - 10 + "px")
          .style("left", event.pageX + 10 + "px");
      })
      .on("mouseout", function () {
        d3.select(this).style("opacity", 0.7);
        tooltip.style("visibility", "hidden");
      })
      .on("click", function (event, d) {
        // Add click interaction - could filter or highlight specific connections
        console.log("Clicked chord:", d);
      });

    // Animate ribbons
    ribbons
      .style("opacity", 0)
      .transition()
      .delay(500)
      .duration(1000)
      .style("opacity", 0.7);

    // Add legend
    var legend = svg
      .append("g")
      .attr("class", "legend")
      .attr("transform", `translate(${width - 150}, 50)`);

    var legendItems = legend
      .selectAll(".legend-item")
      .data(chords.groups)
      .enter()
      .append("g")
      .attr("class", "legend-item")
      .attr("transform", function (d, i) {
        return `translate(0, ${i * 20})`;
      });

    legendItems
      .append("rect")
      .attr("width", 15)
      .attr("height", 15)
      .style("fill", function (d) {
        return color(d.index);
      })
      .style("stroke", "#000")
      .style("stroke-width", "1px");

    legendItems
      .append("text")
      .attr("x", 20)
      .attr("y", 12)
      .style("font-size", "12px")
      .style("fill", "#333")
      .text(function (d, i) {
        return labels[i];
      });
  }

  return draw;
});

element.append(
  "<small>&#x1F310; &#x1F517; &#x1F5FA; Loaded chord diagram &#x1F4CA; &#x1F4C8; &#x1F310;</small>"
);
