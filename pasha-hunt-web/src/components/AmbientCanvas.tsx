"use client";

import { useEffect, useRef } from "react";
import * as THREE from "three";

interface AmbientCanvasProps {
  accentColor?: string;
}

export default function AmbientCanvas({ accentColor = "#F2AA4C" }: AmbientCanvasProps) {
  const mountRef = useRef<HTMLDivElement>(null);
  const colorRef = useRef(accentColor);

  useEffect(() => {
    colorRef.current = accentColor;
  }, [accentColor]);

  useEffect(() => {
    const container = mountRef.current;
    if (!container) return;

    // Scene & Camera
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(
      60,
      window.innerWidth / window.innerHeight,
      0.1,
      1000
    );
    camera.position.z = 80;

    // Renderer
    const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true, powerPreference: "high-performance" });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.5));
    container.appendChild(renderer.domElement);

    // Particles Geometry
    const particleCount = 220;
    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(particleCount * 3);
    const scales = new Float32Array(particleCount);

    for (let i = 0; i < particleCount; i++) {
      positions[i * 3] = (Math.random() - 0.5) * 160;
      positions[i * 3 + 1] = (Math.random() - 0.5) * 100;
      positions[i * 3 + 2] = (Math.random() - 0.5) * 80;
      scales[i] = Math.random() * 2 + 1;
    }

    geometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute("scale", new THREE.BufferAttribute(scales, 1));

    // Particle Material
    const material = new THREE.PointsMaterial({
      color: new THREE.Color(colorRef.current),
      size: 1.8,
      transparent: true,
      opacity: 0.35,
      blending: THREE.AdditiveBlending,
    });

    const particles = new THREE.Points(geometry, material);
    scene.add(particles);

    // Subtle ambient connection grid lines
    const lineMaterial = new THREE.LineBasicMaterial({
      color: new THREE.Color(colorRef.current),
      transparent: true,
      opacity: 0.08,
    });

    const lineGeometry = new THREE.BufferGeometry();
    const linePositions = new Float32Array(60 * 6);
    let lineIdx = 0;
    for (let i = 0; i < 60; i++) {
      const p1 = Math.floor(Math.random() * particleCount);
      const p2 = Math.floor(Math.random() * particleCount);
      linePositions[lineIdx++] = positions[p1 * 3];
      linePositions[lineIdx++] = positions[p1 * 3 + 1];
      linePositions[lineIdx++] = positions[p1 * 3 + 2];
      linePositions[lineIdx++] = positions[p2 * 3];
      linePositions[lineIdx++] = positions[p2 * 3 + 1];
      linePositions[lineIdx++] = positions[p2 * 3 + 2];
    }
    lineGeometry.setAttribute("position", new THREE.BufferAttribute(linePositions, 3));
    const lines = new THREE.LineSegments(lineGeometry, lineMaterial);
    scene.add(lines);

    // Mouse tracking
    let mouseX = 0;
    let mouseY = 0;
    const handleMouseMove = (e: MouseEvent) => {
      mouseX = (e.clientX - window.innerWidth / 2) * 0.02;
      mouseY = (e.clientY - window.innerHeight / 2) * 0.02;
    };
    window.addEventListener("mousemove", handleMouseMove, { passive: true });

    // Window resize
    const handleResize = () => {
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
    };
    window.addEventListener("resize", handleResize);

    // Animation Loop
    let animationId: number;
    let clock = new THREE.Clock();

    const animate = () => {
      animationId = requestAnimationFrame(animate);
      const elapsed = clock.getElapsedTime();

      particles.rotation.y = elapsed * 0.02 + mouseX * 0.05;
      particles.rotation.x = mouseY * 0.05;
      lines.rotation.y = particles.rotation.y;
      lines.rotation.x = particles.rotation.x;

      // Update color if ref changed
      if (material.color.getHexString() !== new THREE.Color(colorRef.current).getHexString()) {
        material.color.set(colorRef.current);
        lineMaterial.color.set(colorRef.current);
      }

      renderer.render(scene, camera);
    };

    animate();

    return () => {
      cancelAnimationFrame(animationId);
      window.removeEventListener("mousemove", handleMouseMove);
      window.removeEventListener("resize", handleResize);
      if (container && renderer.domElement) {
        container.removeChild(renderer.domElement);
      }
      geometry.dispose();
      material.dispose();
      lineGeometry.dispose();
      lineMaterial.dispose();
      renderer.dispose();
    };
  }, []);

  return (
    <div
      ref={mountRef}
      className="pointer-events-none fixed inset-0 z-0 opacity-60"
      style={{ overflow: "hidden" }}
      aria-hidden="true"
    />
  );
}
