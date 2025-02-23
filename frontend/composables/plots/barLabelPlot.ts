import * as d3 from "d3";
import { useLabelDecisionsStore } from "~/stores/sdgLabelDecisions";
import { useSDGsStore } from "~/stores/sdgs";
import { ref, watch } from "vue";

export function createBarLabelPlot(container, width, height, sortDescending) {
  const labelDecisionsStore = useLabelDecisionsStore();
  const sdgsStore = useSDGsStore();

  function updateChart() {
    if (labelDecisionsStore.selectedSDGLabelDecision && labelDecisionsStore.userLabels) {
      let labelDistribution = aggregateUserVotes(labelDecisionsStore.userLabels, labelDecisionsStore.showFinalRound);

      // Apply correct order:
      if (sortDescending) {
        labelDistribution.sort((a, b) => b.count - a.count);
      }

      if (labelDistribution.length === 0) {
        // Display "No Labels Yet" message
        displayNoLabelsMessage(container, width, height);
      } else {
        updateLabelDistributionBarPlot(container, labelDistribution, width, height, sdgsStore);
      }
    }
  }

  // Subscribe to Pinia store updates and update the plot when data changes
  labelDecisionsStore.$subscribe(() => {
    updateChart();
  });

  // Watch for store changes
  watch(() => labelDecisionsStore.showFinalRound, () => {
    updateChart();
  });

  // Watch for sortDescending changes
  watch(() => sortDescending, () => {
    updateChart();
  });

  // Initial rendering of the chart
  updateChart();
}

/**
 * Aggregates user votes, either showing all or only the latest vote per user.
 */
export function aggregateUserVotes(userLabels, showFinalRound) {
  let latestLabels = new Map();

  if (showFinalRound) {
    // Keep only the latest SDG label per user
    userLabels.forEach((label) => {
      if (
        !latestLabels.has(label.userId) ||
        new Date(label.createdAt) > new Date(latestLabels.get(label.userId).createdAt)
      ) {
        latestLabels.set(label.userId, label);
      }
    });
  }

  // Use either all labels or the latest one per user
  let filteredLabels = showFinalRound ? Array.from(latestLabels.values()) : userLabels;

  // Count votes for each SDG label
  let voteCounts = {};
  filteredLabels.forEach((label) => {
    let votedLabel = label.votedLabel;
    if ((votedLabel >= 1 && votedLabel <= 17) || votedLabel === -1) {
      voteCounts[votedLabel] = (voteCounts[votedLabel] || 0) + 1;
    }
  });

  let labelDistribution = Object.entries(voteCounts).map(([label, count]) => ({
    label: Number(label),
    count,
  }));

  return labelDistribution;
}


/**
 * Updates the D3 bar chart with new data.
 */
