import { Card } from '../ui/Card';
import { Code2, Terminal, Brain, FileText, Database, Building2 } from 'lucide-react';

export const Features = () => {
  const features = [
    {
      icon: <Code2 className="w-10 h-10 text-accent-blue" />,
      title: 'VS Code Extension',
      description: 'Inline warnings as you type. See violations before you save.',
    },
    {
      icon: <Terminal className="w-10 h-10 text-accent-green" />,
      title: 'CLI & Pre-commit Hooks',
      description: 'Integrate into any CI/CD pipeline. Block commits with violations.',
    },
    {
      icon: <Brain className="w-10 h-10 text-accent-pink" />,
      title: 'Context-Aware Detection',
      description: 'AST analysis distinguishes test data from production code.',
    },
    {
      icon: <FileText className="w-10 h-10 text-accent-coral" />,
      title: 'Regulatory Mapping',
      description: 'Every violation mapped to GDPR, CCPA, HIPAA regulations.',
    },
    {
      icon: <Database className="w-10 h-10 text-accent-purple" />,
      title: 'Audit Trail Export',
      description: 'JSON reports ready for compliance audits and regulators.',
    },
    {
      icon: <Building2 className="w-10 h-10 text-accent-blue" />,
      title: 'Industry Templates',
      description: 'Pre-built rules for automotive, healthcare, finance.',
    },
  ];

  return (
    <section id="features" className="section-padding bg-bg-secondary/50">
      <div className="container-custom">
        <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold text-center mb-4">
          Built for Developers,{' '}
          <span className="gradient-text">Trusted by Compliance</span>
        </h2>

        <p className="text-lg text-white/60 text-center mb-12 max-w-2xl mx-auto">
          Enterprise-grade compliance scanning that integrates seamlessly into your development workflow.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature, index) => (
            <Card key={index}>
              <div className="mb-4">{feature.icon}</div>
              <h3 className="text-xl font-semibold mb-3 text-white">{feature.title}</h3>
              <p className="text-white/60">{feature.description}</p>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
};
