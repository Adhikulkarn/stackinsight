import { useState, useEffect } from "react";
import axios from "axios";
import { motion, AnimatePresence } from "framer-motion";
import * as d3 from "d3";
import {
  FaGithub,
  FaCode,
  FaRocket,
  FaChartLine,
  FaCube,
} from "react-icons/fa";

export default function AnalyzerPage() {
  const [repoUrl, setRepoUrl] = useState("");
  const [logs, setLogs] = useState([]);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [selectedNode, setSelectedNode] = useState(null);

  const handleAnalyze = async () => {
    if (!repoUrl) return;
    setLoading(true);
    setLogs(["🚀 Starting analysis..."]);

    try {
      const response = await axios.post("http://127.0.0.1:8000/api/analyze/", {
        repo_url: repoUrl,
      });

      setLogs((prev) => [...prev, "✅ Analysis complete!"]);
      setResult(response.data);
    } catch (err) {
      setLogs((prev) => [...prev, `❌ Error: ${err.message}`]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (result && result.nodes && result.links) {
      renderGraph(result);
    }
  }, [result]);

  const renderGraph = (data) => {
    d3.select("#repo-graph").selectAll("*").remove();

    const container = document.getElementById("repo-graph");
    const width = container.clientWidth;
    const height = container.clientHeight;

    const svg = d3
      .select("#repo-graph")
      .append("svg")
      .attr("width", width)
      .attr("height", height);

    const tooltip = d3
      .select("#repo-graph")
      .append("div")
      .attr("class", "absolute bg-gray-800 text-white text-xs p-2 rounded-md border border-gray-700 shadow-md z-50")
      .style("opacity", 0)
      .style("pointer-events", "none")
      .style("position", "absolute");

    const simulation = d3
      .forceSimulation(data.nodes)
      .force("link", d3.forceLink(data.links).id((d) => d.id).distance(120))
      .force("charge", d3.forceManyBody().strength(-350))
      .force("center", d3.forceCenter(width / 2, height / 2));

    const link = svg
      .append("g")
      .attr("stroke", "#666")
      .attr("stroke-opacity", 0.6)
      .selectAll("line")
      .data(data.links)
      .enter()
      .append("line")
      .attr("stroke-width", 1.5);

    const getNodeColor = (label) => {
      const lower = label.toLowerCase();
      if (lower.includes("repo")) return "#16a34a"; // green = repo
      if (
        lower.endsWith(".js") ||
        lower.endsWith(".html") ||
        lower.endsWith(".css") ||
        lower.endsWith(".py")
      )
        return "#3b82f6"; // blue = file
      return "#a855f7"; // purple = function/class
    };

    const getNodeType = (label) => {
      const lower = label.toLowerCase();
      if (lower.includes("repo")) return "📦 Repository";
      if (
        lower.endsWith(".js") ||
        lower.endsWith(".html") ||
        lower.endsWith(".css") ||
        lower.endsWith(".py")
      )
        return "🧩 File";
      return "⚙️ Function / Class";
    };

    const node = svg
      .append("g")
      .selectAll("circle")
      .data(data.nodes)
      .enter()
      .append("circle")
      .attr("r", 8)
      .attr("fill", (d) => getNodeColor(d.label))
      .attr("stroke", "#111")
      .attr("stroke-width", 1)
      .style("cursor", "pointer")
      .on("mouseover", (event, d) => {
        tooltip.transition().duration(200).style("opacity", 1);
        tooltip
          .html(`
            <div class="font-semibold text-cyan-400">${d.label}</div>
            <div class="text-gray-300 mt-1">${getNodeType(d.label)}</div>
            ${
              d.summary
                ? `<div class="text-gray-400 mt-1">${d.summary.substring(0, 120)}...</div>`
                : ""
            }
          `)
          .style("left", `${event.pageX + 10}px`)
          .style("top", `${event.pageY - 20}px`);
      })
      .on("mousemove", (event) => {
        tooltip
          .style("left", `${event.pageX + 10}px`)
          .style("top", `${event.pageY - 20}px`);
      })
      .on("mouseout", () => {
        tooltip.transition().duration(300).style("opacity", 0);
      })
      .on("click", (event, d) => {
        setSelectedNode({
          label: d.label,
          type: getNodeType(d.label),
          summary: d.summary || "No detailed summary available.",
        });
      })
      .call(
        d3
          .drag()
          .on("start", dragstarted)
          .on("drag", dragged)
          .on("end", dragended)
      );

    const label = svg
      .append("g")
      .selectAll("text")
      .data(data.nodes)
      .enter()
      .append("text")
      .text((d) => d.label)
      .attr("font-size", 10)
      .attr("fill", "#fff")
      .attr("x", 10)
      .attr("y", 3);

    simulation.on("tick", () => {
      link
        .attr("x1", (d) => d.source.x)
        .attr("y1", (d) => d.source.y)
        .attr("x2", (d) => d.target.x)
        .attr("y2", (d) => d.target.y);
      node.attr("cx", (d) => d.x).attr("cy", (d) => d.y);
      label.attr("x", (d) => d.x + 10).attr("y", (d) => d.y + 3);
    });

    function dragstarted(event, d) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      d.fx = d.x;
      d.fy = d.y;
    }

    function dragged(event, d) {
      d.fx = event.x;
      d.fy = event.y;
    }

    function dragended(event, d) {
      if (!event.active) simulation.alphaTarget(0);
      d.fx = null;
      d.fy = null;
    }
  };

  return (
    <div className="flex h-screen bg-gradient-to-br from-slate-900 via-gray-900 to-black text-white">
      {/* LEFT PANEL — Controls & Logs */}
      <div className="w-1/4 border-r border-gray-800 p-5 flex flex-col">
        <motion.h1
          initial={{ opacity: 0, y: -15 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-xl font-semibold mb-4 text-cyan-400"
        >
          ⚙️ StackInsight Controls
        </motion.h1>

        <input
          type="text"
          value={repoUrl}
          onChange={(e) => setRepoUrl(e.target.value)}
          placeholder="Enter GitHub Repo URL..."
          className="p-2 rounded-md bg-gray-800 border border-gray-700 text-white focus:border-cyan-400 outline-none"
        />
        <button
          onClick={handleAnalyze}
          disabled={loading}
          className="mt-3 bg-cyan-500 hover:bg-cyan-600 text-white font-semibold py-2 rounded-md transition disabled:opacity-50"
        >
          {loading ? "Analyzing..." : "Analyze"}
        </button>

        <div className="mt-6 flex-1 overflow-y-auto bg-gray-900/40 rounded-md border border-gray-800 p-2 text-xs">
          {logs.map((log, i) => (
            <div key={i} className="text-gray-300">
              {log}
            </div>
          ))}
        </div>
      </div>

      {/* MIDDLE PANEL — Graph Visualization */}
      <div className="flex-1 p-4 flex flex-col items-center relative">
        <h2 className="text-lg font-semibold text-cyan-400 mb-4">
          🕸️ Graph View
        </h2>
        <div
          id="repo-graph"
          className="relative bg-gray-900/30 rounded-md border border-gray-800 w-full h-full flex justify-center items-center"
        >
          {!result && (
            <p className="text-gray-600 text-sm text-center px-4">
              Graph will appear here after analysis
            </p>
          )}
        </div>
      </div>

      {/* RIGHT PANEL — Framework Info */}
      <div className="w-1/4 border-l border-gray-800 p-5 flex flex-col">
        <h2 className="text-lg font-semibold text-cyan-400 mb-4">
          🧠 Detected Frameworks
        </h2>
        {result ? (
          <div>
            <p className="text-sm text-gray-300">
              <strong>Frontend:</strong> {result.frontend_framework || "Unknown"}
              <br />
              <strong>Backend:</strong> {result.backend_framework || "Unknown"}
            </p>
          </div>
        ) : (
          <p className="text-gray-500 italic">
            Analyze a repo to detect technologies...
          </p>
        )}
      </div>

      {/* 🧩 NODE SUMMARY MODAL */}
      <AnimatePresence>
        {selectedNode && (
          <motion.div
            className="fixed inset-0 bg-black/60 flex items-center justify-center z-50"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setSelectedNode(null)}
          >
            <motion.div
              className="bg-gray-900 border border-cyan-500/30 rounded-lg p-6 max-w-md w-full mx-4 relative"
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.8, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
            >
              <h3 className="text-xl font-semibold text-cyan-400 mb-2">
                {selectedNode.label}
              </h3>
              <p className="text-sm text-gray-400 mb-4">{selectedNode.type}</p>
              <p className="text-gray-300 text-sm leading-relaxed">
                {selectedNode.summary}
              </p>
              <button
                onClick={() => setSelectedNode(null)}
                className="mt-4 bg-cyan-600 hover:bg-cyan-700 px-4 py-2 rounded-md text-sm font-semibold text-white"
              >
                ✖ Close
              </button>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
