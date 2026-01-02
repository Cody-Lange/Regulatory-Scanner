import { Card } from '../ui/Card';
import { AlertTriangle, DollarSign, Clock } from 'lucide-react';

export const Problem = () => {
  const problems = [
    {
      icon: <DollarSign className="w-12 h-12 text-accent-coral" />,
      stat: '€20M+',
      title: 'in GDPR Fines',
      description: 'Sending PII to LLM APIs violates data protection regulations. One mistake can cost millions.',
    },
    {
      icon: <AlertTriangle className="w-12 h-12 text-accent-pink" />,
      stat: '$9.23M',
      title: 'Average HIPAA Breach',
      description: 'Healthcare data in LLM prompts triggers mandatory breach notifications and massive penalties.',
    },
    {
      icon: <Clock className="w-12 h-12 text-accent-blue" />,
      stat: 'Too Late',
      title: 'Manual Review Doesn\'t Scale',
      description: 'Code review catches violations too late. By then, the data has already been exposed.',
    },
  ];

  return (
    <section id="problem" className="section-padding bg-bg-secondary/50">
      <div className="container-custom">
        <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold text-center mb-4">
          The Hidden Risk in Your{' '}
          <span className="gradient-text">AI Applications</span>
        </h2>

        <p className="text-lg text-white/60 text-center mb-12 max-w-2xl mx-auto">
          Companies are unknowingly sending sensitive data to LLM APIs, putting them at risk of catastrophic fines and breaches.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {problems.map((problem, index) => (
            <Card key={index} gradient>
              <div className="flex flex-col items-center text-center">
                <div className="mb-4">{problem.icon}</div>
                <div className="text-4xl font-bold gradient-text mb-2">{problem.stat}</div>
                <h3 className="text-xl font-semibold mb-3 text-white">{problem.title}</h3>
                <p className="text-white/60">{problem.description}</p>
              </div>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
};
