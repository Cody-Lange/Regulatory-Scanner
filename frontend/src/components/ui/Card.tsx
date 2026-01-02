interface CardProps {
  children: React.ReactNode;
  className?: string;
  hover?: boolean;
  gradient?: boolean;
}

export const Card = ({ children, className = '', hover = true, gradient = false }: CardProps) => {
  const baseStyles = "glass-card p-6 md:p-8";
  const hoverStyles = hover ? "hover:bg-white/12 hover:-translate-y-1 transition-all duration-300" : "";
  const gradientBorder = gradient ? "border-t-2 border-t-accent-blue" : "";

  return (
    <div className={`${baseStyles} ${hoverStyles} ${gradientBorder} ${className}`}>
      {children}
    </div>
  );
};
