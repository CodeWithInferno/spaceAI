"use client"

import { Suspense } from "react"
import dynamic from "next/dynamic"
import { Loader } from "@/components/loader"

// Import the Globe component dynamically to avoid SSR issues with Three.js
const Globe = dynamic(() => import("@/components/globe"), {
  ssr: false,
  loading: () => <Loader />,
})

export default function Home() {
  return (
    <main className="w-full h-screen bg-black overflow-hidden">
      <Suspense fallback={<Loader />}>
        <Globe />
      </Suspense>
    </main>
  )
}

