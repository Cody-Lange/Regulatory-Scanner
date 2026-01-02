import { Button } from '../ui/Button';
import { GradientOrb } from '../ui/GradientOrb';
import { CodeBlock } from '../ui/CodeBlock';

export const Hero = () => {
  const codeLines = [
    { content: '# analytics.py - Gorilla Gate detecting violations' },
    { content: '' },
    { content: 'customer_email = "john.smith@example.com"', violation: { type: 'high' as const, message: 'PII: Email' } },
    { content: 'vin_number = "1HGCM82633A004352"', violation: { type: 'high' as const, message: 'VIN detected' } },
    { content: '' },
    { content: 'response = openai.chat.completions.create(' },
    { content: '    messages=[{"content": f"Analyze {customer_email}"}]', violation: { type: 'critical' as const, message: 'PII → LLM' } },
    { content: ')' },
  ];

  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden pt-20">
      {/* Gradient Orbs */}
      <GradientOrb color="#4a90d9" size="600px" top="-200px" left="-200px" />
      <GradientOrb color="#ff6b9d" size="500px" bottom="-150px" right="-150px" />

      <div className="container-custom section-padding relative z-10">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          {/* Left Column - Text Content */}
          <div className="text-center lg:text-left">
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold mb-6 leading-tight">
              Catch Data Privacy Violations{' '}
              <span className="gradient-text">Before They Cost Millions</span>
            </h1>

            <p className="text-lg md:text-xl text-white/70 mb-8 max-w-2xl mx-auto lg:mx-0">
              Developer-native compliance scanning for LLM applications. Scan your code for PII, VINs, and sensitive data before it reaches production.
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start">
              <Button size="lg" variant="primary">
                Start Free Trial
              </Button>
              <Button size="lg" variant="outline">
                View Demo
              </Button>
            </div>
          </div>

          {/* Right Column - Code Mockup */}
          <div className="hidden lg:block">
            <CodeBlock lines={codeLines} />
          </div>
        </div>

        {/* Mobile Code Block */}
        <div className="lg:hidden mt-12">
          <CodeBlock lines={codeLines} />
        </div>
      </div>
    </section>
  );
};
