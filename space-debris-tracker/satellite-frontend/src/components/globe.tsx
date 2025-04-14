"use client"

import { useRef, useState, useEffect } from "react"
import { Canvas, useFrame, useLoader } from "@react-three/fiber"
import { OrbitControls, Stars } from "@react-three/drei"
import * as THREE from "three"
import { TextureLoader } from "three"

// Earth radius in km (for scaling)
const EARTH_RADIUS_KM = 6371
// Scale factor to convert km to our 3D units (our Earth has radius 3.5)
const SCALE_FACTOR = 3.5 / EARTH_RADIUS_KM

// Type for position data from API
interface PositionData {
  x: number
  y: number
  z: number
  step: number
}

function Satellite({ positionData }: { positionData: PositionData | null }) {
  const satelliteRef = useRef<THREE.Mesh>(null)
  const trailRef = useRef<THREE.Object3D>(null)

  // Store previous positions for trail
  const [positions, setPositions] = useState<THREE.Vector3[]>([])

  useEffect(() => {
    if (positionData && satelliteRef.current) {
      // Scale the coordinates to fit our scene
      const x = positionData.x * SCALE_FACTOR
      const y = positionData.z * SCALE_FACTOR // Swap y and z for proper orientation
      const z = positionData.y * SCALE_FACTOR

      // Update satellite position
      satelliteRef.current.position.set(x, y, z)

      // Add current position to trail
      setPositions((prev) => {
        const newPositions = [...prev, new THREE.Vector3(x, y, z)]
        // Keep only the last 100 positions
        if (newPositions.length > 100) {
          return newPositions.slice(newPositions.length - 100)
        }
        return newPositions
      })
    }
  }, [positionData])

  if (!positionData) return null

  return (
    <group>
      {/* Satellite marker */}
      <mesh ref={satelliteRef}>
        <sphereGeometry args={[0.1, 16, 16]} />
        <meshStandardMaterial color="#ff5500" emissive="#ff3300" emissiveIntensity={0.5} />
      </mesh>

      {/* Trail effect */}
      {positions.length > 1 && (
        <line>
          <bufferGeometry>
            <bufferAttribute
              attach="attributes-position"
              count={positions.length}
              array={new Float32Array(positions.flatMap((p) => [p.x, p.y, p.z]))}
              itemSize={3}
            />
          </bufferGeometry>
          <lineBasicMaterial color="#ff5500" linewidth={1} />
        </line>
      )}
    </group>
  )
}

function Earth() {
  const earthRef = useRef<THREE.Mesh>(null)
  const [hovered, setHovered] = useState(false)

  // Load earth texture - using a map texture without white background
  const earthTexture = useLoader(TextureLoader, "/earth-blue-marble.jpg")

  // Rotate the earth
  useFrame(() => {
    if (earthRef.current && !hovered) {
      earthRef.current.rotation.y += 0.001
    }
  })

  return (
    <group>
      {/* Main Earth sphere */}
      <mesh ref={earthRef} onPointerOver={() => setHovered(true)} onPointerOut={() => setHovered(false)}>
        <sphereGeometry args={[3.5, 64, 64]} />
        <meshStandardMaterial map={earthTexture} metalness={0.2} roughness={0.8} />
      </mesh>

      {/* Atmosphere glow effect */}
      <mesh>
        <sphereGeometry args={[3.6, 64, 64]} />
        <meshStandardMaterial
          color={new THREE.Color(0x0077ff)}
          transparent={true}
          opacity={0.15}
          side={THREE.BackSide}
        />
      </mesh>
    </group>
  )
}

export default function Globe() {
  const [positionData, setPositionData] = useState<PositionData | null>(null)
  const [error, setError] = useState<string | null>(null)

  // Fetch position data from Flask backend
  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch("http://127.0.0.1:5000/data")
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`)
        }
        const data = await response.json()
        setPositionData(data)
        setError(null)
      } catch (err) {
        console.error("Error fetching position data:", err)
        setError("Failed to connect to backend. Make sure Flask server is running on localhost:5000")
      }
    }

    // Initial fetch
    fetchData()

    // Set up interval for periodic updates
    const intervalId = setInterval(fetchData, 2000) // Match UPDATE_INTERVAL from Flask

    // Clean up interval on component unmount
    return () => clearInterval(intervalId)
  }, [])

  return (
    <div className="absolute inset-0 w-full h-full">
      {error && (
        <div className="absolute top-4 left-4 z-10 bg-red-900 bg-opacity-80 text-white p-3 rounded-md">{error}</div>
      )}

      {positionData && (
        <div className="absolute top-4 right-4 z-10 bg-black bg-opacity-70 text-white p-3 rounded-md">
          <p>Step: {positionData.step}</p>
          <p>X: {positionData.x.toFixed(2)} km</p>
          <p>Y: {positionData.y.toFixed(2)} km</p>
          <p>Z: {positionData.z.toFixed(2)} km</p>
        </div>
      )}

      <Canvas camera={{ position: [0, 0, 10], fov: 45 }} dpr={[1, 2]}>
        <color attach="background" args={["#000000"]} />
        <ambientLight intensity={0.3} />
        <pointLight position={[10, 10, 10]} intensity={1.5} />
        <pointLight position={[-10, -10, -10]} intensity={0.5} color="#0077ff" />

        <Stars radius={100} depth={50} count={7000} factor={4} saturation={0} fade speed={1} />

        <Earth />
        <Satellite positionData={positionData} />

        <OrbitControls
          enableZoom={true}
          enablePan={false}
          minDistance={5}
          maxDistance={20}
          rotateSpeed={0.5}
          zoomSpeed={0.7}
        />
      </Canvas>
    </div>
  )
}

