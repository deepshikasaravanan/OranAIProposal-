/**
 * Browser AI Integration for Government Proposal Platform
 * Leverages Web Machine Learning Writing Assistance APIs for local AI processing
 */

class BrowserAIIntegration {
    constructor() {
        this.features = {
            summarizer: false,
            writer: false,
            rewriter: false
        };
        
        this.configs = {
            rfpAnalysis: {
                type: "key-points",
                sharedContext: "Government RFP document requiring detailed analysis for proposal response",
                expectedInputLanguages: ["en"],
                outputLanguage: "en"
            },
            proposalWriting: {
                tone: "formal",
                sharedContext: "Government contract proposal requiring professional technical content",
                expectedOutputLanguage: "en"
            },
            complianceRewriting: {
                sharedContext: "Government proposal content requiring compliance enhancement and formal tone",
                expectedInputLanguages: ["en"],
                outputLanguage: "en"
            }
        };
        
        this.contextTemplates = {
            requirements: "Extract specific requirements, deliverables, and compliance needs from this RFP",
            deadlines: "Identify all submission deadlines, milestone dates, and timeline requirements",
            evaluation: "Summarize evaluation criteria, scoring factors, and award methodology",
            compliance: "Extract compliance requirements including Section 508, security, and regulatory needs",
            technical: "Generate detailed technical approach addressing system architecture and implementation",
            management: "Create management approach demonstrating project leadership and organization",
            pastPerformance: "Write past performance narrative highlighting relevant contract experience"
        };
    }

    // Browser AI Feature Detection
    async detectCapabilities() {
        console.log('🔍 Detecting Browser AI Capabilities...');
        
        try {
            // Check Summarizer API
            if (typeof Summarizer !== 'undefined') {
                const summarizerAvailability = await Summarizer.availability(this.configs.rfpAnalysis);
                this.features.summarizer = summarizerAvailability !== 'unavailable';
                console.log(`📋 Summarizer API: ${this.features.summarizer ? '✅ Available' : '❌ Not Available'}`);
                
                if (summarizerAvailability === 'downloadable') {
                    console.log('📥 Summarizer model requires download');
                }
            }
            
            // Check Writer API
            if (typeof Writer !== 'undefined') {
                const writerAvailability = await Writer.availability(this.configs.proposalWriting);
                this.features.writer = writerAvailability !== 'unavailable';
                console.log(`✍️ Writer API: ${this.features.writer ? '✅ Available' : '❌ Not Available'}`);
                
                if (writerAvailability === 'downloadable') {
                    console.log('📥 Writer model requires download');
                }
            }
            
            // Check Rewriter API
            if (typeof Rewriter !== 'undefined') {
                const rewriterAvailability = await Rewriter.availability(this.configs.complianceRewriting);
                this.features.rewriter = rewriterAvailability !== 'unavailable';
                console.log(`🔄 Rewriter API: ${this.features.rewriter ? '✅ Available' : '❌ Not Available'}`);
                
                if (rewriterAvailability === 'downloadable') {
                    console.log('📥 Rewriter model requires download');
                }
            }
            
        } catch (error) {
            console.warn('⚠️ Browser AI detection failed:', error);
        }
        
        const totalFeatures = Object.keys(this.features).length;
        const availableFeatures = Object.values(this.features).filter(Boolean).length;
        console.log(`🎯 Browser AI Status: ${availableFeatures}/${totalFeatures} APIs available`);
        
        this.showCapabilityBadge(availableFeatures, totalFeatures);
        return this.features;
    }

