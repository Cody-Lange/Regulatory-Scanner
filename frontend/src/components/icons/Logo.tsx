export const Logo = ({ className = '' }: { className?: string }) => {
  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <div className="text-2xl font-bold tracking-tight">
        <span className="gradient-text">SENTINEL SCAN</span>
      </div>
    </div>
  );
};
