// vision — graph view (vis-network)
(async function () {
  const el = document.getElementById("graph-canvas");
  if (!el || typeof vis === "undefined") return;

  const res = await fetch("/api/graph.json");
  const data = await res.json();

  // Folder colors — match config.py palette
  const folderColors = {
    projects:  "#7aa2f7",
    infra:     "#9ece6a",
    apis:      "#bb9af7",
    reference: "#e0af68",
    people:    "#f7768e",
    ideas:     "#7dcfff",
  };
  const defaultColor = "#c0caf5";

  const nodes = new vis.DataSet(
    data.nodes.map((n) => ({
      id: n.id,
      label: n.label,
      value: n.value,
      color: {
        background: folderColors[n.folder] || defaultColor,
        border: folderColors[n.folder] || defaultColor,
        highlight: { background: "#ffffff", border: "#ffffff" },
      },
      font: { color: "#d6d9e0", size: 12, face: "Inter, system-ui, sans-serif" },
    }))
  );

  const edges = new vis.DataSet(
    data.edges.map((e, i) => ({
      id: i,
      from: e.from,
      to: e.to,
      color: { color: "rgba(138, 143, 161, 0.25)", highlight: "#7dcfff" },
      smooth: { enabled: true, type: "continuous" },
      arrows: { to: { enabled: true, scaleFactor: 0.4 } },
      width: 0.7,
    }))
  );

  const network = new vis.Network(el, { nodes, edges }, {
    nodes: {
      shape: "dot",
      scaling: { min: 8, max: 32, label: { enabled: true, min: 11, max: 18 } },
      borderWidth: 0,
    },
    edges: { width: 0.6 },
    physics: {
      barnesHut: {
        gravitationalConstant: -2600,
        centralGravity: 0.12,
        springLength: 140,
        springConstant: 0.015,
        damping: 0.26,
        avoidOverlap: 0.15,
      },
      stabilization: { iterations: 280 },
    },
    interaction: { hover: true, tooltipDelay: 200, navigationButtons: false, zoomView: true },
  });

  network.on("click", (params) => {
    if (params.nodes && params.nodes.length) {
      window.location.href = `/w/${params.nodes[0]}`;
    }
  });
})();
