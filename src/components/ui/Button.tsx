interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'outline';
  size?: 'sm' | 'md' | 'lg';
  children: React.ReactNode;
  onClick?: () => void;
  className?: string;
  type?: 'button' | 'submit' | 'reset';
}

export const Button = ({
  variant = 'primary',
  size = 'md',
  children,
  onClick,
  className = '',
  type = 'button',
}: ButtonProps) => {
  const baseStyles = "font-semibold rounded-lg transition-all duration-200 inline-block text-center cursor-pointer";

  const variants = {
    primary: "bg-gradient-to-r from-accent-blue to-accent-green text-white hover:opacity-90 hover:shadow-lg hover:shadow-accent-blue/25 hover:scale-105",
    secondary: "bg-white/10 text-white hover:bg-white/20",
    outline: "border-2 border-white/30 text-white hover:bg-white/10 hover:border-white/50",
  };

  const sizes = {
    sm: "px-4 py-2 text-sm",
    md: "px-6 py-3 text-base",
    lg: "px-8 py-4 text-lg",
  };

  return (
    <button
      type={type}
      className={`${baseStyles} ${variants[variant]} ${sizes[size]} ${className}`}
      onClick={onClick}
    >
      {children}
    </button>
  );
};
