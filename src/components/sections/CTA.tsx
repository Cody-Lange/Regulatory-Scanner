import { useState } from 'react';
import { Button } from '../ui/Button';
import { GradientOrb } from '../ui/GradientOrb';

export const CTA = () => {
  const [email, setEmail] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Handle form submission
    console.log('Email submitted:', email);
    alert('Thank you for joining the waitlist!');
    setEmail('');
  };

  return (
    <section className="section-padding relative overflow-hidden">
      {/* Gradient Orbs */}
      <GradientOrb color="#9d4edd" size="500px" top="-100px" left="-100px" />
      <GradientOrb color="#00d4aa" size="400px" bottom="-100px" right="-100px" />

      <div className="container-custom relative z-10">
        <div className="max-w-3xl mx-auto text-center">
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold mb-6">
            Stop Compliance Violations{' '}
            <span className="gradient-text">Today</span>
          </h2>

          <p className="text-lg text-white/70 mb-8">
            Join the waitlist for early access. Be the first to protect your LLM applications from costly data privacy violations.
          </p>

          <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-4 max-w-xl mx-auto mb-4">
            <input
              type="email"
              placeholder="Enter your email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="flex-1 px-6 py-4 rounded-lg bg-white/10 border border-white/20 text-white placeholder-white/50 focus:outline-none focus:border-accent-blue focus:bg-white/15 transition-all"
            />
            <Button type="submit" size="lg">
              Join Waitlist
            </Button>
          </form>

          <p className="text-sm text-white/50">
            Free trial available. No credit card required.
          </p>
        </div>
      </div>
    </section>
  );
};
