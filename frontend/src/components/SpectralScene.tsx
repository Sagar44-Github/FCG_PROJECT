import { Canvas } from '@react-three/fiber'
import type { ThreeEvent } from '@react-three/fiber'
import { ContactShadows, OrbitControls, useGLTF } from '@react-three/drei'
import { Component, Suspense, useEffect, useMemo, useState } from 'react'
import type { ErrorInfo, ReactNode } from 'react'
import * as THREE from 'three'
import type { ColourId, IlluminationId, ProjectConfiguration } from '../lib/types'

const MODEL_URL = '/assets/supermarket/verdant_market.glb'
// Distinct RGB teaching presets make the live light switch easy to see.
// They are not measured or spectrally accurate lamp renderings; colour science
// remains in the Python pipeline.
const lighting = {
  L1: { key: '#fff5df', fill: '#dce7f7', ambient: '#edf0f2', environment: '#0b1112', keyPower: 3.7, fillPower: 1.0, spotPower: 34 },
  L2: { key: '#ffd28c', fill: '#d8b991', ambient: '#e4cda9', environment: '#17120d', keyPower: 3.6, fillPower: 0.72, spotPower: 32 },
  L3: { key: '#ff9b4a', fill: '#cb7545', ambient: '#d9a071', environment: '#1b1009', keyPower: 3.5, fillPower: 0.48, spotPower: 30 },
} satisfies Record<IlluminationId, { key: string; fill: string; ambient: string; environment: string; keyPower: number; fillPower: number; spotPower: number }>
const idPattern = /Q3_LABEL_([GYOR])_PANEL/

function labelFromObject(target: THREE.Object3D): ColourId | undefined {
  let current: THREE.Object3D | null = target
  while (current) {
    const match = idPattern.exec(current.name)
    const colour = current.userData.colour_id ?? match?.[1]
    if (colour === 'G' || colour === 'Y' || colour === 'O' || colour === 'R') return colour
    current = current.parent
  }
  return undefined
}

function RetailShelf({ selectedColor, onSelect }: { selectedColor: ColourId; onSelect: (id: ColourId) => void }) {
  const { scene } = useGLTF(MODEL_URL)
  const model = useMemo(() => {
    const clone = scene.clone(true)
    clone.traverse((object) => {
      if (!(object instanceof THREE.Mesh)) return
      const nameMatch = idPattern.exec(object.name)
      if (!nameMatch) return
      object.material = Array.isArray(object.material)
        ? object.material.map((material) => material.clone())
        : object.material.clone()
      object.userData.q3LabelId = nameMatch[1]
    })
    return clone
  }, [scene])

  useEffect(() => {
    model.traverse((object) => {
      if (!(object instanceof THREE.Mesh) || !object.userData.q3LabelId) return
      const isSelected = object.userData.q3LabelId === selectedColor
      const materials = Array.isArray(object.material) ? object.material : [object.material]
      materials.forEach((material) => {
        if (!('emissive' in material)) return
        const standard = material as THREE.MeshStandardMaterial
        const swatch = { G: '#3cc76c', Y: '#ffd23f', O: '#ff8b36', R: '#ff443b' }[selectedColor]
        standard.emissive.set(isSelected ? swatch : '#000000')
        standard.emissiveIntensity = isSelected ? 0.18 : 0
        standard.needsUpdate = true
      })
    })
  }, [model, selectedColor])

  function handlePointer(event: ThreeEvent<PointerEvent>) {
    const colour = labelFromObject(event.object)
    if (!colour) return
    event.stopPropagation()
    onSelect(colour)
  }

  function handleHover(event: ThreeEvent<PointerEvent>) {
    if (labelFromObject(event.object)) document.body.style.cursor = 'pointer'
  }

  function handleOut() { document.body.style.cursor = '' }

  return <>
    <primitive object={model} onPointerDown={handlePointer} onPointerOver={handleHover} onPointerOut={handleOut} />
    <ContactShadows position={[0, 0.005, 0]} opacity={0.27} scale={14} blur={2.4} far={6} resolution={256} />
    <OrbitControls makeDefault target={[0, 2.0, 0]} enablePan={false} enableDamping dampingFactor={0.08} minDistance={6.0} maxDistance={21} minPolarAngle={0.38} maxPolarAngle={1.47} autoRotate={false} />
  </>
}