export function updateLabelDistributionBarPlot(container, labelDistribution, width, height, sdgsStore) {
  // Clear previous chart
  d3.select(container).selectAll('*').remove();

  const svg = d3.select(container)
    .append("svg")
    .attr("width", width)
    .attr("height", height);

  const margin = { top: 30, right: 30, bottom: 20, left: 30 };
  const chartWidth = width - margin.left - margin.right;
  const chartHeight = height - margin.top - margin.bottom;

  const g = svg.append("g").attr("transform", `translate(${margin.left},${margin.top})`);

  // X-Axis: SDG Labels
  const x = d3.scaleBand()
    .domain(labelDistribution.map(d => d.label === -1 ? 'Not relevant' : `SDG ${d.label}`))
    .range([0, chartWidth])
    .padding(0.3);

  // Y-Axis: Number of votes
  const y = d3.scaleLinear()
    .domain([0, d3.max(labelDistribution, d => d.count) || 1])
    .nice()
    .range([chartHeight, 0]);

  // Draw X-Axis
  g.append("g")
    .attr("transform", `translate(0,${chartHeight})`)
    .call(d3.axisBottom(x))
    .selectAll("text")
    .style("text-anchor", "middle");

  // Draw Y-Axis
  g.append("g")
    .call(d3.axisLeft(y).ticks(d3.max(labelDistribution, d => d.count) || 1).tickFormat(d3.format("d")));

  // Create tooltip div
  const tooltip = d3.select("body")
    .append("div")
    .attr("class", "tooltip")
    .style("opacity", 0)
    .style("pointer-events", "none")
    .style("position", "absolute")
    .style("padding", "8px")
    .style("background-color", "rgba(255, 255, 255, 0.95)")
    .style("border-radius", "4px")
    .style("font-size", "14px")
    .style("box-shadow", "0 2px 4px rgba(0, 0, 0, 0.1)");

  // Draw bars
  g.selectAll(".bar")
    .data(labelDistribution)
    .enter().append("rect")
    .attr("class", "bar")
    .attr("x", d => x(d.label === -1 ? 'Not relevant' : `SDG ${d.label}`))
    .attr("y", d => y(d.count))
    .attr("width", x.bandwidth())
    .attr("height", d => chartHeight - y(d.count))
    .attr("fill", d => d.label === -1 ? '#CCCCCC' : sdgsStore.getColorBySDG(d.label) || '#CCCCCC')
    .attr("fill-opacity", 0.8)
    .on("mouseover", function (event, d) {
      // Show tooltip
      const labelText = d.label === -1 ? "Not relevant" : `SDG ${d.label}`;
      const shortTitle = d.label === -1 ? "General" : sdgsStore.getShortTitleBySDG(d.label); // Fetch short title
      const color = d.label === -1 ? '#CCCCCC' : sdgsStore.getColorBySDG(d.label) || '#CCCCCC';

      tooltip.transition()
        .duration(200)
        .style("opacity", 1);

      tooltip.html(
        `<div style="display: flex; align-items: center;">
      <div style="width: 12px; height: 12px; background-color: ${color}; border-radius: 50%; margin-right: 8px;"></div>
      <div>
        <strong>${labelText}:</strong> ${d.count} ${d.count === 1 ? 'Label' : 'Labels'}
        <br>
        <span style="font-size: 12px; color: ${color};">${shortTitle}</span>
      </div>
    </div>`
      )
        .style("left", (event.pageX + 10) + "px")
        .style("top", (event.pageY - 28) + "px");

      // Highlight bar
      d3.select(this)
        .transition()
        .duration(200)
        .attr("fill-opacity", 1);
    })

    .on("mouseout", function () {
      // Hide tooltip properly
      tooltip.transition()
        .duration(200)
        .style("opacity", 0)
        .on("end", function () {
          tooltip.style("left", "-9999px"); // Move out of view
          tooltip.style("top", "-9999px");  // Move out of view
        });

      // Reset bar opacity
      d3.select(this)
        .transition()
        .duration(200)
        .attr("fill-opacity", 0.7);
    });


  // Update the D3 bar chart to display vote count above each bar
  g.selectAll(".label")
    .data(labelDistribution)
    .enter().append("text")
    .attr("class", "label")
    .attr("x", d => x(d.label === -1 ? 'Not relevant' : `SDG ${d.label}`) + x.bandwidth() / 2)
    .attr("y", d => y(d.count) - 5) // Position above the bar
    .attr("text-anchor", "middle")
    .attr("fill", "#000") // Keep text black for visibility
    .attr("font-size", "12px")
    .attr("font-weight", "bold")
    .text(d => d.count);
}

/**
 * Displays a "No Labels Yet" message when there are no labels in the dataset.
 */
function displayNoLabelsMessage(container, width, height) {
  d3.select(container).selectAll('*').remove(); // Clear previous chart

  const svg = d3.select(container)
    .append("svg")
    .attr("width", width)
    .attr("height", height);

  svg.append("text")
    .attr("x", width / 2)
    .attr("y", height / 2)
    .attr("text-anchor", "middle")
    .attr("font-size", "18px")
    .attr("fill", "#333")
    .text("No Labels available");
}
