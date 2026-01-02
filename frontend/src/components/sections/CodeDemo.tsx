import { CodeBlock } from '../ui/CodeBlock';
import { AlertTriangle, XCircle } from 'lucide-react';

export const CodeDemo = () => {
  const demoCode = [
    { content: '# customer_analytics.py' },
    { content: '' },
    { content: 'def analyze_feedback(customer_data):' },
    { content: '    email = customer_data["email"]', violation: { type: 'high' as const, message: 'Email address' } },
    { content: '    phone = customer_data["phone"]', violation: { type: 'high' as const, message: 'Phone number' } },
    { content: '    vin = customer_data["vin"]', violation: { type: 'critical' as const, message: 'VIN detected' } },
    { content: '' },
    { content: '    prompt = f"""' },
    { content: '    Analyze this customer feedback:' },
    { content: '    Customer: {email}' },
    { content: '    Vehicle: {vin}' },
    { content: '    """' },
    { content: '' },
    { content: '    # 🚨 CRITICAL: PII flowing to LLM API', violation: { type: 'critical' as const, message: 'PII → LLM API' } },
    { content: '    response = client.chat.completions.create(' },
    { content: '        model="gpt-4",' },
    { content: '        messages=[{"role": "user", "content": prompt}]' },
    { content: '    )' },
  ];

  const violations = [
    { severity: 'critical', line: 14, type: 'VIN → LLM API', icon: <XCircle className="w-4 h-4" /> },
    { severity: 'critical', line: 14, type: 'Email → LLM API', icon: <XCircle className="w-4 h-4" /> },
    { severity: 'high', line: 4, type: 'Email detected', icon: <AlertTriangle className="w-4 h-4" /> },
    { severity: 'high', line: 5, type: 'Phone detected', icon: <AlertTriangle className="w-4 h-4" /> },
  ];

  return (
    <section id="demo" className="section-padding">
      <div className="container-custom">
        <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold text-center mb-4">
          See It In <span className="gradient-text">Action</span>
        </h2>

        <p className="text-lg text-white/60 text-center mb-12 max-w-2xl mx-auto">
          Sentinel Scan analyzes your code and highlights violations in real-time.
        </p>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Code Editor - 2/3 width */}
          <div className="lg:col-span-2">
            <CodeBlock lines={demoCode} filename="customer_analytics.py" />
          </div>

          {/* Violations Panel - 1/3 width */}
          <div className="lg:col-span-1">
            <div className="glass-card p-6 h-full">
              <div className="flex items-center gap-2 mb-6">
                <div className="w-3 h-3 rounded-full bg-accent-green" />
                <h3 className="text-lg font-semibold">Sentinel Scan: 4 violations found</h3>
              </div>

              <div className="space-y-3">
                {violations.map((violation, index) => (
                  <div
                    key={index}
                    className={`p-4 rounded-lg border ${
                      violation.severity === 'critical'
                        ? 'bg-red-500/10 border-red-500/30'
                        : 'bg-yellow-500/10 border-yellow-500/30'
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      <div
                        className={`mt-0.5 ${
                          violation.severity === 'critical' ? 'text-red-400' : 'text-yellow-400'
                        }`}
                      >
                        {violation.icon}
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <span
                            className={`text-xs font-semibold uppercase ${
                              violation.severity === 'critical' ? 'text-red-400' : 'text-yellow-400'
                            }`}
                          >
                            {violation.severity}
                          </span>
                          <span className="text-white/50 text-xs">Line {violation.line}</span>
                        </div>
                        <p className="text-sm text-white/80">{violation.type}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              <div className="mt-6 pt-6 border-t border-white/10">
                <p className="text-sm text-white/50">
                  💡 Violations are mapped to GDPR Article 32, CCPA §1798.150, and HIPAA §164.308
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