    // Show capability status in UI
    showCapabilityBadge(available, total) {
        const badge = document.createElement('div');
        badge.className = 'browser-ai-badge';
        badge.innerHTML = `
            <div class="ai-badge-content">
                <span class="ai-icon">🤖</span>
                <span class="ai-text">Browser AI: ${available}/${total}</span>
                <span class="ai-status ${available > 0 ? 'active' : 'inactive'}">${available > 0 ? 'ACTIVE' : 'OFFLINE'}</span>
            </div>
        `;
        
        // Add to header
        const header = document.querySelector('.platform-header .header-content');
        if (header) {
            header.appendChild(badge);
        }
        
        // Add CSS
        if (!document.getElementById('browser-ai-styles')) {
            const style = document.createElement('style');
            style.id = 'browser-ai-styles';
            style.textContent = `
                .browser-ai-badge {
                    background: linear-gradient(135deg, #1f2937, #374151);
                    color: white;
                    padding: 0.5rem 1rem;
                    border-radius: 12px;
                    border: 1px solid #4b5563;
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
                    margin-left: auto;
                }
                
                .ai-badge-content {
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                    font-size: 0.875rem;
                    font-weight: 600;
                }
                
                .ai-status.active {
                    background: linear-gradient(135deg, #10b981, #059669);
                    color: white;
                    padding: 0.25rem 0.5rem;
                    border-radius: 8px;
                    font-size: 0.75rem;
                }
                
                .ai-status.inactive {
                    background: linear-gradient(135deg, #6b7280, #4b5563);
                    color: white;
                    padding: 0.25rem 0.5rem;
                    border-radius: 8px;
                    font-size: 0.75rem;
                }
            `;
            document.head.appendChild(style);
        }
    }

    // RFP Analysis with Browser AI
    async analyzeRFPContent(rfpContent, analysisType = 'requirements') {
        if (!this.features.summarizer) {
            throw new Error('Browser AI Summarizer not available - falling back to cloud API');
        }
        
        try {
            console.log(`📋 Analyzing RFP with Browser AI (${analysisType})...`);
            
            const summarizer = await Summarizer.create({
                ...this.configs.rfpAnalysis,
                monitor(m) {
                    m.addEventListener("downloadprogress", e => {
                        console.log(`📥 AI model download: ${(e.loaded * 100).toFixed(1)}%`);
                        platformManager.showNotification(`Downloading AI model: ${(e.loaded * 100).toFixed(1)}%`, 'info');
                    });
                }
            });
            
            const context = this.contextTemplates[analysisType] || this.contextTemplates.requirements;
            
            const startTime = performance.now();
            const analysis = await summarizer.summarize(rfpContent, { context });
            const processingTime = ((performance.now() - startTime) / 1000).toFixed(2);
            
            console.log(`✅ RFP analysis completed in ${processingTime}s`);
            
            return {
                success: true,
                analysis: analysis,
                analysis_type: analysisType,
                processing_time: `${processingTime}s (local AI)`,
                privacy_note: "🔒 Data processed locally - never sent to cloud",
                method: "Browser AI Summarizer"
            };
            
        } catch (error) {
            console.error('❌ Browser AI analysis failed:', error);
            throw error;
        }
    }

    // Proposal Content Generation with Browser AI
    async generateProposalContent(prompt, sectionType = 'technical') {
        if (!this.features.writer) {
            throw new Error('Browser AI Writer not available - falling back to cloud API');
        }
        
        try {
            console.log(`✍️ Generating ${sectionType} content with Browser AI...`);
            
            const writer = await Writer.create({
                ...this.configs.proposalWriting,
                monitor(m) {
                    m.addEventListener("downloadprogress", e => {
                        console.log(`📥 Writer model download: ${(e.loaded * 100).toFixed(1)}%`);
                        platformManager.showNotification(`Downloading writing model: ${(e.loaded * 100).toFixed(1)}%`, 'info');
                    });
                }
            });
            
            const startTime = performance.now();
            const content = await writer.write(prompt);
            const processingTime = ((performance.now() - startTime) / 1000).toFixed(2);
            
            console.log(`✅ Content generation completed in ${processingTime}s`);
            
            return {
                success: true,
                content: content,
                section_type: sectionType,
                processing_time: `${processingTime}s (local AI)`,
                privacy_note: "🔒 Generated locally - no data sent to external servers",
                method: "Browser AI Writer"
            };
            
        } catch (error) {
            console.error('❌ Browser AI writing failed:', error);
            throw error;
        }
    }

