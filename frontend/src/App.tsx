import { Navbar } from './components/layout/Navbar';
import { Footer } from './components/layout/Footer';
import { Hero } from './components/sections/Hero';
import { Problem } from './components/sections/Problem';
import { Solution } from './components/sections/Solution';
import { Features } from './components/sections/Features';
import { CodeDemo } from './components/sections/CodeDemo';
import { Pricing } from './components/sections/Pricing';
import { Compliance } from './components/sections/Compliance';
import { CTA } from './components/sections/CTA';

function App() {
  return (
    <div className="min-h-screen bg-bg-primary text-white">
      <Navbar />
      <main>
        <Hero />
        <Problem />
        <Solution />
        <Features />
        <CodeDemo />
        <Pricing />
        <Compliance />
        <CTA />
      </main>
      <Footer />
    </div>
  );
}

export default App;
