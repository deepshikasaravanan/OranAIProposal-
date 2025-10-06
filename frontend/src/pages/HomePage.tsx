import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Bot, FileText, Target, TrendingUp, Users, Zap, Upload, Download, CheckCircle } from 'lucide-react'
import { useDropzone } from 'react-dropzone'
import { proposalApi } from '../services/api'
import { ProcessResult, PricingTier } from '../types'
import { cn, formatFileSize } from '../utils'

const HomePage = () => {
  const [isProcessing, setIsProcessing] = useState(false)
  const [result, setResult] = useState<ProcessResult | null>(null)
  const [progress, setProgress] = useState(0)
  const [pricing, setPricing] = useState<PricingTier[]>([])
  const [selectedFiles, setSelectedFiles] = useState<File[]>([])
  const [model, setModel] = useState('')

  // Load pricing on component mount
  useEffect(() => {
    const loadPricing = async () => {
      try {
        const data = await proposalApi.getPricing()
        setPricing(data.tiers)
      } catch (error) {
        console.error('Failed to load pricing:', error)
      }
    }
    loadPricing()
  }, [])

  // File dropzone configuration
  const onDrop = (acceptedFiles: File[]) => {
    setSelectedFiles(acceptedFiles)
  }

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/markdown': ['.md'],
      'text/plain': ['.txt'],
      'application/x-yaml': ['.yaml', '.yml'],
    },
    multiple: true,
  })

  // Simulate progress
  const simulateProgress = () => {
    let currentProgress = 5
    setProgress(currentProgress)
    
    const interval = setInterval(() => {
      currentProgress = Math.min(95, currentProgress + Math.random() * 8)
      setProgress(currentProgress)
    }, 300)

    return () => {
      clearInterval(interval)
      setProgress(100)
      setTimeout(() => setProgress(0), 600)
    }
  }

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (selectedFiles.length === 0) {
      alert('Please select at least one file')
      return
    }

    setIsProcessing(true)
    const stopProgress = simulateProgress()

    try {
      const formData = new FormData()
      
      // Add PWS file (first file)
      formData.append('pws', selectedFiles[0])
      
      // Add RFP file if available (second file)
      if (selectedFiles.length > 1) {
        formData.append('rfp', selectedFiles[1])
      }
      
      // Add model if selected
      if (model) {
        formData.append('model', model)
      }

      const data = await proposalApi.processProposal(formData)
      setResult(data)
    } catch (error) {
      console.error('Processing failed:', error)
      alert('Processing failed. Please try again.')
    } finally {
      setIsProcessing(false)
      stopProgress()
    }
  }

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative bg-gradient-to-br from-secondary-900 via-primary-900 to-accent-900 text-white overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-primary-600/20 to-accent-600/20"></div>
        <div className="relative mx-auto max-w-7xl px-4 py-24 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center"
          >
            <h1 className="text-5xl font-bold sm:text-6xl lg:text-7xl">
              Find. Bid. Win!
              <br />
              <span className="gradient-text">Government Contracts with AI</span>
            </h1>
            <p className="mx-auto mt-6 max-w-3xl text-xl text-gray-200">
              Effortlessly discover opportunities, craft winning proposals, and stay ahead of the competition. 
              The simplest way to leverage AI for your GovCon business.
            </p>
            <div className="mt-10 flex flex-col sm:flex-row gap-4 justify-center">
              <a
                href="#get-started"
                className="btn btn-accent text-lg px-8 py-4"
              >
                Start for Free
              </a>
              <a
                href="#features"
                className="btn btn-ghost text-lg px-8 py-4"
              >
                Learn More
              </a>
            </div>
            
            {/* Trust indicators */}
            <div className="mt-12 flex flex-col items-center gap-4">
              <div className="flex items-center gap-2">
                <div className="flex -space-x-2">
                  {[1, 2, 3, 4].map((i) => (
                    <div
                      key={i}
                      className="h-8 w-8 rounded-full bg-gradient-to-r from-primary-400 to-accent-400 border-2 border-white"
                    />
                  ))}
                </div>
                <span className="ml-2 font-semibold">Trusted by 400+ companies</span>
              </div>
              <div className="flex flex-wrap justify-center gap-6 text-gray-300">
                <span className="font-mono text-sm">red-inc</span>
                <span className="font-mono text-sm">Marathon</span>
                <span className="font-mono text-sm">VarnerMiller</span>
                <span className="font-mono text-sm">BATIR</span>
              </div>
              <div className="flex flex-wrap justify-center gap-4 text-sm">
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-4 w-4 text-green-400" />
                  <span>7-day free trial</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-4 w-4 text-green-400" />
                  <span>Federal & SLED Contracts</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-4 w-4 text-green-400" />
                  <span>Secure & Compliant</span>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-24 bg-white">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl font-bold text-secondary-900">Platform Capabilities</h2>
            <p className="mt-4 text-xl text-secondary-600">
              Everything you need to win government contracts
            </p>
          </motion.div>

          <div className="grid grid-cols-1 gap-8 md:grid-cols-2 lg:grid-cols-3">
            {[
              {
                icon: Bot,
                title: 'AI GovCon Agent',
                description: 'Turns 200+ page PDFs into navigable sections, distilled requirements, and actionable guidance.',
                color: 'from-blue-500 to-blue-600'
              },
              {
                icon: Target,
                title: 'Smart Opportunity Match',
                description: 'Ranks and scores opportunities using enrichment (SAM + USAspending) with compliance and fit heuristics.',
                color: 'from-green-500 to-green-600'
              },
              {
                icon: FileText,
                title: 'Proposal Writer',
                description: 'Expands structured outlines & requirements coverage into narrative draft sections aligned to shalls.',
                color: 'from-purple-500 to-purple-600',
                isActive: true
              },
              {
                icon: TrendingUp,
                title: 'Pursuit Management',
                description: 'Scoring outputs expose blockers, next actions, competitor signals, and value alignment for BD reviews.',
                color: 'from-orange-500 to-orange-600'
              },
              {
                icon: Upload,
                title: 'Document Hub',
                description: 'Normalizes mixed-source inputs (ZIP, PDF, DOCX, MD) and materializes assets for traceability & audit.',
                color: 'from-indigo-500 to-indigo-600'
              },
              {
                icon: Users,
                title: 'Teaming Insights',
                description: 'Surfacing incumbent & competitor density heuristics to inform teaming or positioning early.',
                color: 'from-pink-500 to-pink-600'
              },
            ].map((feature, index) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                viewport={{ once: true }}
                className={cn(
                  'card card-hover p-8 cursor-pointer',
                  feature.isActive && 'ring-2 ring-primary-500'
                )}
                onClick={() => {
                  if (feature.isActive) {
                    document.getElementById('get-started')?.scrollIntoView({ behavior: 'smooth' })
                  }
                }}
              >
                <div className={cn('w-12 h-12 rounded-lg bg-gradient-to-r flex items-center justify-center mb-4', feature.color)}>
                  <feature.icon className="h-6 w-6 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-secondary-900 mb-3">{feature.title}</h3>
                <p className="text-secondary-600">{feature.description}</p>
                {feature.isActive && (
                  <div className="mt-4">
                    <span className="inline-flex items-center rounded-full bg-primary-100 px-3 py-1 text-sm font-medium text-primary-800">
                      <Zap className="mr-1 h-3 w-3" />
                      Try Now
                    </span>
                  </div>
                )}
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Proposal Generation Section */}
      <section id="get-started" className="py-24 bg-gradient-to-br from-gray-50 to-blue-50">
        <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
            className="text-center mb-12"
          >
            <h2 className="text-4xl font-bold text-secondary-900">Generate Your Proposal</h2>
            <p className="mt-4 text-xl text-secondary-600">
              Upload your documents and let AI create a winning proposal
            </p>
          </motion.div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Upload Section */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              viewport={{ once: true }}
              className="card p-8"
            >
              <h3 className="text-2xl font-semibold text-secondary-900 mb-6">1. Upload Source</h3>
              
              <form onSubmit={handleSubmit} className="space-y-6">
                {/* File Upload */}
                <div>
                  <label className="label">PWS / SoW (pdf, docx, md, txt) *</label>
                  <div
                    {...getRootProps()}
                    className={cn(
                      'border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors',
                      isDragActive 
                        ? 'border-primary-500 bg-primary-50' 
                        : 'border-secondary-300 hover:border-primary-400 hover:bg-gray-50'
                    )}
                  >
                    <input {...getInputProps()} />
                    <Upload className="mx-auto h-12 w-12 text-secondary-400 mb-4" />
                    {selectedFiles.length > 0 ? (
                      <div className="space-y-2">
                        {selectedFiles.map((file, index) => (
                          <div key={index} className="flex items-center justify-between bg-white rounded-lg p-3 border">
                            <span className="text-sm font-medium">{file.name}</span>
                            <span className="text-xs text-secondary-500">{formatFileSize(file.size)}</span>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div>
                        <p className="text-secondary-600">
                          {isDragActive ? 'Drop files here...' : 'Drag & drop files here, or click to select'}
                        </p>
                        <p className="text-sm text-secondary-500 mt-2">
                          Supports PDF, DOCX, MD, TXT, YAML
                        </p>
                      </div>
                    )}
                  </div>
                </div>

                {/* Model Selection */}
                <div>
                  <label className="label">Model (optional)</label>
                  <select
                    value={model}
                    onChange={(e) => setModel(e.target.value)}
                    className="input"
                  >
                    <option value="">Use default</option>
                    <optgroup label="OpenAI">
                      <option value="gpt-4o-mini">gpt-4o-mini</option>
                      <option value="gpt-4o">gpt-4o</option>
                      <option value="gpt-4.1-mini">gpt-4.1-mini</option>
                      <option value="gpt-4.1">gpt-4.1</option>
                    </optgroup>
                    <optgroup label="Anthropic">
                      <option value="claude-3-5-sonnet-20241022">claude-3-5-sonnet</option>
                      <option value="claude-3-opus-20240229">claude-3-opus</option>
                      <option value="claude-3-haiku-20240307">claude-3-haiku</option>
                    </optgroup>
                  </select>
                </div>

                {/* Submit Button */}
                <button
                  type="submit"
                  disabled={isProcessing || selectedFiles.length === 0}
                  className="w-full btn btn-primary text-lg py-4"
                >
                  {isProcessing ? 'Processing...' : 'Generate Proposal'}
                </button>

                {/* Progress Bar */}
                {isProcessing && (
                  <div className="w-full bg-secondary-200 rounded-full h-3 overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-primary-500 to-accent-500 transition-all duration-300 ease-out"
                      style={{ width: `${progress}%` }}
                    />
                  </div>
                )}
              </form>
            </motion.div>

            {/* Results Section */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.4 }}
              viewport={{ once: true }}
              className="card p-8"
            >
              <h3 className="text-2xl font-semibold text-secondary-900 mb-6">2. Results</h3>
              
              {result ? (
                <div className="space-y-6">
                  {/* Summary Metrics */}
                  {result.section6_coverage && (
                    <div className="grid grid-cols-2 gap-4">
                      <div className="bg-gradient-to-r from-primary-600 to-primary-700 text-white p-4 rounded-xl">
                        <div className="text-2xl font-bold">
                          {Object.values(result.section6_coverage).filter(Boolean).length}
                        </div>
                        <div className="text-sm opacity-90">
                          / {Object.keys(result.section6_coverage).length} Coverage
                        </div>
                      </div>
                      <div className="bg-gradient-to-r from-green-500 to-green-600 text-white p-4 rounded-xl">
                        <div className="text-2xl font-bold">✓</div>
                        <div className="text-sm opacity-90">Generated</div>
                      </div>
                    </div>
                  )}

                  {/* Download Links */}
                  <div className="space-y-3">
                    {result.outputs?.docx && (
                      <a
                        href={proposalApi.downloadFile(result.outputs.docx)}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center justify-between p-4 bg-secondary-900 text-white rounded-xl hover:bg-secondary-800 transition-colors"
                      >
                        <span className="font-medium">Proposal DOCX</span>
                        <Download className="h-5 w-5" />
                      </a>
                    )}
                    
                    {result.outputs?.requirements && (
                      <a
                        href={proposalApi.downloadFile(result.outputs.requirements)}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center justify-between p-4 bg-secondary-900 text-white rounded-xl hover:bg-secondary-800 transition-colors"
                      >
                        <span className="font-medium">Requirements JSON</span>
                        <Download className="h-5 w-5" />
                      </a>
                    )}

                    {result.run_id && (
                      <a
                        href={proposalApi.downloadBundle(result.run_id)}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center justify-between p-4 bg-gradient-to-r from-accent-500 to-accent-600 text-white rounded-xl hover:from-accent-600 hover:to-accent-700 transition-colors"
                      >
                        <span className="font-medium">All Files (.zip)</span>
                        <Download className="h-5 w-5" />
                      </a>
                    )}
                  </div>
                </div>
              ) : (
                <div className="text-center text-secondary-500 py-12">
                  <FileText className="mx-auto h-16 w-16 mb-4 opacity-50" />
                  <p>Upload a document to see structured output.</p>
                </div>
              )}
            </motion.div>
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="py-24 bg-white">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl font-bold text-secondary-900">Pricing</h2>
            <p className="mt-4 text-xl text-secondary-600">
              Flexible plans that scale with your federal capture & proposal velocity.
            </p>
          </motion.div>

          <div className="grid grid-cols-1 gap-8 md:grid-cols-3">
            {pricing.map((tier, index) => (
              <motion.div
                key={tier.id}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.2 }}
                viewport={{ once: true }}
                className={cn(
                  'card p-8 relative',
                  tier.highlight && 'ring-2 ring-primary-500 scale-105'
                )}
              >
                {tier.highlight && (
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                    <span className="bg-gradient-to-r from-primary-500 to-accent-500 text-white px-4 py-2 rounded-full text-sm font-semibold">
                      ✨ Most Popular
                    </span>
                  </div>
                )}

                <div className="text-center">
                  <h3 className="text-2xl font-bold text-secondary-900">{tier.name}</h3>
                  <p className="mt-2 text-secondary-600">{tier.tagline}</p>
                  
                  {tier.trial && (
                    <p className="mt-4 text-sm font-semibold text-primary-600">{tier.trial}</p>
                  )}

                  <div className="mt-6">
                    {tier.contact ? (
                      <div className="text-3xl font-bold text-secondary-900">Contact Us</div>
                    ) : (
                      <div className="flex items-baseline justify-center">
                        <span className="text-5xl font-bold text-secondary-900">${tier.price_month}</span>
                        <span className="ml-2 text-secondary-600">/month</span>
                      </div>
                    )}
                  </div>

                  <ul className="mt-8 space-y-3">
                    {tier.features.map((feature) => (
                      <li key={feature} className="flex items-center">
                        <CheckCircle className="mr-3 h-5 w-5 text-primary-500" />
                        <span className="text-secondary-600">{feature}</span>
                      </li>
                    ))}
                  </ul>

                  <button
                    className={cn(
                      'mt-8 w-full btn',
                      tier.highlight ? 'btn-primary' : 'btn-secondary'
                    )}
                  >
                    {tier.contact ? 'Contact Sales' : 'Start Trial'}
                  </button>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>
    </div>
  )
}

export default HomePage