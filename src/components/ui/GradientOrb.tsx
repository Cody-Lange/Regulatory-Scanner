interface GradientOrbProps {
  color: string;
  size: string;
  top?: string;
  left?: string;
  right?: string;
  bottom?: string;
  blur?: number;
  opacity?: number;
  animate?: boolean;
}

export const GradientOrb = ({
  color,
  size,
  top,
  left,
  right,
  bottom,
  blur = 80,
  opacity = 0.5,
  animate = true,
}: GradientOrbProps) => (
  <div
    className={`absolute rounded-full pointer-events-none ${animate ? 'animate-float' : ''}`}
    style={{
      background: `radial-gradient(circle, ${color} 0%, transparent 70%)`,
      width: size,
      height: size,
      top,
      left,
      right,
      bottom,
      filter: `blur(${blur}px)`,
      opacity,
    }}
  />
);
