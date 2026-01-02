import { Button } from '../ui/Button';
import { Check } from 'lucide-react';

export const Pricing = () => {
  const tiers = [
    {
      name: 'Starter',
      price: '$15,000',
      period: '/year',
      description: 'Perfect for small teams getting started',
      features: [
        'Up to 5 developers',
        '1 project',
        'Email support',
        'Pre-built templates',
        'Basic reporting',
      ],
      cta: 'Get Started',
      highlighted: false,
    },
    {
      name: 'Professional',
      price: '$35,000',
      period: '/year',
      description: 'For growing teams with compliance needs',
      features: [
        'Up to 20 developers',
        '5 projects',
        'Priority support',
        'Custom rules',
        'Quarterly compliance reviews',
        'Advanced analytics',
        'API access',
      ],
      cta: 'Get Started',
      highlighted: true,
    },
    {
      name: 'Enterprise',
      price: 'Custom',
      period: '',
      description: 'For organizations with complex requirements',
      features: [
        'Unlimited developers',
        'Unlimited projects',
        'Dedicated CSM',
        'SLA guarantee',
        'On-premises option',
        'Custom integrations',
        'White-glove onboarding',
        'Legal review support',
      ],
      cta: 'Contact Sales',
      highlighted: false,
    },
  ];

  return (
    <section id="pricing" className="section-padding bg-bg-secondary/50">
      <div className="container-custom">
        <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold text-center mb-4">
          Simple, <span className="gradient-text">Transparent Pricing</span>
        </h2>

        <p className="text-lg text-white/60 text-center mb-12 max-w-2xl mx-auto">
          Choose the plan that fits your team size and compliance requirements.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {tiers.map((tier, index) => (
            <div
              key={index}
              className={`glass-card p-8 flex flex-col ${
                tier.highlighted
                  ? 'border-2 border-accent-blue shadow-2xl shadow-accent-blue/20 scale-105'
                  : ''
              }`}
            >
              {tier.highlighted && (
                <div className="text-xs font-semibold uppercase text-accent-blue mb-4 text-center">
                  Recommended
                </div>
              )}

              <h3 className="text-2xl font-bold mb-2 text-white">{tier.name}</h3>
              <p className="text-white/60 text-sm mb-6">{tier.description}</p>

              <div className="mb-8">
                <span className="text-4xl font-bold gradient-text">{tier.price}</span>
                <span className="text-white/60">{tier.period}</span>
              </div>

              <ul className="space-y-3 mb-8 flex-grow">
                {tier.features.map((feature, i) => (
                  <li key={i} className="flex items-start gap-3">
                    <Check className="w-5 h-5 text-accent-green flex-shrink-0 mt-0.5" />
                    <span className="text-white/80">{feature}</span>
                  </li>
                ))}
              </ul>

              <Button
                variant={tier.highlighted ? 'primary' : 'outline'}
                size="lg"
                className="w-full"
              >
                {tier.cta}
              </Button>
            </div>
          ))}
        </div>

        <p className="text-center text-white/50 text-sm mt-8">
          All plans include a 14-day free trial. No credit card required.
        </p>
      </div>
    </section>
  );
};
