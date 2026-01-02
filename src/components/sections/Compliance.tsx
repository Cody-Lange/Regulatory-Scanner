import { Shield } from 'lucide-react';

export const Compliance = () => {
  const regulations = [
    { name: 'GDPR', description: 'EU Data Protection' },
    { name: 'CCPA', description: 'California Privacy' },
    { name: 'HIPAA', description: 'Healthcare Data' },
    { name: 'PCI-DSS', description: 'Payment Card' },
    { name: 'EU AI Act', description: 'AI Regulation' },
  ];

  return (
    <section className="section-padding">
      <div className="container-custom">
        <h2 className="text-2xl md:text-3xl font-bold text-center mb-4">
          Designed for <span className="gradient-text">Regulatory Compliance</span>
        </h2>

        <p className="text-white/60 text-center mb-12 max-w-2xl mx-auto">
          Every violation is automatically mapped to relevant regulations for easy compliance reporting.
        </p>

        <div className="flex flex-wrap justify-center items-center gap-8 md:gap-12">
          {regulations.map((regulation, index) => (
            <div
              key={index}
              className="flex flex-col items-center gap-2 opacity-60 hover:opacity-100 transition-opacity duration-300"
            >
              <div className="glass-card p-6 rounded-xl">
                <Shield className="w-8 h-8 text-accent-blue" />
              </div>
              <div className="text-center">
                <div className="font-bold text-white">{regulation.name}</div>
                <div className="text-xs text-white/50">{regulation.description}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};
