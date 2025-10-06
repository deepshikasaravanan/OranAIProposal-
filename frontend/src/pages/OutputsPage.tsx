import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Download, FileText, Image, Archive, Clock, CheckCircle } from 'lucide-react'
import { proposalApi } from '../services/api'
import { cn, formatFileSize } from '../utils'

interface OutputFile {
  name: string
  path: string
  type: 'docx' | 'json' | 'png' | 'zip'
  size: number
  created: string
}

interface OutputRun {
  id: string
  created: string
  status: 'completed' | 'processing' | 'failed'
  files: OutputFile[]
}

const OutputsPage = () => {
  const [outputs, setOutputs] = useState<OutputRun[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedRun, setSelectedRun] = useState<string | null>(null)

  useEffect(() => {
    loadOutputs()
  }, [])

  const loadOutputs = async () => {
    try {
      setLoading(true)
      const data = await proposalApi.getOutputs()
      
      // Transform the data to match our interface
      const transformedOutputs: OutputRun[] = data.map((item: any) => ({
        id: item.run_id || `run-${Date.now()}`,
        created: item.created || new Date().toISOString(),
        status: item.status || 'completed',
        files: Object.entries(item.files || {}).map(([key, path]: [string, any]) => ({
          name: getFileName(key, path as string),
          path: path as string,
          type: getFileType(key),
          size: 0, // Size not provided by API
          created: item.created || new Date().toISOString(),
        }))
      }))
      
      setOutputs(transformedOutputs)
    } catch (error) {
      console.error('Failed to load outputs:', error)
      // Show some mock data for demo purposes
      setOutputs([
        {
          id: 'run-123',
          created: new Date().toISOString(),
          status: 'completed',
          files: [
            {
              name: 'proposal.docx',
              path: '/path/to/proposal.docx',
              type: 'docx',
              size: 2048576,
              created: new Date().toISOString(),
            },
            {
              name: 'requirements.json',
              path: '/path/to/requirements.json',
              type: 'json',
              size: 102400,
              created: new Date().toISOString(),
            },
          ]
        }
      ])
    } finally {
      setLoading(false)
    }
  }

  const getFileName = (key: string, path: string): string => {
    if (path) {
      return path.split('/').pop() || key
    }
    return key
  }

  const getFileType = (key: string): 'docx' | 'json' | 'png' | 'zip' => {
    if (key.includes('docx') || key === 'proposal') return 'docx'
    if (key.includes('json') || key === 'requirements' || key === 'outlines') return 'json'
    if (key.includes('png') || key === 'gantt' || key === 'flowchart') return 'png'
    if (key.includes('zip') || key === 'bundle') return 'zip'
    return 'json'
  }

  const getFileIcon = (type: string) => {
    switch (type) {
      case 'docx':
        return <FileText className="h-5 w-5 text-blue-600" />
      case 'json':
        return <FileText className="h-5 w-5 text-green-600" />
      case 'png':
        return <Image className="h-5 w-5 text-purple-600" />
      case 'zip':
        return <Archive className="h-5 w-5 text-orange-600" />
      default:
        return <FileText className="h-5 w-5 text-gray-600" />
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-green-500" />
      case 'processing':
        return <Clock className="h-5 w-5 text-yellow-500 animate-spin" />
      case 'failed':
        return <div className="h-5 w-5 bg-red-500 rounded-full" />
      default:
        return <div className="h-5 w-5 bg-gray-400 rounded-full" />
    }
  }

  const handleDownload = (filePath: string, fileName: string) => {
    const url = proposalApi.downloadFile(filePath)
    const link = document.createElement('a')
    link.href = url
    link.download = fileName
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  const handleDownloadBundle = (runId: string) => {
    const url = proposalApi.downloadBundle(runId)
    window.open(url, '_blank')
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600"></div>
          <p className="mt-4 text-secondary-600">Loading outputs...</p>
        </div>
      </div>
    )
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
            <h1 className="text-4xl font-bold text-secondary-900">Generated Outputs</h1>
            <p className="mt-4 text-xl text-secondary-600">
              View and download your proposal documents and analysis files
            </p>
          </motion.div>
        </div>
      </div>

      {/* Main Content */}
      <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
        {outputs.length === 0 ? (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center py-24"
          >
            <FileText className="mx-auto h-24 w-24 text-secondary-300 mb-8" />
            <h2 className="text-3xl font-bold text-secondary-900 mb-4">No outputs yet</h2>
            <p className="text-xl text-secondary-600 mb-8 max-w-2xl mx-auto">
              Generate your first proposal to see outputs here. Upload documents and let AI create your proposal.
            </p>
            <button
              onClick={() => window.location.href = '/'}
              className="btn btn-primary text-lg px-8 py-4"
            >
              Generate Proposal
            </button>
          </motion.div>
        ) : (
          <div className="space-y-8">
            {outputs.map((run, runIndex) => (
              <motion.div
                key={run.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: runIndex * 0.1 }}
                className="card p-8"
              >
                {/* Run Header */}
                <div className="flex items-center justify-between mb-6">
                  <div className="flex items-center gap-4">
                    {getStatusIcon(run.status)}
                    <div>
                      <h3 className="text-xl font-semibold text-secondary-900">
                        Run {run.id}
                      </h3>
                      <p className="text-secondary-600">
                        Generated on {new Date(run.created).toLocaleDateString()} at{' '}
                        {new Date(run.created).toLocaleTimeString()}
                      </p>
                    </div>
                  </div>
                  
                  {run.status === 'completed' && run.files.length > 1 && (
                    <button
                      onClick={() => handleDownloadBundle(run.id)}
                      className="btn btn-secondary flex items-center gap-2"
                    >
                      <Archive className="h-4 w-4" />
                      Download All
                    </button>
                  )}
                </div>

                {/* Files Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {run.files.map((file, fileIndex) => (
                    <motion.div
                      key={`${run.id}-${file.name}`}
                      initial={{ opacity: 0, scale: 0.8 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ duration: 0.4, delay: (runIndex * 0.1) + (fileIndex * 0.05) }}
                      className="bg-gradient-to-br from-white to-gray-50 rounded-xl p-6 border border-secondary-200 hover:border-primary-300 hover:shadow-lg transition-all duration-200"
                    >
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex items-center gap-3">
                          {getFileIcon(file.type)}
                          <div>
                            <h4 className="font-medium text-secondary-900 truncate">
                              {file.name}
                            </h4>
                            <p className="text-sm text-secondary-500">
                              {file.size > 0 ? formatFileSize(file.size) : 'Unknown size'}
                            </p>
                          </div>
                        </div>
                      </div>

                      <button
                        onClick={() => handleDownload(file.path, file.name)}
                        className="w-full btn btn-primary flex items-center justify-center gap-2"
                      >
                        <Download className="h-4 w-4" />
                        Download
                      </button>
                    </motion.div>
                  ))}
                </div>

                {/* Expand/Collapse Details */}
                <div className="mt-6 pt-6 border-t border-secondary-200">
                  <button
                    onClick={() => setSelectedRun(selectedRun === run.id ? null : run.id)}
                    className="text-primary-600 hover:text-primary-700 font-medium flex items-center gap-2"
                  >
                    {selectedRun === run.id ? 'Hide' : 'Show'} Details
                    <div className={cn(
                      'transition-transform duration-200',
                      selectedRun === run.id ? 'rotate-180' : ''
                    )}>
                      ↓
                    </div>
                  </button>
                  
                  {selectedRun === run.id && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      exit={{ opacity: 0, height: 0 }}
                      className="mt-4 space-y-2"
                    >
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                        <div>
                          <span className="font-medium text-secondary-700">Status:</span>
                          <span className="ml-2 capitalize text-secondary-600">{run.status}</span>
                        </div>
                        <div>
                          <span className="font-medium text-secondary-700">Files:</span>
                          <span className="ml-2 text-secondary-600">{run.files.length} generated</span>
                        </div>
                        <div>
                          <span className="font-medium text-secondary-700">Run ID:</span>
                          <span className="ml-2 font-mono text-secondary-600">{run.id}</span>
                        </div>
                        <div>
                          <span className="font-medium text-secondary-700">Total Size:</span>
                          <span className="ml-2 text-secondary-600">
                            {formatFileSize(run.files.reduce((sum, file) => sum + file.size, 0))}
                          </span>
                        </div>
                      </div>
                    </motion.div>
                  )}
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default OutputsPage