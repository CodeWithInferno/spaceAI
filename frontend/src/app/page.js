"use client";

import { useEffect, useRef } from "react";
import dynamic from "next/dynamic";

// Dynamically import Plotly to avoid SSR issues
const Plotly = dynamic(() => import("plotly.js-dist-min"), { ssr: false });

export default function SatelliteTracker() {
  const plotRef = useRef(null);

  useEffect(() => {
    const r = 6371;

    // Generate spherical coordinates manually (no numeric needed)
    const theta = [];
    const phi = [];
    const n = 100;
    for (let i = 0; i < n; i++) {
      theta.push((i / (n - 1)) * 2 * Math.PI);
      phi.push((i / (n - 1)) * Math.PI);
    }

    const x = [], y = [], z = [];
    for (let i = 0; i < n; i++) {
      x[i] = [];
      y[i] = [];
      z[i] = [];
      for (let j = 0; j < n; j++) {
        x[i][j] = r * Math.sin(phi[i]) * Math.cos(theta[j]);
        y[i][j] = r * Math.sin(phi[i]) * Math.sin(theta[j]);
        z[i][j] = r * Math.cos(phi[i]);
      }
    }

    const surface = {
      type: "surface",
      x, y, z,
      colorscale: "Earth",
      showscale: false,
      opacity: 1,
      lighting: { diffuse: 1, specular: 0.5 },
      lightposition: { x: 100, y: 200, z: 0 },
      hoverinfo: "skip",
    };

    const sat = {
      x: [0], y: [0], z: [0],
      mode: "markers",
      marker: { size: 6, color: "red" },
      type: "scatter3d",
      name: "Satellite",
    };

    const layout = {
      scene: {
        xaxis: { visible: false },
        yaxis: { visible: false },
        zaxis: { visible: false },
        aspectmode: "data",
        bgcolor: "black",
        camera: { eye: { x: 1.8, y: 1.8, z: 1.2 } }
      },
      margin: { l: 0, r: 0, t: 30, b: 0 },
      paper_bgcolor: "black",
      font: { color: "white" },
      title: "🌍 Satellite Tracker"
    };

    Plotly.newPlot(plotRef.current, [surface, sat], layout);

    const update = async () => {
      try {
        const res = await fetch("http://localhost:5000/data");
        const data = await res.json();
        Plotly.restyle(plotRef.current, {
          x: [[data.x]],
          y: [[data.y]],
          z: [[data.z]],
        }, [1]);
        Plotly.relayout(plotRef.current, { "title.text": `🌍 Step ${data.step}` });
      } catch (err) {
        console.error("Failed to update satellite position:", err);
      }
    };

    const interval = setInterval(update, 2000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div style={{ background: "black", height: "100vh", width: "100vw" }}>
      <div ref={plotRef} style={{ width: "100%", height: "100%" }} />
    </div>
  );
}