    // Streaming Content Generation
    async generateContentStreaming(prompt, outputElement, sectionType = 'technical') {
        if (!this.features.writer) {
            throw new Error('Browser AI Writer not available for streaming');
        }
        
        try {
            console.log(`🌊 Starting streaming generation for ${sectionType}...`);
            
            const writer = await Writer.create(this.configs.proposalWriting);
            const stream = writer.writeStreaming(prompt);
            
            outputElement.textContent = '';
            let totalContent = '';
            
            for await (const chunk of stream) {
                totalContent += chunk;
                outputElement.textContent = totalContent;
                
                // Scroll to keep content visible
                outputElement.scrollTop = outputElement.scrollHeight;
            }
            
            console.log('✅ Streaming generation completed');
            
            return {
                success: true,
                content: totalContent,
                method: "Browser AI Streaming Writer"
            };
            
        } catch (error) {
            console.error('❌ Streaming generation failed:', error);
            throw error;
        }
    }

    // Compliance Enhancement with Browser AI
    async enhanceCompliance(content, enhancementType = 'government_tone') {
        if (!this.features.rewriter) {
            throw new Error('Browser AI Rewriter not available - falling back to cloud API');
        }
        
        try {
            console.log(`🔄 Enhancing content for ${enhancementType}...`);
            
            const rewriter = await Rewriter.create({
                ...this.configs.complianceRewriting,
                monitor(m) {
                    m.addEventListener("downloadprogress", e => {
                        console.log(`📥 Rewriter model download: ${(e.loaded * 100).toFixed(1)}%`);
                        platformManager.showNotification(`Downloading enhancement model: ${(e.loaded * 100).toFixed(1)}%`, 'info');
                    });
                }
            });
            
            const contexts = {
                government_tone: "Rewrite to use formal government contracting language, ensure professional tone, remove informal expressions",
                section_508: "Enhance for Section 508 accessibility compliance, use clear language, include accommodation terminology",
                clarity: "Improve clarity and readability while maintaining technical accuracy, simplify complex terms",
                formal: "Increase formality level for government audience, use appropriate business terminology"
            };
            
            const context = contexts[enhancementType] || contexts.government_tone;
            
            const startTime = performance.now();
            const improvedContent = await rewriter.rewrite(content, { context });
            const processingTime = ((performance.now() - startTime) / 1000).toFixed(2);
            
            console.log(`✅ Content enhancement completed in ${processingTime}s`);
            
            return {
                success: true,
                original_content: content,
                improved_content: improvedContent,
                enhancement_type: enhancementType,
                processing_time: `${processingTime}s (local AI)`,
                privacy_note: "🔒 Sensitive content enhanced locally only",
                method: "Browser AI Rewriter"
            };
            
        } catch (error) {
            console.error('❌ Browser AI enhancement failed:', error);
            throw error;
        }
    }

    // Multi-step RFP Processing Pipeline
    async processRFPPipeline(rfpContent) {
        const results = {
            pipeline: "Browser AI RFP Processing",
            steps: []
        };
        
        try {
            // Step 1: Extract Requirements
            const requirements = await this.analyzeRFPContent(rfpContent, 'requirements');
            results.steps.push({
                step: "Requirements Extraction",
                ...requirements
            });
            
            // Step 2: Identify Deadlines
            const deadlines = await this.analyzeRFPContent(rfpContent, 'deadlines');
            results.steps.push({
                step: "Deadline Analysis", 
                ...deadlines
            });
            
            // Step 3: Compliance Analysis
            const compliance = await this.analyzeRFPContent(rfpContent, 'compliance');
            results.steps.push({
                step: "Compliance Review",
                ...compliance
            });
            
            // Step 4: Evaluation Criteria
            const evaluation = await this.analyzeRFPContent(rfpContent, 'evaluation');
            results.steps.push({
                step: "Evaluation Criteria",
                ...evaluation
            });
            
            results.success = true;
            results.total_steps = results.steps.length;
            results.privacy_note = "🔒 Entire pipeline processed locally with browser AI";
            
            console.log('✅ Complete RFP pipeline processing finished');
            
        } catch (error) {
            console.error('❌ RFP pipeline processing failed:', error);
            results.success = false;
            results.error = error.message;
        }
        
        return results;
    }

