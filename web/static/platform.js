// Platform Capabilities JavaScript
class PlatformManager {
    constructor() {
        this.currentCapability = null;
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        // Close modal when clicking outside
        document.getElementById('capability-modal').addEventListener('click', (e) => {
            if (e.target.id === 'capability-modal') {
                this.closeModal();
            }
        });

        // ESC key to close modal
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeModal();
            }
        });
    }

    openCapability(capabilityType) {
        this.currentCapability = capabilityType;
        const modal = document.getElementById('capability-modal');
        const modalTitle = document.getElementById('modal-title');
        const modalBody = document.getElementById('modal-body');

        // Set title and content based on capability
        switch (capabilityType) {
            case 'govcon-agent':
                modalTitle.textContent = 'AI GovCon Agent';
                modalBody.innerHTML = this.getGovConAgentInterface();
                break;
            case 'opportunity-match':
                modalTitle.textContent = 'Smart Opportunity Match';
                modalBody.innerHTML = this.getOpportunityMatchInterface();
                break;
            case 'pursuit-management':
                modalTitle.textContent = 'Pursuit Management';
                modalBody.innerHTML = this.getPursuitManagementInterface();
                break;
            case 'document-hub':
                modalTitle.textContent = 'Document Hub';
                modalBody.innerHTML = this.getDocumentHubInterface();
                break;
            case 'teaming-insights':
                modalTitle.textContent = 'Teaming Insights';
                modalBody.innerHTML = this.getTeamingInsightsInterface();
                break;
        }

        modal.style.display = 'block';
        this.initializeCapabilityFeatures(capabilityType);
    }

    closeModal() {
        document.getElementById('capability-modal').style.display = 'none';
        this.currentCapability = null;
    }

    getGovConAgentInterface() {
        return `
            <div class="feature-interface">
                <div class="federal-enhancement-banner">
                    <div class="banner-content">
                        <h4>🏛️ Federal Contracting AI - Specialized for Government Proposals</h4>
                        <p>Addresses specific shortcomings of general AI identified by GovDash analysis</p>
                        <div class="enhancement-features">
                            <span class="enhancement-tag">📋 Section L/M/C Analysis</span>
                            <span class="enhancement-tag">⚖️ Requirements Matrix</span>
                            <span class="enhancement-tag">🧠 Context Retention</span>
                            <span class="enhancement-tag">🔍 Compliance Validation</span>
                        </div>
                    </div>
                </div>

                <div class="ai-enhancement-banner">
                    <div class="banner-content">
                        <h4>🤖 Enhanced with Browser AI + Federal Expertise</h4>
                        <p>Local processing with specialized federal contracting knowledge</p>
                        <div class="ai-benefits">
                            <span class="benefit-tag">🔒 Private & Secure</span>
                            <span class="benefit-tag">⚡ Instant Processing</span>
                            <span class="benefit-tag">💰 Zero API Costs</span>
                            <span class="benefit-tag">�️ Federal-Specific</span>
                        </div>
                    </div>
                </div>

                <div class="feature-section">
                    <h4>PDF Document Processing - Federal RFP Analysis</h4>
                    <div class="upload-area" id="pdf-upload">
                        <div class="upload-icon">📄</div>
                        <p>Drop your federal RFP documents here (200+ pages supported)</p>
                        <small>Specialized for Sections L, M, C analysis and requirements extraction</small>
                        <div class="processing-note">
                            <span class="ai-badge">🏛️ Federal AI</span>
                            Analyzes federal structure, compliance requirements, and risk factors
                        </div>
                        <input type="file" id="pdf-file" accept=".pdf" style="display: none;" multiple>
                    </div>
                </div>
                
                <div class="feature-section">
                    <h4>Federal Analysis Options</h4>
                    <div class="analysis-grid">
                        <div class="analysis-option">
                            <input type="radio" id="federal-structure" name="analysis-type" value="federal_structure" checked>
                            <label for="federal-structure">
                                <div class="option-header">
                                    <span class="option-icon">🏛️</span>
                                    <span class="option-title">Federal Structure Analysis</span>
                                </div>
                                <p>Analyze Sections L, M, C structure and extract requirements matrix</p>
                                <div class="option-features">
                                    <span class="feature-point">• Section L/M/C parsing</span>
                                    <span class="feature-point">• Requirements matrix</span>
                                    <span class="feature-point">• Evaluation factors</span>
                                </div>
                            </label>
                        </div>
                        
                        <div class="analysis-option">
                            <input type="radio" id="compliance-analysis" name="analysis-type" value="compliance">
                            <label for="compliance-analysis">
                                <div class="option-header">
                                    <span class="option-icon">⚖️</span>
                                    <span class="option-title">Compliance & Risk Analysis</span>
                                </div>
                                <p>Identify compliance requirements, risk factors, and regulatory needs</p>
                                <div class="option-features">
                                    <span class="feature-point">• FAR/DFARS compliance</span>
                                    <span class="feature-point">• Section 508 requirements</span>
                                    <span class="feature-point">• Risk factor identification</span>
                                </div>
                            </label>
                        </div>
                        
                        <div class="analysis-option">
                            <input type="radio" id="evaluation-analysis" name="analysis-type" value="evaluation">
                            <label for="evaluation-analysis">
                                <div class="option-header">
                                    <span class="option-icon">📊</span>
                                    <span class="option-title">Evaluation Criteria Mapping</span>
                                </div>
                                <p>Extract evaluation factors, weights, and scoring methodology</p>
                                <div class="option-features">
                                    <span class="feature-point">• Factor identification</span>
                                    <span class="feature-point">• Weight extraction</span>
                                    <span class="feature-point">• Scoring methodology</span>
                                </div>
                            </label>
                        </div>
                        
                        <div class="analysis-option">
                            <input type="radio" id="context-generation" name="analysis-type" value="context_aware">
                            <label for="context-generation">
                                <div class="option-header">
                                    <span class="option-icon">🧠</span>
                                    <span class="option-title">Context-Aware Proposal Generation</span>
                                </div>
                                <p>Generate proposal sections with maintained context and compliance focus</p>
                                <div class="option-features">
                                    <span class="feature-point">• Context retention</span>
                                    <span class="feature-point">• Federal language</span>
                                    <span class="feature-point">• Compliance-focused</span>
                                </div>
                            </label>
                        </div>
                    </div>
                </div>

                <div class="feature-section">
                    <div class="action-buttons">
                        <button class="btn btn-primary" onclick="processFederalRFP()">
                            <span class="btn-icon">🏛️</span>
                            <span class="btn-text">Analyze Federal RFP</span>
                        </button>
                        <button class="btn btn-secondary" onclick="generateFederalProposal()">
                            <span class="btn-icon">📝</span>
                            <span class="btn-text">Generate Proposal Section</span>
                        </button>
                        <button class="btn btn-secondary" onclick="validateFederalCompliance()">
                            <span class="btn-icon">✅</span>
                            <span class="btn-text">Validate Compliance</span>
                        </button>
                    </div>
                    <div class="federal-advantages">
                        <h5>🎯 Addresses General AI Shortcomings:</h5>
                        <div class="advantage-grid">
                            <div class="advantage-item">
                                <span class="advantage-icon">🧠</span>
                                <div class="advantage-content">
                                    <strong>Context Retention</strong>
                                    <p>Maintains RFP context across all proposal sections</p>
                                </div>
                            </div>
                            <div class="advantage-item">
                                <span class="advantage-icon">🏛️</span>
                                <div class="advantage-content">
                                    <strong>Federal Structure Awareness</strong>
                                    <p>Understands Sections L, M, C and federal formatting</p>
                                </div>
                            </div>
                            <div class="advantage-item">
                                <span class="advantage-icon">⚖️</span>
                                <div class="advantage-content">
                                    <strong>Compliance Focus</strong>
                                    <p>Built-in FAR, DFARS, and regulatory knowledge</p>
                                </div>
                            </div>
                            <div class="advantage-item">
                                <span class="advantage-icon">📝</span>
                                <div class="advantage-content">
                                    <strong>Non-Generic Language</strong>
                                    <p>Government-appropriate tone and terminology</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div id="processing-results" class="results-container" style="display: none;">
                    <h4>Federal Analysis Results</h4>
                    <div id="results-content"></div>
                </div>
            </div>
        `;
    }

    getOpportunityMatchInterface() {
        return `
            <div class="feature-interface">
                <div class="feature-section">
                    <h4>Opportunity Data Input</h4>
                    <div class="tabs">
                        <button class="tab active" onclick="platformManager.switchTab('sam-data')">SAM.gov Data</button>
                        <button class="tab" onclick="platformManager.switchTab('manual-input')">Manual Input</button>
                        <button class="tab" onclick="platformManager.switchTab('batch-upload')">Batch Upload</button>
                    </div>
                    
                    <div id="sam-data" class="tab-content active">
                        <div class="form-group">
                            <label>SAM.gov Notice ID</label>
                            <input type="text" class="form-input" id="sam-notice-id" placeholder="Enter notice ID">
                        </div>
                        <button class="btn btn-secondary" onclick="platformManager.fetchSAMData()">Fetch SAM Data</button>
                    </div>
                    
                    <div id="manual-input" class="tab-content">
                        <div class="form-group">
                            <label>Agency</label>
                            <input type="text" class="form-input" id="agency" placeholder="Enter agency name">
                        </div>
                        <div class="form-group">
                            <label>NAICS Code</label>
                            <input type="text" class="form-input" id="naics" placeholder="Enter NAICS code">
                        </div>
                        <div class="form-group">
                            <label>Contract Value (USD)</label>
                            <input type="number" class="form-input" id="contract-value" placeholder="Enter estimated value">
                        </div>
                    </div>
                    
                    <div id="batch-upload" class="tab-content">
                        <div class="upload-area" id="batch-upload-area">
                            <div class="upload-icon">📊</div>
                            <p>Upload CSV or Excel file with opportunity data</p>
                            <input type="file" id="batch-file" accept=".csv,.xlsx,.xls" style="display: none;">
                        </div>
                    </div>
                </div>

                <div class="feature-section">
                    <h4>Scoring Configuration</h4>
                    <div class="form-group">
                        <label>Company Revenue (USD)</label>
                        <input type="number" class="form-input" id="company-revenue" placeholder="Your company's annual revenue">
                    </div>
                    <div class="form-group">
                        <label>Technical Capabilities</label>
                        <select class="form-select" id="tech-capabilities" multiple>
                            <option value="cloud">Cloud Computing</option>
                            <option value="ai-ml">AI/ML</option>
                            <option value="cybersecurity">Cybersecurity</option>
                            <option value="data-analytics">Data Analytics</option>
                            <option value="software-dev">Software Development</option>
                        </select>
                    </div>
                </div>

                <div class="feature-section">
                    <button class="btn btn-primary" onclick="platformManager.scoreOpportunities()">
                        Score Opportunities
                    </button>
                </div>

                <div id="scoring-results" class="results-container" style="display: none;">
                    <h4>Opportunity Scores</h4>
                    <div id="opportunity-scores"></div>
                </div>
            </div>
        `;
    }

    getPursuitManagementInterface() {
        return `
            <div class="feature-interface">
                <div class="feature-section">
                    <h4>Active Pursuits Dashboard</h4>
                    <div class="metrics-grid">
                        <div class="metric-card">
                            <div class="metric-value">12</div>
                            <div class="metric-label">Active Pursuits</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">8</div>
                            <div class="metric-label">GO Decisions</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">3</div>
                            <div class="metric-label">Under Review</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">$2.4M</div>
                            <div class="metric-label">Total Value</div>
                        </div>
                    </div>
                </div>

                <div class="feature-section">
                    <h4>Pursuit Analysis</h4>
                    <div class="form-group">
                        <label>Select Pursuit</label>
                        <select class="form-select" id="pursuit-select">
                            <option value="">Choose a pursuit to analyze</option>
                            <option value="dod-ai-2024">DoD AI Platform (Score: 85)</option>
                            <option value="nasa-cloud-2024">NASA Cloud Migration (Score: 72)</option>
                            <option value="hhs-data-2024">HHS Data Analytics (Score: 68)</option>
                        </select>
                    </div>
                    <button class="btn btn-primary" onclick="platformManager.analyzePursuit()">Analyze Pursuit</button>
                </div>

                <div id="pursuit-analysis" class="results-container" style="display: none;">
                    <div class="tabs">
                        <button class="tab active" onclick="platformManager.switchTab('blockers')">Blockers</button>
                        <button class="tab" onclick="platformManager.switchTab('actions')">Next Actions</button>
                        <button class="tab" onclick="platformManager.switchTab('competitors')">Competitors</button>
                        <button class="tab" onclick="platformManager.switchTab('value-alignment')">Value Alignment</button>
                    </div>
                    
                    <div id="blockers" class="tab-content active">
                        <h5>Identified Blockers</h5>
                        <div class="result-item">
                            <span>Missing security clearance requirements</span>
                            <span class="result-score" style="background: #ef4444;">High</span>
                        </div>
                        <div class="result-item">
                            <span>Incumbent advantage in technical approach</span>
                            <span class="result-score" style="background: #f59e0b;">Medium</span>
                        </div>
                    </div>
                    
                    <div id="actions" class="tab-content">
                        <h5>Recommended Next Actions</h5>
                        <ul style="list-style: none; padding: 0;">
                            <li style="padding: 0.5rem 0; border-bottom: 1px solid var(--border-color);">✅ Initiate security clearance process</li>
                            <li style="padding: 0.5rem 0; border-bottom: 1px solid var(--border-color);">📋 Schedule technical review meeting</li>
                            <li style="padding: 0.5rem 0; border-bottom: 1px solid var(--border-color);">🤝 Identify potential teaming partners</li>
                            <li style="padding: 0.5rem 0;">📊 Conduct competitive analysis</li>
                        </ul>
                    </div>
                    
                    <div id="competitors" class="tab-content">
                        <h5>Competitor Analysis</h5>
                        <div class="result-item">
                            <span>Raytheon Technologies</span>
                            <span class="result-score">Incumbent</span>
                        </div>
                        <div class="result-item">
                            <span>Lockheed Martin</span>
                            <span class="result-score" style="background: #f59e0b;">Strong</span>
                        </div>
                    </div>
                    
                    <div id="value-alignment" class="tab-content">
                        <h5>Value Alignment Score: 78/100</h5>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: 78%;"></div>
                        </div>
                        <p style="margin-top: 1rem; color: var(--text-secondary);">
                            Strong alignment with agency priorities. Technical capabilities match 85% of requirements.
                            Financial profile suitable for contract size.
                        </p>
                    </div>
                </div>
            </div>
        `;
    }

    getDocumentHubInterface() {
        return `
            <div class="feature-interface">
                <div class="feature-section">
                    <h4>Document Upload & Processing</h4>
                    <div class="upload-area" id="multi-upload">
                        <div class="upload-icon">📁</div>
                        <p>Drop mixed-format documents here (ZIP, PDF, DOCX, MD)</p>
                        <small>Supports batch processing and automatic format detection</small>
                        <input type="file" id="multi-files" multiple style="display: none;">
                    </div>
                </div>

                <div class="feature-section">
                    <h4>Document Library</h4>
                    <div class="tabs">
                        <button class="tab active" onclick="platformManager.switchTab('all-docs')">All Documents</button>
                        <button class="tab" onclick="platformManager.switchTab('rfps')">RFPs</button>
                        <button class="tab" onclick="platformManager.switchTab('proposals')">Proposals</button>
                        <button class="tab" onclick="platformManager.switchTab('references')">References</button>
                    </div>
                    
                    <div id="all-docs" class="tab-content active">
                        <div class="result-item">
                            <div>
                                <strong>DoD_AI_Platform_RFP.pdf</strong>
                                <br><small>Uploaded: 2024-10-01 | Size: 2.4 MB | Status: Processed</small>
                            </div>
                            <button class="btn btn-secondary">View</button>
                        </div>
                        <div class="result-item">
                            <div>
                                <strong>NASA_Cloud_SOW.docx</strong>
                                <br><small>Uploaded: 2024-09-28 | Size: 1.8 MB | Status: Processing</small>
                            </div>
                            <button class="btn btn-secondary">View</button>
                        </div>
                    </div>
                </div>

                <div class="feature-section">
                    <h4>Document Analytics</h4>
                    <div class="metrics-grid">
                        <div class="metric-card">
                            <div class="metric-value">156</div>
                            <div class="metric-label">Total Documents</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">89%</div>
                            <div class="metric-label">Processing Success</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">2.1 GB</div>
                            <div class="metric-label">Total Storage</div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    getTeamingInsightsInterface() {
        return `
            <div class="feature-interface">
                <div class="feature-section">
                    <h4>Market Intelligence</h4>
                    <div class="form-group">
                        <label>Search Scope</label>
                        <select class="form-select" id="search-scope">
                            <option value="agency">By Agency</option>
                            <option value="naics">By NAICS Code</option>
                            <option value="keyword">By Keywords</option>
                            <option value="contractor">By Contractor</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Search Term</label>
                        <input type="text" class="form-input" id="search-term" placeholder="Enter search criteria">
                    </div>
                    <button class="btn btn-primary" onclick="platformManager.searchTeamingData()">Search Insights</button>
                </div>

                <div class="feature-section">
                    <h4>Incumbent Analysis</h4>
                    <div id="incumbent-results" class="results-container">
                        <div class="result-item">
                            <div>
                                <strong>Raytheon Technologies</strong>
                                <br><small>Win Rate: 68% | Avg Contract: $12.4M | Active: 23 contracts</small>
                            </div>
                            <span class="result-score">Dominant</span>
                        </div>
                        <div class="result-item">
                            <div>
                                <strong>Lockheed Martin</strong>
                                <br><small>Win Rate: 54% | Avg Contract: $8.7M | Active: 18 contracts</small>
                            </div>
                            <span class="result-score" style="background: #f59e0b;">Strong</span>
                        </div>
                        <div class="result-item">
                            <div>
                                <strong>General Dynamics</strong>
                                <br><small>Win Rate: 41% | Avg Contract: $6.2M | Active: 12 contracts</small>
                            </div>
                            <span class="result-score" style="background: #64748b;">Moderate</span>
                        </div>
                    </div>
                </div>

                <div class="feature-section">
                    <h4>Teaming Recommendations</h4>
                    <div class="tabs">
                        <button class="tab active" onclick="platformManager.switchTab('prime-opportunities')">Prime Opportunities</button>
                        <button class="tab" onclick="platformManager.switchTab('sub-opportunities')">Subcontractor Opportunities</button>
                        <button class="tab" onclick="platformManager.switchTab('joint-ventures')">Joint Ventures</button>
                    </div>
                    
                    <div id="prime-opportunities" class="tab-content active">
                        <div class="result-item">
                            <div>
                                <strong>DoD Cybersecurity Platform</strong>
                                <br><small>Low incumbent density | High technical match | Est. Value: $15M</small>
                            </div>
                            <span class="result-score">Recommended</span>
                        </div>
                    </div>
                    
                    <div id="sub-opportunities" class="tab-content">
                        <div class="result-item">
                            <div>
                                <strong>Partner with Boeing on NASA Contract</strong>
                                <br><small>AI/ML specialty needed | 6-month timeline | Est. Sub value: $3.2M</small>
                            </div>
                            <span class="result-score">High Match</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    initializeCapabilityFeatures(capabilityType) {
        // Initialize file upload handlers
        this.initializeFileUploads();
        
        // Initialize specific features based on capability
        switch (capabilityType) {
            case 'govcon-agent':
                this.initializeGovConAgent();
                break;
            case 'opportunity-match':
                this.initializeOpportunityMatch();
                break;
            case 'pursuit-management':
                this.initializePursuitManagement();
                break;
            case 'document-hub':
                this.initializeDocumentHub();
                break;
            case 'teaming-insights':
                this.initializeTeamingInsights();
                break;
        }
    }

    initializeFileUploads() {
        // Handle file upload areas
        const uploadAreas = document.querySelectorAll('.upload-area');
        uploadAreas.forEach(area => {
            const fileInput = area.querySelector('input[type="file"]');
            
            area.addEventListener('click', () => {
                if (fileInput) fileInput.click();
            });

            area.addEventListener('dragover', (e) => {
                e.preventDefault();
                area.classList.add('dragover');
            });

            area.addEventListener('dragleave', () => {
                area.classList.remove('dragover');
            });

            area.addEventListener('drop', (e) => {
                e.preventDefault();
                area.classList.remove('dragover');
                const files = e.dataTransfer.files;
                this.handleFiles(files, fileInput);
            });
            
            // Handle file input change
            if (fileInput) {
                fileInput.addEventListener('change', (e) => {
                    this.handleFiles(e.target.files, fileInput);
                });
            }
        });
    }

    switchTab(tabId) {
        // Hide all tab contents
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        
        // Remove active class from all tabs
        document.querySelectorAll('.tab').forEach(tab => {
            tab.classList.remove('active');
        });
        
        // Show selected tab content and mark tab as active
        const targetContent = document.getElementById(tabId);
        const targetTab = event.target;
        
        if (targetContent) targetContent.classList.add('active');
        if (targetTab) targetTab.classList.add('active');
    }

    // Enhanced RFP Pipeline Processing with Browser AI
    async processRFPPipeline() {
        try {
            const fileInput = document.getElementById('pdf-file');
            
            if (!fileInput.files || fileInput.files.length === 0) {
                this.showNotification('Please select an RFP file for pipeline analysis', 'error');
                return;
            }
            
            this.showLoading('Running full RFP analysis pipeline...');
            
            // Read file content (simplified - would need actual PDF parsing)
            const file = fileInput.files[0];
            const text = await file.text();
            
            // Check if Browser AI is available
            if (window.browserAI && Object.values(window.browserAI.features).some(Boolean)) {
                console.log('🔄 Starting Browser AI pipeline processing...');
                
                const pipelineResult = await window.browserAI.processRFPPipeline(text);
                
                this.hideLoading();
                this.displayPipelineResults(pipelineResult);
                
                if (pipelineResult.success) {
                    this.showNotification(`✅ Pipeline completed: ${pipelineResult.total_steps} steps processed with Browser AI!`, 'success');
                } else {
                    this.showNotification('⚠️ Pipeline completed with some errors', 'warning');
                }
                
            } else {
                // Fallback to cloud processing
                console.log('🌐 Browser AI unavailable, using cloud pipeline...');
                this.hideLoading();
                this.showNotification('🌐 Processing with cloud APIs...', 'info');
                
                // Simulate cloud pipeline (would integrate with actual backend)
                setTimeout(() => {
                    this.displayPipelineResults({
                        pipeline: "Cloud API Processing",
                        success: true,
                        steps: [
                            {
                                step: "Requirements Extraction",
                                success: true,
                                method: "Cloud API",
                                processing_time: "3.2s"
                            },
                            {
                                step: "Deadline Analysis", 
                                success: true,
                                method: "Cloud API",
                                processing_time: "2.8s"
                            }
                        ],
                        total_steps: 2
                    });
                    this.showNotification('✅ Cloud pipeline processing completed', 'success');
                }, 2000);
            }
            
        } catch (error) {
            this.hideLoading();
            console.error('Pipeline processing failed:', error);
            this.showNotification('❌ Pipeline processing failed: ' + error.message, 'error');
        }
    }
    
    displayPipelineResults(results) {
        const container = document.getElementById('processing-results');
        if (!container) return;
        
        container.style.display = 'block';
        
        let html = `
            <div class="pipeline-results">
                <div class="pipeline-header">
                    <h4>🔄 ${results.pipeline}</h4>
                    <div class="pipeline-status ${results.success ? 'success' : 'error'}">
                        ${results.success ? '✅ Completed' : '❌ Failed'}
                    </div>
                </div>
        `;
        
        if (results.success && results.steps) {
            html += `<div class="pipeline-steps">`;
            
            results.steps.forEach((step, index) => {
                html += `
                    <div class="pipeline-step ${step.success ? 'completed' : 'failed'}">
                        <div class="step-header">
                            <span class="step-title">${index + 1}. ${step.step}</span>
                            <span class="step-status">${step.success ? 'Completed' : 'Failed'}</span>
                        </div>
                        <div class="step-content">
                            <p><strong>Method:</strong> ${step.method || 'Unknown'}</p>
                            <p><strong>Time:</strong> ${step.processing_time || 'N/A'}</p>
                            ${step.privacy_note ? `<p><strong>Privacy:</strong> ${step.privacy_note}</p>` : ''}
                            ${step.analysis ? `<div class="step-analysis"><strong>Analysis:</strong><br>${step.analysis.substring(0, 200)}...</div>` : ''}
                        </div>
                    </div>
                `;
            });
            
            html += `</div>`;
            
            if (results.privacy_note) {
                html += `
                    <div class="pipeline-privacy">
                        <p><strong>${results.privacy_note}</strong></p>
                    </div>
                `;
            }
        }
        
        if (!results.success && results.error) {
            html += `
                <div class="pipeline-error">
                    <p><strong>Error:</strong> ${results.error}</p>
                </div>
            `;
        }
        
        html += `</div>`;
        
        const contentDiv = container.querySelector('#results-content');
        if (contentDiv) {
            contentDiv.innerHTML = html;
        }
    }
    async processDocuments() {
        this.showLoading('Processing documents...');
        
        try {
            // Get uploaded files
            const fileInput = document.getElementById('pdf-file');
            const analysisType = document.getElementById('analysis-type').value;
            const outputFormat = document.getElementById('output-format').value;
            
            // Check for files from input or drag-and-drop
            let files = null;
            if (fileInput.files && fileInput.files.length > 0) {
                files = fileInput.files;
            } else if (fileInput._droppedFiles) {
                files = fileInput._droppedFiles;
            }
            
            if (!files || files.length === 0) {
                this.hideLoading();
                this.showNotification('Please select PDF files to process', 'error');
                return;
            }
            
            // Create FormData for file upload
            const formData = new FormData();
            Array.from(files).forEach(file => {
                formData.append('files', file);
            });
            formData.append('analysis_type', analysisType);
            formData.append('output_format', outputFormat);
            
            // Make API call to backend
            const response = await fetch('/api/platform/govcon-agent/process', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            
            this.hideLoading();
            
            if (result.status === 'success') {
                this.showResults('processing-results', {
                    documents_processed: result.documents_processed,
                    sections: result.sections.length,
                    requirements: result.requirements.length,
                    deadlines: result.deadlines.length,
                    compliance_score: result.compliance_score,
                    processing_time: Math.round(result.processing_time * 100) / 100
                });
                this.showNotification('Documents processed successfully!');
            } else {
                this.showNotification('Processing failed: ' + (result.error || 'Unknown error'), 'error');
            }
            
        } catch (error) {
            this.hideLoading();
            console.error('Error processing documents:', error);
            this.showNotification('Error processing documents: ' + error.message, 'error');
        }
    }

    async scoreOpportunities() {
        this.showLoading('Scoring opportunities...');
        
        try {
            // Get form data
            const companyRevenue = document.getElementById('company-revenue').value;
            const techCapabilities = Array.from(document.getElementById('tech-capabilities').selectedOptions)
                .map(option => option.value);
            
            // Get opportunity data based on active tab
            let opportunities = [];
            let companyProfile = {
                revenue: parseInt(companyRevenue) || 0,
                capabilities: techCapabilities
            };
            
            // For demo purposes, create sample opportunity data
            opportunities = [
                {
                    title: "AI Platform Development",
                    agency: "Department of Defense",
                    naics: "541511",
                    estimated_value: 15000000
                }
            ];
            
            // Make API call to backend
            const response = await fetch('/api/platform/opportunity-match/score', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    opportunities: opportunities,
                    company_profile: companyProfile
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            
            this.hideLoading();
            
            if (result.status === 'success') {
                this.showResults('scoring-results', {
                    total_opportunities: result.total_opportunities,
                    go_decisions: result.summary.go_decisions,
                    review_needed: result.summary.review_needed,
                    no_bid: result.summary.no_bid,
                    average_score: Math.round(result.summary.average_score)
                });
                this.showNotification('Opportunities scored successfully!');
            } else {
                this.showNotification('Scoring failed: ' + (result.error || 'Unknown error'), 'error');
            }
            
        } catch (error) {
            this.hideLoading();
            console.error('Error scoring opportunities:', error);
            this.showNotification('Error scoring opportunities: ' + error.message, 'error');
        }
    }

    analyzePursuit() {
        const pursuitSelect = document.getElementById('pursuit-select');
        if (!pursuitSelect.value) {
            this.showNotification('Please select a pursuit to analyze', 'error');
            return;
        }
        
        document.getElementById('pursuit-analysis').style.display = 'block';
        this.showNotification('Pursuit analysis updated');
    }

    async fetchSAMData() {
        const noticeId = document.getElementById('sam-notice-id').value;
        if (!noticeId) {
            this.showNotification('Please enter a SAM.gov notice ID', 'error');
            return;
        }
        
        this.showLoading('Fetching SAM data...');
        
        try {
            const response = await fetch(`/api/platform/opportunity-match/sam/${encodeURIComponent(noticeId)}`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            
            this.hideLoading();
            
            if (result.notice_id) {
                // Populate form fields with SAM data
                if (result.agency) document.getElementById('agency').value = result.agency;
                if (result.naics) document.getElementById('naics').value = result.naics;
                if (result.estimated_value) document.getElementById('contract-value').value = result.estimated_value;
                
                this.showNotification('SAM data fetched successfully');
            } else if (result.notice === 'missing_sam_key') {
                this.showNotification('SAM.gov API key not configured', 'error');
            } else {
                this.showNotification('SAM data fetched but incomplete');
            }
            
        } catch (error) {
            this.hideLoading();
            console.error('Error fetching SAM data:', error);
            this.showNotification('Error fetching SAM data: ' + error.message, 'error');
        }
    }

    async searchTeamingData() {
        const searchScope = document.getElementById('search-scope').value;
        const searchTerm = document.getElementById('search-term').value;
        
        if (!searchTerm) {
            this.showNotification('Please enter a search term', 'error');
            return;
        }
        
        this.showLoading('Searching teaming insights...');
        
        try {
            const response = await fetch(`/api/platform/teaming-insights/search?scope=${encodeURIComponent(searchScope)}&term=${encodeURIComponent(searchTerm)}`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            
            this.hideLoading();
            
            if (result.results_count > 0) {
                this.showNotification(`Found ${result.results_count} teaming insights`);
                // Update the incumbent results display
                this.updateIncumbentResults(result.incumbents);
            } else {
                this.showNotification('No teaming insights found for this search');
            }
            
        } catch (error) {
            this.hideLoading();
            console.error('Error searching teaming data:', error);
            this.showNotification('Error searching teaming data: ' + error.message, 'error');
        }
    }

    updateIncumbentResults(incumbents) {
        const container = document.getElementById('incumbent-results');
        if (container && incumbents) {
            container.innerHTML = incumbents.map(incumbent => `
                <div class="result-item">
                    <div>
                        <strong>${incumbent.contractor}</strong>
                        <br><small>Win Rate: ${incumbent.win_rate}% | Avg Contract: $${(incumbent.avg_contract_value / 1000000).toFixed(1)}M | Active: ${incumbent.active_contracts} contracts</small>
                    </div>
                    <span class="result-score">${incumbent.status}</span>
                </div>
            `).join('');
        }
    }

    // Enhanced utility methods
    showLoading(message = 'Loading...') {
        const buttons = document.querySelectorAll('.btn-primary, .demo-btn, .launch-btn');
        buttons.forEach(btn => {
            btn.classList.add('loading');
            btn.setAttribute('data-original-text', btn.textContent);
            btn.innerHTML = `<span class="spinner"></span> ${message}`;
            btn.disabled = true;
        });
    }

    hideLoading() {
        const buttons = document.querySelectorAll('.btn-primary, .demo-btn, .launch-btn');
        buttons.forEach(btn => {
            btn.classList.remove('loading');
            const originalText = btn.getAttribute('data-original-text');
            if (originalText) {
                btn.textContent = originalText;
                btn.removeAttribute('data-original-text');
            }
            btn.disabled = false;
        });
    }

    showResults(containerId, data) {
        const container = document.getElementById(containerId);
        if (container) {
            container.style.display = 'block';
            container.style.animation = 'slideInUp 0.4s ease';
            const content = container.querySelector('#results-content') || container.querySelector(`#${containerId.replace('-results', '-scores')}`);
            if (content) {
                content.innerHTML = this.formatResults(data);
            }
        }
    }

    formatResults(data) {
        return Object.entries(data).map(([key, value]) => {
            const formattedKey = key.replace(/_/g, ' ').toUpperCase();
            let scoreClass = 'result-score';
            
            // Add dynamic color coding based on value
            if (typeof value === 'number') {
                if (value >= 80) scoreClass += ' high-score';
                else if (value >= 60) scoreClass += ' medium-score';
                else scoreClass += ' low-score';
            }
            
            return `<div class="result-item">
                <span>${formattedKey}</span>
                <span class="${scoreClass}">${value}</span>
            </div>`;
        }).join('');
    }

    showNotification(message, type = 'success') {
        // Remove existing notifications
        const existingNotifications = document.querySelectorAll('.notification');
        existingNotifications.forEach(n => n.remove());
        
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        
        // Add icon based on type
        let icon = '';
        switch(type) {
            case 'success': icon = '✅ '; break;
            case 'error': icon = '❌ '; break;
            case 'warning': icon = '⚠️ '; break;
            default: icon = 'ℹ️ ';
        }
        
        notification.innerHTML = `${icon}${message}`;
        document.body.appendChild(notification);
        
        // Auto-remove after 4 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.style.animation = 'slideOutRight 0.3s ease';
                setTimeout(() => notification.remove(), 300);
            }
        }, 4000);
    }

    // Enhanced file handling with better feedback
    handleFiles(files, fileInput = null) {
        if (files && files.length > 0) {
            const fileNames = Array.from(files).map(f => f.name);
            const totalSize = Array.from(files).reduce((sum, f) => sum + f.size, 0);
            const formattedSize = this.formatFileSize(totalSize);
            
            if (fileInput && files instanceof FileList) {
                fileInput._droppedFiles = files;
            }
            
            // Show enhanced notification with file details
            if (fileNames.length === 1) {
                this.showNotification(`File selected: ${fileNames[0]} (${formattedSize})`);
            } else {
                this.showNotification(`${fileNames.length} files selected (${formattedSize} total)`);
            }
            
            // Add visual feedback to upload area
            const uploadArea = document.querySelector('.upload-area');
            if (uploadArea) {
                uploadArea.style.borderColor = '#10b981';
                uploadArea.style.background = 'linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%)';
                
                setTimeout(() => {
                    uploadArea.style.borderColor = '';
                    uploadArea.style.background = '';
                }, 2000);
            }
            
            Array.from(files).forEach(file => {
                console.log('File selected:', file.name, 'Size:', this.formatFileSize(file.size));
            });
        }
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    // Enhanced error handling
    handleError(error, context = '') {
        console.error(`Error in ${context}:`, error);
        let message = 'An unexpected error occurred';
        
        if (error.message) {
            message = error.message;
        } else if (typeof error === 'string') {
            message = error;
        }
        
        this.showNotification(`${context ? context + ': ' : ''}${message}`, 'error');
    }

    // Add button click effects
    addButtonEffects() {
        document.addEventListener('click', (e) => {
            if (e.target.matches('.launch-btn, .demo-btn, .btn-primary, .btn-secondary')) {
                // Create ripple effect
                const button = e.target;
                const ripple = document.createElement('span');
                const rect = button.getBoundingClientRect();
                const size = Math.max(rect.width, rect.height);
                const x = e.clientX - rect.left - size / 2;
                const y = e.clientY - rect.top - size / 2;
                
                ripple.style.cssText = `
                    position: absolute;
                    border-radius: 50%;
                    background: rgba(255, 255, 255, 0.3);
                    transform: scale(0);
                    animation: ripple 0.6s linear;
                    left: ${x}px;
                    top: ${y}px;
                    width: ${size}px;
                    height: ${size}px;
                    pointer-events: none;
                `;
                
                button.style.position = 'relative';
                button.style.overflow = 'hidden';
                button.appendChild(ripple);
                
                setTimeout(() => ripple.remove(), 600);
            }
        });
    }

    // Initialize capability-specific features
    initializeGovConAgent() {
        console.log('GovCon Agent initialized');
    }

    initializeOpportunityMatch() {
        console.log('Opportunity Match initialized');
    }

    initializePursuitManagement() {
        console.log('Pursuit Management initialized');
    }

    initializeDocumentHub() {
        console.log('Document Hub initialized');
    }

    initializeTeamingInsights() {
        console.log('Teaming Insights initialized');
    }
}

// Global functions for onclick handlers
function openCapability(capability) {
    platformManager.openCapability(capability);
}

function closeModal() {
    platformManager.closeModal();
}

// New functions for enhanced capabilities
function launchGovConAgent() {
    openCapability('govcon-agent');
}

function launchOpportunityMatch() {
    openCapability('opportunity-match');
}

function launchPursuitManagement() {
    openCapability('pursuit-management');
}

function launchDocumentHub() {
    openCapability('document-hub');
}

function launchTeamingInsights() {
    openCapability('teaming-insights');
}

// New Compliance Engine functions
function launchComplianceEngine() {
    openModal('complianceModal');
}

function openModal(modalId) {
    document.getElementById(modalId).style.display = 'block';
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

async function processComplianceDocuments() {
    const fileInput = document.getElementById('complianceUpload');
    const resultsDiv = document.getElementById('complianceResults');
    
    if (fileInput.files.length === 0) {
        return;
    }

    // Show processing animation
    resultsDiv.style.display = 'block';
    
    try {
        const formData = new FormData();
        for (let file of fileInput.files) {
            formData.append('files', file);
        }
        formData.append('analysis_type', 'compliance');

        const response = await fetch('/api/platform/compliance/analyze', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        console.log('Compliance analysis result:', result);
        
        // Results are already displayed in the HTML structure
        // In a real implementation, we would update with actual results
        
    } catch (error) {
        console.error('Error analyzing compliance:', error);
        resultsDiv.innerHTML = `<div class="error">Error analyzing compliance: ${error.message}</div>`;
    }
}

// New Predictive Analytics functions
function launchPredictiveAnalytics() {
    openModal('predictiveModal');
}

async function runPredictiveAnalysis() {
    const resultsDiv = document.getElementById('analyticsResults');
    
    // Show results
    resultsDiv.style.display = 'block';
    
    try {
        const response = await fetch('/api/platform/predictive/performance', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                opportunity_data: {
                    estimated_value: 5000000,
                    past_performance_match: true,
                    technical_fit_score: 85,
                    compliance_score: 87,
                    security_clearance_required: true,
                    timeline_compressed: false
                }
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        console.log('Predictive analysis result:', result);
        
        // Results are already displayed in the HTML structure
        // In a real implementation, we would update with actual predictions
        
    } catch (error) {
        console.error('Error running predictive analysis:', error);
        resultsDiv.innerHTML = `<div class="error">Error running analysis: ${error.message}</div>`;
    }
}

// Initialize when page loads
const platformManager = new PlatformManager();

// Federal RFP Processing Functions
async function processFederalRFP() {
    try {
        const fileInput = document.getElementById('pdf-file');
        const analysisType = document.querySelector('input[name="analysis-type"]:checked')?.value || 'federal_structure';
        
        if (!fileInput.files || fileInput.files.length === 0) {
            platformManager.showNotification('Please select an RFP file for federal analysis', 'error');
            return;
        }
        
        platformManager.showLoading('Analyzing federal RFP structure...');
        
        // Read file content (simplified for demo)
        const file = fileInput.files[0];
        const text = await file.text();
        
        try {
            // Use Federal AI for specialized analysis
            if (window.federalAI) {
                console.log('🏛️ Using Federal Contracting AI for analysis...');
                
                let result;
                switch (analysisType) {
                    case 'federal_structure':
                        result = await window.federalAI.analyzeFederalStructure(text);
                        break;
                    case 'compliance':
                        result = await window.federalAI.analyzeFederalStructure(text);
                        // Focus on compliance aspects
                        result.focus = 'compliance';
                        break;
                    case 'evaluation':
                        result = await window.federalAI.analyzeFederalStructure(text);
                        // Focus on evaluation criteria
                        result.focus = 'evaluation';
                        break;
                    case 'context_aware':
                        result = await window.federalAI.analyzeFederalStructure(text);
                        // Prepare for context-aware generation
                        result.focus = 'context_generation';
                        break;
                    default:
                        result = await window.federalAI.analyzeFederalStructure(text);
                }
                
                platformManager.hideLoading();
                displayFederalAnalysisResults(result);
                
                platformManager.showNotification(
                    `✅ Federal analysis completed! Structure score: ${result.structureScore}/100`,
                    'success'
                );
                
            } else {
                throw new Error('Federal AI not available');
            }
            
        } catch (federalAIError) {
            console.warn('Federal AI failed, falling back to general analysis:', federalAIError);
            
            // Fallback to browser AI or cloud processing
            if (window.browserAI && Object.values(window.browserAI.features).some(Boolean)) {
                const result = await window.browserAI.analyzeRFPContent(text, analysisType);
                platformManager.hideLoading();
                platformManager.showResults('processing-results', result);
            } else {
                platformManager.hideLoading();
                platformManager.showNotification('⚠️ AI analysis unavailable - please try again', 'error');
            }
        }
        
    } catch (error) {
        platformManager.hideLoading();
        platformManager.showNotification('❌ Federal RFP analysis failed: ' + error.message, 'error');
    }
}

async function generateFederalProposal() {
    try {
        // Check if RFP analysis has been done
        const rfpAnalysis = window.federalAI?.getSessionContext('rfpAnalysis');
        if (!rfpAnalysis) {
            platformManager.showNotification('⚠️ Please analyze the RFP first before generating proposal sections', 'warning');
            return;
        }
        
        // Prompt user for section type
        const sectionType = prompt('Enter proposal section type:\n- executiveSummary\n- technicalApproach\n- managementApproach\n- pastPerformance', 'technicalApproach');
        
        if (!sectionType) return;
        
        platformManager.showLoading('Generating context-aware proposal section...');
        
        try {
            const result = window.federalAI.generateContextAwareProposal(sectionType);
            
            platformManager.hideLoading();
            
            // Display the contextual prompt for user review
            const container = document.getElementById('processing-results');
            container.style.display = 'block';
            container.innerHTML = `
                <div class="proposal-generation-results">
                    <h4>🧠 Context-Aware Proposal Generation</h4>
                    <div class="generation-info">
                        <p><strong>Section Type:</strong> ${sectionType}</p>
                        <p><strong>Context Elements:</strong> ${result.context.requirements} requirements, ${result.context.evaluationFactors} evaluation factors, ${result.context.complianceAreas} compliance areas</p>
                        <p><strong>Session ID:</strong> ${result.metadata.sessionId}</p>
                    </div>
                    <div class="contextual-prompt">
                        <h5>Generated Contextual Prompt:</h5>
                        <div class="prompt-content">
                            <pre>${result.prompt}</pre>
                        </div>
                    </div>
                    <div class="prompt-actions">
                        <button class="btn btn-primary" onclick="copyPromptToClipboard()">📋 Copy Prompt</button>
                        <button class="btn btn-secondary" onclick="useWithBrowserAI('${sectionType}')">🤖 Generate with Browser AI</button>
                    </div>
                </div>
            `;
            
            // Store the prompt for later use
            window.currentFederalPrompt = result.prompt;
            
            platformManager.showNotification(
                `✅ Context-aware prompt generated for ${sectionType}! Ready for AI generation.`,
                'success'
            );
            
        } catch (error) {
            platformManager.hideLoading();
            platformManager.showNotification('❌ Proposal generation failed: ' + error.message, 'error');
        }
        
    } catch (error) {
        platformManager.hideLoading();
        platformManager.showNotification('❌ Error in proposal generation: ' + error.message, 'error');
    }
}

async function validateFederalCompliance() {
    try {
        // Get sample proposal content or prompt user
        const proposalContent = prompt('Paste proposal content to validate compliance:', 'Sample proposal text for compliance validation...');
        
        if (!proposalContent || proposalContent.trim() === '') {
            platformManager.showNotification('Please provide proposal content for validation', 'warning');
            return;
        }
        
        platformManager.showLoading('Validating federal compliance...');
        
        try {
            const validation = await window.federalAI.validateCompliance(proposalContent, 'general');
            
            platformManager.hideLoading();
            displayComplianceValidation(validation);
            
            platformManager.showNotification(
                `✅ Compliance validation completed! Score: ${validation.overallScore.toFixed(1)}%`,
                validation.overallScore >= 80 ? 'success' : 'warning'
            );
            
        } catch (error) {
            platformManager.hideLoading();
            platformManager.showNotification('❌ Compliance validation failed: ' + error.message, 'error');
        }
        
    } catch (error) {
        platformManager.hideLoading();
        platformManager.showNotification('❌ Error in compliance validation: ' + error.message, 'error');
    }
}

function displayFederalAnalysisResults(analysis) {
    const container = document.getElementById('processing-results');
    container.style.display = 'block';
    
    const content = container.querySelector('#results-content');
    if (content) {
        content.innerHTML = window.federalAI.displayComprehensiveAnalysis(analysis);
    }
}

function displayComplianceValidation(validation) {
    const container = document.getElementById('processing-results');
    container.style.display = 'block';
    
    const content = container.querySelector('#results-content');
    if (content) {
        content.innerHTML = `
            <div class="compliance-validation-results">
                <div class="validation-header">
                    <h3>✅ Federal Compliance Validation</h3>
                    <div class="compliance-score">
                        <span class="score-value ${validation.overallScore >= 80 ? 'high' : validation.overallScore >= 60 ? 'medium' : 'low'}">${validation.overallScore.toFixed(1)}%</span>
                        <span class="score-label">Compliance Score</span>
                    </div>
                </div>
                
                <div class="validation-sections">
                    <div class="requirements-coverage">
                        <h4>📋 Requirements Coverage</h4>
                        ${Object.entries(validation.requirementsCoverage).slice(0, 10).map(([id, req]) => `
                            <div class="coverage-item ${req.status}">
                                <span class="req-id">${id}</span>
                                <span class="req-text">${req.requirement.substring(0, 80)}...</span>
                                <span class="coverage-score">${req.coverage.toFixed(0)}%</span>
                                <span class="status-badge ${req.status}">${req.status.toUpperCase()}</span>
                            </div>
                        `).join('')}
                    </div>
                    
                    ${validation.missingRequirements.length > 0 ? `
                        <div class="missing-requirements">
                            <h4>⚠️ Missing Requirements (${validation.missingRequirements.length})</h4>
                            ${validation.missingRequirements.map(req => `
                                <div class="missing-item">
                                    <span class="requirement">${req.requirement}</span>
                                    <span class="risk-level ${req.risk}">${req.risk.toUpperCase()}</span>
                                    <div class="recommendation">${req.recommendation}</div>
                                </div>
                            `).join('')}
                        </div>
                    ` : ''}
                    
                    <div class="federal-language-check">
                        <h4>📝 Federal Language Validation</h4>
                        <div class="language-metrics">
                            <div class="metric">
                                <span class="label">Informal Language Issues:</span>
                                <span class="value ${validation.federalLanguageCheck.informalLanguage > 0 ? 'warning' : 'good'}">${validation.federalLanguageCheck.informalLanguage}</span>
                            </div>
                            <div class="metric">
                                <span class="label">Federal Tone Score:</span>
                                <span class="value">${validation.federalLanguageCheck.toneScore}/100</span>
                            </div>
                        </div>
                    </div>
                    
                    ${validation.recommendations.length > 0 ? `
                        <div class="recommendations">
                            <h4>💡 Recommendations</h4>
                            ${validation.recommendations.map(rec => `
                                <div class="recommendation-item">
                                    <span class="recommendation-text">${rec}</span>
                                </div>
                            `).join('')}
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }
}

function copyPromptToClipboard() {
    if (window.currentFederalPrompt) {
        navigator.clipboard.writeText(window.currentFederalPrompt).then(() => {
            platformManager.showNotification('📋 Prompt copied to clipboard!', 'success');
        }).catch(err => {
            console.error('Failed to copy prompt:', err);
            platformManager.showNotification('❌ Failed to copy prompt', 'error');
        });
    }
}

async function useWithBrowserAI(sectionType) {
    if (window.currentFederalPrompt && window.browserAI && window.browserAI.features.writer) {
        try {
            platformManager.showLoading('Generating with Browser AI...');
            
            const result = await window.browserAI.generateProposalContent(
                window.currentFederalPrompt, 
                sectionType
            );
            
            platformManager.hideLoading();
            
            // Display the generated content
            const container = document.getElementById('processing-results');
            const existingContent = container.innerHTML;
            container.innerHTML = existingContent + `
                <div class="generated-content">
                    <h4>🤖 Generated Content (Browser AI)</h4>
                    <div class="content-preview">
                        <pre>${result.content}</pre>
                    </div>
                    <div class="generation-meta">
                        <p><strong>Processing Time:</strong> ${result.processing_time}</p>
                        <p><strong>Method:</strong> ${result.method}</p>
                        <p><strong>Privacy:</strong> ${result.privacy_note}</p>
                    </div>
                </div>
            `;
            
            platformManager.showNotification('✅ Content generated with Browser AI!', 'success');
            
        } catch (error) {
            platformManager.hideLoading();
            platformManager.showNotification('❌ Browser AI generation failed: ' + error.message, 'error');
        }
    } else {
        platformManager.showNotification('⚠️ Browser AI not available for content generation', 'warning');
    }
}

// Add enhanced button effects when page loads
document.addEventListener('DOMContentLoaded', () => {
    platformManager.addButtonEffects();
    
    // Add CSS for ripple animation
    const style = document.createElement('style');
    style.textContent = `
        @keyframes ripple {
            to {
                transform: scale(4);
                opacity: 0;
            }
        }
        
        @keyframes slideOutRight {
            from {
                opacity: 1;
                transform: translateX(0);
            }
            to {
                opacity: 0;
                transform: translateX(100%);
            }
        }
        
        .result-score.high-score {
            background: linear-gradient(135deg, #10b981, #059669);
        }
        
        .result-score.medium-score {
            background: linear-gradient(135deg, #f59e0b, #d97706);
        }
        
        .result-score.low-score {
            background: linear-gradient(135deg, #ef4444, #dc2626);
        }
    `;
    document.head.appendChild(style);
});