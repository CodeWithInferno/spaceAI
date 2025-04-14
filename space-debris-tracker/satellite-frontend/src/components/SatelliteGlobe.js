"use client"

import { useRef, useState, useEffect } from "react"
import { Canvas, useFrame } from "@react-three/fiber"
import { OrbitControls } from "@react-three/drei"
import { Satellite } from "lucide-react"

// === Earth Component
function Earth() {
  const earthRef = useRef()
  useFrame(() => {
    earthRef.current.rotation.y += 0.0005 // rotate slowly
  })

  return (
    <mesh ref={earthRef}>
      <sphereGeometry args={[6371, 64, 64]} />
      <meshStandardMaterial color="#2266DD" metalness={0.1} roughness={0.7} />
    </mesh>
  )
}

// === Satellite Component
function SatelliteObject({ position }) {
  return (
    <group>
      <mesh position={position}>
        <boxGeometry args={[400, 400, 400]} />
        <meshStandardMaterial color="#FF0000" emissive="#FF0000" emissiveIntensity={0.6} />
      </mesh>

      <line>
        <bufferGeometry>
          <bufferAttribute
            attach="attributes-position"
            array={new Float32Array([0, 0, 0, ...position])}
            count={2}
            itemSize={3}
          />
        </bufferGeometry>
        <lineBasicMaterial color="#FF0000" />
      </line>
    </group>
  )
}

// === Main Component
export default function SatelliteGlobe() {
  const [satellitePos, setSatellitePos] = useState([0, 0, 8000])
  const [error, setError] = useState(null)

  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const res = await fetch("http://127.0.0.1:5000/data")
        const data = await res.json()
        setSatellitePos([data.x, data.y, data.z])
      } catch (e) {
        console.error("Fetch failed", e)
        setError("🚨 Flask server not running or data error!")
      }
    }, 2000)

    return () => clearInterval(interval)
  }, [])

  return (
    <div className="w-screen h-screen relative bg-black text-white">
      <Canvas camera={{ position: [0, 0, 16000], fov: 45 }}>
        <ambientLight intensity={0.5} />
        <pointLight position={[10000, 10000, 10000]} />
        <OrbitControls />
        <Earth />
        <SatelliteObject position={satellitePos} />
      </Canvas>

      <div className="absolute top-4 left-4 bg-black/80 backdrop-blur-md text-white p-4 rounded border border-white/20 w-64 z-10">
        <div className="flex items-center gap-2 font-semibold mb-2">
          <Satellite size={16} className="text-red-400" />
          Satellite Data
        </div>
        <div className="text-sm space-y-1">
          <div>X: {satellitePos[0].toFixed(2)} km</div>
          <div>Y: {satellitePos[1].toFixed(2)} km</div>
          <div>Z: {satellitePos[2].toFixed(2)} km</div>
          <div>
            Distance:{" "}
            {Math.sqrt(
              satellitePos[0] ** 2 + satellitePos[1] ** 2 + satellitePos[2] ** 2
            ).toFixed(2)}{" "}
            km
          </div>
        </div>
        {error && (
          <div className="mt-3 text-xs text-red-400">
            {error}
          </div>
        )}
      </div>
    </div>
  )
}
