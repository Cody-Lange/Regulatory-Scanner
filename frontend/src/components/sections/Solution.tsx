import { Search, Eye, Shield } from 'lucide-react';

export const Solution = () => {
  const steps = [
    {
      number: '01',
      icon: <Search className="w-12 h-12 text-accent-blue" />,
      title: 'Scan',
      description: 'Install our VS Code extension or CLI tool. Sentinel Scan scans your Python code in real-time.',
    },
    {
      number: '02',
      icon: <Eye className="w-12 h-12 text-accent-green" />,
      title: 'Detect',
      description: 'AI-powered detection finds PII, VINs, PHI, and sensitive data patterns. Context-aware to reduce false positives.',
    },
    {
      number: '03',
      icon: <Shield className="w-12 h-12 text-accent-coral" />,
      title: 'Block',
      description: 'Pre-commit hooks prevent violations from reaching production. Generate audit trails for compliance teams.',
    },
  ];

  return (
    <section id="solution" className="section-padding">
      <div className="container-custom">
        <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold text-center mb-4">
          Stop Violations at the{' '}
          <span className="gradient-text">Source</span>
        </h2>

        <p className="text-lg text-white/60 text-center mb-16 max-w-2xl mx-auto">
          Sentinel Scan integrates into your development workflow to catch violations before they reach production.
        </p>

        <div className="relative">
          {/* Connecting Line - Desktop */}
          <div className="hidden md:block absolute top-20 left-0 right-0 h-0.5 bg-gradient-to-r from-accent-blue via-accent-green to-accent-coral opacity-30" />

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 md:gap-12">
            {steps.map((step, index) => (
              <div key={index} className="relative">
                {/* Step Number Circle */}
                <div className="flex items-center justify-center w-16 h-16 rounded-full bg-gradient-to-r from-accent-blue to-accent-green text-white font-bold text-xl mb-6 mx-auto md:mx-0 relative z-10">
                  {step.number}
                </div>

                {/* Content */}
                <div className="text-center md:text-left">
                  <div className="flex justify-center md:justify-start mb-4">
                    {step.icon}
                  </div>
                  <h3 className="text-2xl font-bold mb-3 text-white">{step.title}</h3>
                  <p className="text-white/60">{step.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};
