import { Logo } from '../icons/Logo';
import { Github, Twitter, Linkedin } from 'lucide-react';

export const Footer = () => {
  const productLinks = ['Features', 'Pricing', 'Docs', 'Blog', 'Changelog'];
  const legalLinks = ['Privacy', 'Terms', 'Security'];

  return (
    <footer className="bg-bg-secondary border-t border-white/10">
      <div className="max-w-7xl mx-auto px-6 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Logo & Description */}
          <div className="col-span-1 md:col-span-2">
            <Logo className="mb-4" />
            <p className="text-white/60 text-sm max-w-md">
              Developer-native compliance scanning for LLM applications. Catch data privacy violations before they cost millions.
            </p>
          </div>

          {/* Product Links */}
          <div>
            <h4 className="text-white font-semibold mb-4">Product</h4>
            <ul className="space-y-2">
              {productLinks.map((link) => (
                <li key={link}>
                  <a href="#" className="text-white/60 hover:text-white transition-colors text-sm">
                    {link}
                  </a>
                </li>
              ))}
            </ul>
          </div>

          {/* Legal Links */}
          <div>
            <h4 className="text-white font-semibold mb-4">Legal</h4>
            <ul className="space-y-2">
              {legalLinks.map((link) => (
                <li key={link}>
                  <a href="#" className="text-white/60 hover:text-white transition-colors text-sm">
                    {link}
                  </a>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="mt-12 pt-8 border-t border-white/10 flex flex-col md:flex-row justify-between items-center gap-4">
          <p className="text-white/40 text-sm">
            © 2026 Sentinel Scan. All rights reserved.
          </p>

          {/* Social Links */}
          <div className="flex gap-4">
            <a href="#" className="text-white/40 hover:text-white transition-colors">
              <Github size={20} />
            </a>
            <a href="#" className="text-white/40 hover:text-white transition-colors">
              <Twitter size={20} />
            </a>
            <a href="#" className="text-white/40 hover:text-white transition-colors">
              <Linkedin size={20} />
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
};