/* Kept as a separate, low-cost light rig so condition changes stay in sync with
 * the scene controls without mutating any of the exported material data. */
function RetailIlluminant({ selectedIllumination }: { selectedIllumination: IlluminationId }) {
  const preset = lighting[selectedIllumination]
  return <>
    <color attach="background" args={[preset.environment]} />
    <fog attach="fog" args={[preset.environment, 15, 34]} />
    <ambientLight intensity={selectedIllumination === 'L3' ? 0.35 : 0.55} color={preset.ambient} />
    <hemisphereLight args={[preset.key, selectedIllumination === 'L1' ? '#3f493b' : '#4b2e1b', 0.85]} />
    <directionalLight position={[-6, 11, 9]} intensity={preset.keyPower} color={preset.key} />
    <directionalLight position={[8, 6, -5]} intensity={preset.fillPower} color={preset.fill} />
    <spotLight position={[0, 8, 5]} intensity={preset.spotPower} angle={0.68} penumbra={0.72} color={preset.key} castShadow={false} />
    <pointLight position={[0, 5.5, 2.5]} intensity={selectedIllumination === 'L1' ? 2.5 : 4.0} distance={15} color={preset.key} />
  </>
}

class SceneBoundary extends Component<{ children: ReactNode; fallback: ReactNode }, { failed: boolean }> {
  state = { failed: false }
  static getDerivedStateFromError() { return { failed: true } }
  componentDidCatch(error: Error, info: ErrorInfo) { console.warn('WebGL scene unavailable; using render preview fallback.', error, info.componentStack) }
  render() { return this.state.failed ? this.props.fallback : this.props.children }
}

export function SpectralScene({ config, selectedColor, selectedIllumination, onSelect, fallbackUrl }: {
  config: ProjectConfiguration; selectedColor: ColourId; selectedIllumination: IlluminationId; onSelect: (id: ColourId) => void; fallbackUrl?: string
}) {
  const [webglAvailable, setWebglAvailable] = useState<boolean | null>(null)
  useEffect(() => {
    try {
      const canvas = document.createElement('canvas')
      setWebglAvailable(Boolean(canvas.getContext('webgl2') || canvas.getContext('webgl') || canvas.getContext('experimental-webgl')))
    } catch { setWebglAvailable(false) }
  }, [])
  const imageFallback = <div className="scene-fallback">{fallbackUrl ? <img src={fallbackUrl} alt={`${config.colours[selectedColor].name} label under ${config.illuminations[selectedIllumination].name}`} /> : <div className="scene-fallback__placeholder">Interactive model unavailable · Blender render preview is available in the evidence gallery.</div>}</div>
  if (webglAvailable === false) return imageFallback
  return <SceneBoundary fallback={imageFallback}>
    <div className="scene-canvas-wrap">
      <Suspense fallback={<div className="scene-fallback__placeholder">Loading the Blender shelf model…</div>}>
        <Canvas dpr={[1, 1.35]} frameloop="demand" camera={{ position: [7.0, 5.4, 8.0], fov: 38, near: .1, far: 100 }} shadows={false} gl={{ antialias: true, powerPreference: 'high-performance', alpha: false, toneMapping: THREE.ACESFilmicToneMapping }}>
          <RetailShelf selectedColor={selectedColor} onSelect={onSelect} />
          <RetailIlluminant selectedIllumination={selectedIllumination} />
        </Canvas>
      </Suspense>
      <div className="scene-instruction"><span>DRAG TO ORBIT</span><i /><span>SCROLL TO ZOOM</span></div>
      <div className="scene-hud"><span>VERDANT MARKET · BLENDER ASSET</span><b>{selectedColor} / {selectedIllumination}</b></div>
    </div>
  </SceneBoundary>
}

useGLTF.preload(MODEL_URL)
