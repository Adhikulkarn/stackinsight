import { useState, useEffect } from "react";
import axios from "axios";
import { motion } from "framer-motion";
import * as d3 from "d3";

export default function AnalyzerPage() {
  const [repoUrl, setRepoUrl] = useState("");
  const [logs, setLogs] = useState([]);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

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

    const width = 800;
    const height = 600;

    const svg = d3
      .select("#repo-graph")
      .append("svg")
      .attr("width", width)
      .attr("height", height);

    const simulation = d3
      .forceSimulation(data.nodes)
      .force("link", d3.forceLink(data.links).id((d) => d.id).distance(150))
      .force("charge", d3.forceManyBody().strength(-400))
      .force("center", d3.forceCenter(width / 2, height / 2));

    const link = svg
      .append("g")
      .attr("stroke", "#555")
      .attr("stroke-opacity", 0.6)
      .selectAll("line")
      .data(data.links)
      .enter()
      .append("line")
      .attr("stroke-width", 1.5);

    const node = svg
      .append("g")
      .selectAll("circle")
      .data(data.nodes)
      .enter()
      .append("circle")
      .attr("r", 8)
      .attr("fill", "#22d3ee")
      .call(
        d3.drag()
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
      .attr("font-size", 12)
      .attr("fill", "#fff")
      .attr("x", 12)
      .attr("y", 4);

    simulation.on("tick", () => {
      link
        .attr("x1", (d) => d.source.x)
        .attr("y1", (d) => d.source.y)
        .attr("x2", (d) => d.target.x)
        .attr("y2", (d) => d.target.y);

      node.attr("cx", (d) => d.x).attr("cy", (d) => d.y);
      label.attr("x", (d) => d.x + 12).attr("y", (d) => d.y + 4);
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
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-gray-900 to-black text-white flex flex-col items-center p-8">
      <motion.h1
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-4xl font-bold mb-8"
      >
        🔍 StackInsight Analyzer
      </motion.h1>

      <div className="w-full max-w-3xl bg-gray-800/40 p-6 rounded-xl border border-gray-700">
        <input
          type="text"
          value={repoUrl}
          onChange={(e) => setRepoUrl(e.target.value)}
          placeholder="Enter GitHub Repository URL..."
          className="w-full p-3 rounded-lg bg-gray-900 border border-gray-700 text-white focus:border-cyan-400 outline-none"
        />
        <button
          onClick={handleAnalyze}
          disabled={loading}
          className="mt-4 w-full bg-cyan-500 hover:bg-cyan-600 text-white font-semibold py-2 rounded-lg transition disabled:opacity-50"
        >
          {loading ? "Analyzing..." : "Analyze Repository"}
        </button>
      </div>

      {/* Logs */}
      <div className="mt-8 w-full max-w-3xl bg-black/40 p-4 rounded-xl border border-gray-800 text-sm overflow-y-auto h-48">
        {logs.map((log, i) => (
          <div key={i} className="text-gray-300">
            {log}
          </div>
        ))}
      </div>

      {/* D3 Graph */}
      <div id="repo-graph" className="mt-12 w-full flex justify-center"></div>
    </div>
  );
}
