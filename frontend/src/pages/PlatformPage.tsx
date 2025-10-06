import { useState } from 'react'
import { motion } from 'framer-motion'
import { Bot, Target, FileText, TrendingUp, Upload, Users, Zap, Play, Settings } from 'lucide-react'
import { cn } from '../utils'

const PlatformPage = () => {
  const [activeCapability, setActiveCapability] = useState<string | null>(null)

  const capabilities = [
    {
      id: 'govcon-agent',
      icon: Bot,
      title: 'AI GovCon Agent',
      description: 'Turns 200+ page PDFs into navigable sections, distilled requirements, and actionable guidance.',
      status: 'active' as const,
      color: 'from-blue-500 to-blue-600',
      action: 'Launch Agent'
    },
    {
      id: 'opportunity-match',
      icon: Target,
      title: 'Smart Opportunity Match',
      description: 'Ranks and scores opportunities using enrichment (SAM + USAspending) with compliance and fit heuristics.',
      status: 'active' as const,
      color: 'from-green-500 to-green-600',
      action: 'Score Opportunities'
    },
    {
      id: 'proposal-writer',
      icon: FileText,
      title: 'Proposal Writer',
      description: 'Expands structured outlines & requirements coverage into narrative draft sections aligned to shalls.',
      status: 'working' as const,
      color: 'from-purple-500 to-purple-600',
      action: 'Write Proposal'
    },
    {
      id: 'pursuit-management',
      icon: TrendingUp,
      title: 'Pursuit Management',
      description: 'Scoring outputs expose blockers, next actions, competitor signals, and value alignment for BD reviews.',
      status: 'active' as const,
      color: 'from-orange-500 to-orange-600',
      action: 'Manage Pursuits'
    },
    {
      id: 'document-hub',
      icon: Upload,
      title: 'Document Hub',
      description: 'Normalizes mixed-source inputs (ZIP, PDF, DOCX, MD) and materializes assets for traceability & audit.',
      status: 'active' as const,
      color: 'from-indigo-500 to-indigo-600',
      action: 'Access Hub'
    },
    {
      id: 'teaming-insights',
      icon: Users,
      title: 'Teaming Insights',
      description: 'Surfacing incumbent & competitor density heuristics to inform teaming or positioning early.',
      status: 'active' as const,
      color: 'from-pink-500 to-pink-600',
      action: 'View Insights'
    },
  ]

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'active':
        return <span className="inline-flex items-center rounded-full bg-green-100 px-2 py-1 text-xs font-medium text-green-800">Active</span>
      case 'working':
        return <span className="inline-flex items-center rounded-full bg-yellow-100 px-2 py-1 text-xs font-medium text-yellow-800">Working</span>
      case 'coming-soon':
        return <span className="inline-flex items-center rounded-full bg-gray-100 px-2 py-1 text-xs font-medium text-gray-800">Coming Soon</span>
      default:
        return null
    }
  }

  const handleCapabilityClick = (capabilityId: string) => {
    if (capabilityId === 'proposal-writer') {
      window.location.href = '/'
      return
    }
    setActiveCapability(capabilityId)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Header */}
      <div className="bg-white border-b border-secondary-200">
        <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <h1 className="text-4xl font-bold text-secondary-900">Platform Capabilities</h1>
            <p className="mt-4 text-xl text-secondary-600">
              Comprehensive AI-powered solutions for government contracting and proposal development
            </p>
          </motion.div>
        </div>
      </div>

      {/* Main Content */}
      <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 gap-8 lg:grid-cols-3">
          {capabilities.map((capability, index) => (
            <motion.div
              key={capability.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              className={cn(
                'card card-hover p-8 cursor-pointer relative overflow-hidden',
                capability.status === 'working' && 'ring-2 ring-yellow-300',
                activeCapability === capability.id && 'ring-2 ring-primary-500'
              )}
              onClick={() => handleCapabilityClick(capability.id)}
            >
              {/* Background gradient accent */}
              <div className={cn('absolute top-0 right-0 w-20 h-20 opacity-10 rounded-bl-full bg-gradient-to-br', capability.color)} />
              
              {/* Icon */}
              <div className={cn('w-16 h-16 rounded-xl bg-gradient-to-r flex items-center justify-center mb-6', capability.color)}>
                <capability.icon className="h-8 w-8 text-white" />
              </div>

              {/* Content */}
              <div className="space-y-4">
                <div className="flex items-start justify-between">
                  <h3 className="text-2xl font-bold text-secondary-900">{capability.title}</h3>
                  {getStatusBadge(capability.status)}
                </div>
                
                <p className="text-secondary-600 leading-relaxed">
                  {capability.description}
                </p>

                {/* Action Button */}
                <div className="pt-4">
                  <button
                    className={cn(
                      'btn w-full justify-center',
                      capability.status === 'working' 
                        ? 'btn-accent' 
                        : 'btn-primary'
                    )}
                  >
                    <Play className="mr-2 h-4 w-4" />
                    {capability.action}
                  </button>
                </div>

                {/* Quick Stats or Features */}
                {capability.status === 'active' && (
                  <div className="pt-4 border-t border-secondary-100">
                    <div className="flex items-center text-sm text-secondary-500">
                      <Settings className="mr-2 h-4 w-4" />
                      <span>Ready to use</span>
                    </div>
                  </div>
                )}

                {capability.status === 'working' && (
                  <div className="pt-4 border-t border-yellow-200">
                    <div className="flex items-center text-sm text-yellow-700">
                      <Zap className="mr-2 h-4 w-4" />
                      <span>Enhanced interface available</span>
                    </div>
                  </div>
                )}
              </div>
            </motion.div>
          ))}
        </div>

        {/* Feature Highlights */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.6 }}
          className="mt-16 bg-white rounded-2xl shadow-xl border border-secondary-100 overflow-hidden"
        >
          <div className="bg-gradient-to-r from-primary-600 to-accent-600 px-8 py-6">
            <h2 className="text-2xl font-bold text-white">Platform Features</h2>
            <p className="text-primary-100 mt-2">Powered by advanced AI and designed for government contractors</p>
          </div>
          
          <div className="p-8">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {[
                { icon: '🚀', title: 'Fast Processing', desc: 'Analyze 200+ page documents in minutes' },
                { icon: '🔒', title: 'Secure & Compliant', desc: 'Enterprise-grade security for sensitive documents' },
                { icon: '🎯', title: 'High Accuracy', desc: 'AI-powered analysis with 95%+ accuracy rates' },
                { icon: '📊', title: 'Detailed Analytics', desc: 'Comprehensive insights and scoring metrics' },
              ].map((feature, index) => (
                <motion.div
                  key={feature.title}
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ duration: 0.4, delay: 0.8 + index * 0.1 }}
                  className="text-center"
                >
                  <div className="text-3xl mb-3">{feature.icon}</div>
                  <h3 className="font-semibold text-secondary-900 mb-2">{feature.title}</h3>
                  <p className="text-sm text-secondary-600">{feature.desc}</p>
                </motion.div>
              ))}
            </div>
          </div>
        </motion.div>

        {/* Call to Action */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 1.0 }}
          className="mt-16 text-center"
        >
          <div className="bg-gradient-to-r from-secondary-900 to-primary-900 rounded-2xl px-8 py-12 text-white">
            <h2 className="text-3xl font-bold mb-4">Ready to Get Started?</h2>
            <p className="text-xl text-gray-200 mb-8 max-w-2xl mx-auto">
              Try our Proposal Writer to experience the power of AI-driven government contracting.
            </p>
            <button
              onClick={() => window.location.href = '/'}
              className="btn bg-white text-secondary-900 hover:bg-gray-100 text-lg px-8 py-4"
            >
              Start Writing Proposals
            </button>
          </div>
        </motion.div>
      </div>
    </div>
  )
}

export default PlatformPage