import axios from 'axios'
import { ProcessResult, PricingTier, Opportunity } from '../types'

const api = axios.create({
  baseURL: process.env.NODE_ENV === 'production' ? '' : 'http://localhost:8000',
  timeout: 120000, // 2 minutes for file processing
})

export const proposalApi = {
  // Process proposal files
  async processProposal(formData: FormData): Promise<ProcessResult> {
    const response = await api.post('/process', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  // Get pricing information
  async getPricing(): Promise<{ tiers: PricingTier[] }> {
    const response = await api.get('/api/pricing')
    return response.data
  },

  // Get outputs list
  async getOutputs() {
    const response = await api.get('/outputs')
    return response.data
  },

  // Download file
  downloadFile(path: string) {
    return `${api.defaults.baseURL}/download?path=${encodeURIComponent(path)}`
  },

  // Download bundle
  downloadBundle(runId: string) {
    return `${api.defaults.baseURL}/download/bundle?run_id=${encodeURIComponent(runId)}`
  },

  // Bid scoring APIs
  async scoreOpportunity(opportunity: Opportunity) {
    const response = await api.post('/api/bid/score', opportunity)
    return response.data
  },

  async enrichOpportunity(opportunity: Opportunity) {
    const response = await api.post('/api/bid/enrich', { opportunity })
    return response.data
  },

  async getSamNotice(noticeId: string) {
    const response = await api.get(`/api/bid/sam-notice?noticeId=${noticeId}`)
    return response.data
  },

  // Platform capabilities
  async processGovConAgent(files: File[], analysisType = 'full', outputFormat = 'interactive') {
    const formData = new FormData()
    files.forEach(file => formData.append('files', file))
    formData.append('analysis_type', analysisType)
    formData.append('output_format', outputFormat)
    
    const response = await api.post('/api/platform/govcon-agent/process', formData)
    return response.data
  },

  async scoreOpportunities(opportunities: any[], companyProfile: any) {
    const response = await api.post('/api/platform/opportunity-match/score', {
      opportunities,
      company_profile: companyProfile
    })
    return response.data
  },

  async getPursuitDashboard() {
    const response = await api.get('/api/platform/pursuit-management/dashboard')
    return response.data
  },

  async analyzePursuit(pursuitId: string) {
    const response = await api.get(`/api/platform/pursuit-management/analyze/${pursuitId}`)
    return response.data
  },

  async processDocuments(files: File[]) {
    const formData = new FormData()
    files.forEach(file => formData.append('files', file))
    
    const response = await api.post('/api/platform/document-hub/process', formData)
    return response.data
  },

  async getDocumentLibrary() {
    const response = await api.get('/api/platform/document-hub/library')
    return response.data
  },

  async searchTeamingInsights(scope: string, term: string) {
    const response = await api.get('/api/platform/teaming-insights/search', {
      params: { scope, term }
    })
    return response.data
  },
}

export default api