import { motion } from 'framer-motion'

const Footer = () => {
  const currentYear = new Date().getFullYear()

  return (
    <motion.footer 
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ delay: 0.5 }}
      className="bg-secondary-900 text-white"
    >
      <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 gap-8 md:grid-cols-4">
          {/* Brand */}
          <div className="md:col-span-2">
            <h3 className="text-lg font-bold">Proposal Bot</h3>
            <p className="mt-2 text-sm text-secondary-300">
              AI-powered government contracting platform that helps you find, bid, and win federal contracts.
            </p>
            <div className="mt-4 flex space-x-2">
              <span className="inline-block rounded-md bg-primary-600 px-2 py-1 text-xs font-semibold">
                7-day free trial
              </span>
              <span className="inline-block rounded-md bg-secondary-700 px-2 py-1 text-xs font-semibold">
                Federal & SLED
              </span>
              <span className="inline-block rounded-md bg-accent-600 px-2 py-1 text-xs font-semibold">
                Secure & Compliant
              </span>
            </div>
          </div>

          {/* Features */}
          <div>
            <h4 className="text-sm font-semibold uppercase tracking-wide">Features</h4>
            <ul className="mt-4 space-y-2 text-sm">
              <li><a href="#" className="text-secondary-300 hover:text-white transition-colors">AI GovCon Agent</a></li>
              <li><a href="#" className="text-secondary-300 hover:text-white transition-colors">Opportunity Match</a></li>
              <li><a href="#" className="text-secondary-300 hover:text-white transition-colors">Proposal Writer</a></li>
              <li><a href="#" className="text-secondary-300 hover:text-white transition-colors">Pursuit Management</a></li>
            </ul>
          </div>

          {/* Resources */}
          <div>
            <h4 className="text-sm font-semibold uppercase tracking-wide">Resources</h4>
            <ul className="mt-4 space-y-2 text-sm">
              <li><a href="#" className="text-secondary-300 hover:text-white transition-colors">Documentation</a></li>
              <li><a href="#" className="text-secondary-300 hover:text-white transition-colors">API Reference</a></li>
              <li><a href="#" className="text-secondary-300 hover:text-white transition-colors">Support</a></li>
              <li><a href="#" className="text-secondary-300 hover:text-white transition-colors">Status</a></li>
            </ul>
          </div>
        </div>

        <div className="mt-8 border-t border-secondary-800 pt-8 text-center">
          <p className="text-sm text-secondary-400">
            © {currentYear} Proposal Bot – Auto-drafted content preview.
          </p>
        </div>
      </div>
    </motion.footer>
  )
}

export default Footer