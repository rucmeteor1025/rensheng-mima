import { useEffect, useRef } from "react";
import * as THREE from "three";

const SYMBOLS = [
  "甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸",
  "子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥",
  "紫微", "天府", "七杀", "破军", "贪狼", "武曲", "太阳", "太阴"
];

type TileState = {
  x: number;
  y: number;
  delay: number;
  progress: number;
  flipping: boolean;
  duration: number;
  nextFlip: number;
};

function easeInOutCubic(t: number) {
  return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
}

function makeTextTexture(text: string) {
  const canvas = document.createElement("canvas");
  canvas.width = 256;
  canvas.height = 128;
  const ctx = canvas.getContext("2d");
  if (!ctx) return new THREE.CanvasTexture(canvas);
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = "rgba(253,246,227,0.86)";
  ctx.font = text.length > 2 ? "700 34px Noto Serif SC, serif" : "900 58px Noto Serif SC, serif";
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.fillText(text, canvas.width / 2, canvas.height / 2 + 2);
  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.SRGBColorSpace;
  return texture;
}

export function HeroMatrix() {
  const mountRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const mount = mountRef.current;
    if (!mount) return;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(45, 1, 0.1, 80);
    camera.position.set(0, 0, 18);

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setClearColor(0x050401, 0);
    mount.appendChild(renderer.domElement);

    const cols = 20;
    const rows = 14;
    const count = cols * rows;
    const geometry = new THREE.PlaneGeometry(0.82, 0.52, 1, 1);
    const material = new THREE.MeshBasicMaterial({
      color: 0xffb627,
      transparent: true,
      opacity: 0.16,
      side: THREE.DoubleSide
    });
    const mesh = new THREE.InstancedMesh(geometry, material, count);
    scene.add(mesh);

    const glyphGroup = new THREE.Group();
    const textures = SYMBOLS.map(makeTextTexture);
    const sprites: THREE.Sprite[] = [];
    scene.add(glyphGroup);

    const tiles: TileState[] = [];
    const matrix = new THREE.Matrix4();
    const position = new THREE.Vector3();
    const quaternion = new THREE.Quaternion();
    const scale = new THREE.Vector3(1, 1, 1);
    const euler = new THREE.Euler();

    for (let row = 0; row < rows; row += 1) {
      for (let col = 0; col < cols; col += 1) {
        const index = row * cols + col;
        const x = (col - cols / 2) * 0.95 + 0.48;
        const y = (rows / 2 - row) * 0.66 - 0.34;
        tiles[index] = {
          x,
          y,
          delay: Math.random() * 4,
          progress: 0,
          flipping: false,
          duration: 0.9 + Math.random() * 0.55,
          nextFlip: 0.8 + Math.random() * 5
        };
        const sprite = new THREE.Sprite(new THREE.SpriteMaterial({
          map: textures[index % textures.length],
          transparent: true,
          opacity: 0.34,
          depthWrite: false
        }));
        sprite.position.set(x, y, 0.04);
        sprite.scale.set(0.66, 0.32, 1);
        glyphGroup.add(sprite);
        sprites[index] = sprite;
      }
    }

    const resize = () => {
      const width = mount.clientWidth || window.innerWidth;
      const height = mount.clientHeight || window.innerHeight;
      renderer.setSize(width, height, false);
      camera.aspect = width / height;
      camera.position.z = width < 640 ? 22 : 17;
      camera.updateProjectionMatrix();
    };
    resize();
    window.addEventListener("resize", resize);

    const clock = new THREE.Clock();
    let raf = 0;

    const animate = () => {
      const delta = clock.getDelta();
      tiles.forEach((tile, index) => {
        tile.delay -= delta;
        if (!tile.flipping && tile.delay <= 0) {
          tile.flipping = true;
          tile.progress = 0;
          tile.duration = 0.75 + Math.random() * 0.65;
        }
        if (tile.flipping) {
          tile.progress += delta / tile.duration;
          if (tile.progress >= 1) {
            tile.flipping = false;
            tile.progress = 0;
            tile.delay = tile.nextFlip + Math.random() * 4.5;
          }
        }
        const eased = tile.flipping ? easeInOutCubic(Math.min(tile.progress, 1)) : 0;
        const rotY = eased * Math.PI;
        const z = tile.flipping ? Math.sin(eased * Math.PI) * 0.8 : 0;
        const wave = Math.sin(clock.elapsedTime * 0.25 + index * 0.07) * 0.05;
        position.set(tile.x, tile.y, z + wave);
        euler.set(-0.18, rotY, 0.02 * Math.sin(index));
        quaternion.setFromEuler(euler);
        matrix.compose(position, quaternion, scale);
        mesh.setMatrixAt(index, matrix);
        const sprite = sprites[index];
        sprite.position.set(tile.x, tile.y, z + 0.08);
        sprite.rotation.y = rotY;
        (sprite.material as THREE.SpriteMaterial).opacity = tile.flipping ? 0.12 + 0.34 * Math.abs(Math.cos(rotY)) : 0.34;
      });
      mesh.instanceMatrix.needsUpdate = true;
      mesh.rotation.z = Math.sin(clock.elapsedTime * 0.12) * 0.015;
      glyphGroup.rotation.z = mesh.rotation.z;
      renderer.render(scene, camera);
      raf = requestAnimationFrame(animate);
    };
    animate();

    return () => {
      cancelAnimationFrame(raf);
      window.removeEventListener("resize", resize);
      textures.forEach((texture) => texture.dispose());
      geometry.dispose();
      material.dispose();
      renderer.dispose();
      mount.removeChild(renderer.domElement);
    };
  }, []);

  return <div ref={mountRef} className="absolute inset-0" aria-hidden="true" />;
}