    // Check quota usage for large documents
    async checkInputQuota(text, apiType = 'summarizer') {
        if (!this.features[apiType]) {
            return { available: false, reason: `${apiType} API not available` };
        }
        
        try {
            let api;
            switch (apiType) {
                case 'summarizer':
                    api = await Summarizer.create(this.configs.rfpAnalysis);
                    break;
                case 'writer':
                    api = await Writer.create(this.configs.proposalWriting);
                    break;
                case 'rewriter':
                    api = await Rewriter.create(this.configs.complianceRewriting);
                    break;
                default:
                    throw new Error(`Unknown API type: ${apiType}`);
            }
            
            const usage = await api.measureInputUsage(text);
            const quota = api.inputQuota;
            
            return {
                available: true,
                usage: usage,
                quota: quota,
                percentage: quota === Infinity ? 0 : (usage / quota) * 100,
                canProcess: usage <= quota
            };
            
        } catch (error) {
            console.error(`❌ Quota check failed for ${apiType}:`, error);
            return { available: false, error: error.message };
        }
    }

    // Initialize Browser AI Integration
    async initialize() {
        console.log('🚀 Initializing Browser AI Integration...');
        
        // Detect capabilities
        await this.detectCapabilities();
        
        // Show status to user
        const available = Object.values(this.features).filter(Boolean).length;
        const total = Object.keys(this.features).length;
        
        if (available > 0) {
            platformManager.showNotification(
                `🤖 Browser AI activated: ${available}/${total} APIs available for local processing`,
                'success'
            );
        } else {
            platformManager.showNotification(
                '⚠️ Browser AI unavailable - using cloud APIs as fallback',
                'warning'
            );
        }
        
        return this.features;
    }
}

// Global Browser AI instance
const browserAI = new BrowserAIIntegration();

// Enhanced platform functions with Browser AI integration
async function processDocumentsWithBrowserAI() {
    try {
        const fileInput = document.getElementById('pdf-file');
        const analysisType = document.getElementById('analysis-type')?.value || 'requirements';
        
        if (!fileInput.files || fileInput.files.length === 0) {
            platformManager.showNotification('Please select PDF files to process', 'error');
            return;
        }
        
        platformManager.showLoading('Processing with Browser AI...');
        
        // Read file content
        const file = fileInput.files[0];
        const text = await file.text(); // Simplified - in reality would need PDF parsing
        
        try {
            // Try Browser AI first
            const result = await browserAI.analyzeRFPContent(text, analysisType);
            
            platformManager.hideLoading();
            platformManager.showResults('processing-results', {
                success: true,
                method: result.method,
                processing_time: result.processing_time,
                privacy: result.privacy_note,
                analysis_type: result.analysis_type
            });
            
            platformManager.showNotification('✅ Document processed with Browser AI!', 'success');
            
        } catch (browserAIError) {
            console.warn('Browser AI failed, falling back to cloud:', browserAIError);
            
            // Fallback to original cloud processing
            return platformManager.processDocuments();
        }
        
    } catch (error) {
        platformManager.hideLoading();
        platformManager.showNotification('❌ Processing failed: ' + error.message, 'error');
    }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', async () => {
    console.log('🎯 Starting Browser AI integration...');
    await browserAI.initialize();
});

// Export for global access
window.browserAI = browserAI;
window.processDocumentsWithBrowserAI = processDocumentsWithBrowserAI;