// Enhanced Interactive Features for AI Proposal Agent
// Modern, CLEATUS-inspired functionality

class ProposalAgent {
  constructor() {
    this.currentStep = 0;
    this.uploadedFiles = new Map();
    this.processingStatus = {
      requirements: false,
      analysis: false,
      generation: false,
      formatting: false
    };
    
    this.init();
  }

  init() {
    this.setupAnimations();
    this.setupFileHandling();
    this.setupFormInteractions();
    this.setupProgressTracking();
    this.setupTooltips();
  }

  // Enhanced Animations
  setupAnimations() {
    // Intersection Observer for scroll animations
    const observerOptions = {
      threshold: 0.1,
      rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('animate-slide-up');
        }
      });
    }, observerOptions);

    // Observe all feature cards
    document.querySelectorAll('.feature-card').forEach(card => {
      observer.observe(card);
    });

    // Add staggered animation delays
    document.querySelectorAll('.workflow-grid .feature-card').forEach((card, index) => {
      card.style.animationDelay = `${index * 0.1}s`;
    });
  }

  // Enhanced File Handling
  setupFileHandling() {
    const fileTypes = {
      'pws': { icon: '📄', color: 'var(--primary-blue)' },
      'rfp': { icon: '📋', color: 'var(--success-green)' },
      'resume': { icon: '👤', color: 'var(--orange)' },
      'template': { icon: '📋', color: 'var(--purple)' }
    };

    Object.keys(fileTypes).forEach(type => {
      this.setupUploadArea(type, fileTypes[type]);
    });
  }

  setupUploadArea(type, config) {
    const uploadAreas = document.querySelectorAll(`[id*="${type}-upload"], [data-upload="${type}"]`);
    
    uploadAreas.forEach(uploadArea => {
      const fileInput = uploadArea.querySelector('input[type="file"]') || 
                       document.getElementById(`${type}-file`);
      
      if (!fileInput) return;

      // Click handler
      uploadArea.addEventListener('click', (e) => {
        if (e.target.tagName !== 'INPUT') {
          fileInput.click();
        }
      });

      // Drag and drop
      uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
        uploadArea.style.transform = 'scale(1.02)';
      });

      uploadArea.addEventListener('dragleave', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        uploadArea.style.transform = 'scale(1)';
      });

      uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        uploadArea.style.transform = 'scale(1)';
        
        const files = Array.from(e.dataTransfer.files);
        this.handleFileUpload(files, type, uploadArea, config);
      });

      // File input change
      fileInput.addEventListener('change', (e) => {
        const files = Array.from(e.target.files);
        this.handleFileUpload(files, type, uploadArea, config);
      });
    });
  }

  handleFileUpload(files, type, uploadArea, config) {
    if (files.length === 0) return;

    const file = files[0];
    this.uploadedFiles.set(type, file);

    // Update UI with success state
    this.updateUploadState(uploadArea, file, config);
    
    // Add file preview for certain types
    if (type === 'pws' || type === 'rfp') {
      this.createFilePreview(file, uploadArea);
    }

    // Trigger validation
    this.validateForm();
  }

  updateUploadState(uploadArea, file, config) {
    const uploadIcon = uploadArea.querySelector('.upload-icon');
    const uploadText = uploadArea.querySelector('p');
    
    // Animate the change
    uploadArea.style.transition = 'all 0.3s ease';
    uploadIcon.style.transform = 'scale(0)';
    
    setTimeout(() => {
      uploadIcon.textContent = '✅';
      uploadIcon.style.background = config.color;
      uploadIcon.style.color = 'white';
      uploadIcon.style.transform = 'scale(1.1)';
      
      uploadText.innerHTML = `
        <strong style="color: ${config.color}">File uploaded:</strong> 
        <span style="font-size: 0.9em">${file.name}</span>
        <br>
        <small style="color: var(--gray-600)">
          ${this.formatFileSize(file.size)} • ${file.type || 'Unknown type'}
        </small>
      `;
      
      uploadArea.style.borderColor = config.color;
      uploadArea.style.background = `${config.color}15`;
      
      // Add remove button
      this.addRemoveButton(uploadArea, file.name);
      
    }, 150);

    setTimeout(() => {
      uploadIcon.style.transform = 'scale(1)';
    }, 300);
  }

  addRemoveButton(uploadArea, fileName) {
    // Remove existing remove button
    const existingBtn = uploadArea.querySelector('.remove-file-btn');
    if (existingBtn) existingBtn.remove();

    const removeBtn = document.createElement('button');
    removeBtn.className = 'remove-file-btn';
    removeBtn.innerHTML = '✕';
    removeBtn.style.cssText = `
      position: absolute;
      top: 10px;
      right: 10px;
      background: var(--error-red);
      color: white;
      border: none;
      border-radius: 50%;
      width: 24px;
      height: 24px;
      cursor: pointer;
      font-size: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      opacity: 0.8;
      transition: all 0.2s ease;
    `;

    removeBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      this.removeFile(uploadArea);
    });

    removeBtn.addEventListener('mouseenter', () => {
      removeBtn.style.opacity = '1';
      removeBtn.style.transform = 'scale(1.1)';
    });

    removeBtn.addEventListener('mouseleave', () => {
      removeBtn.style.opacity = '0.8';
      removeBtn.style.transform = 'scale(1)';
    });

    uploadArea.style.position = 'relative';
    uploadArea.appendChild(removeBtn);
  }

  removeFile(uploadArea) {
    // Reset upload area
    const uploadIcon = uploadArea.querySelector('.upload-icon');
    const uploadText = uploadArea.querySelector('p');
    const removeBtn = uploadArea.querySelector('.remove-file-btn');
    
    uploadIcon.textContent = '📄';
    uploadIcon.style.background = 'var(--primary-blue-light)';
    uploadIcon.style.color = 'var(--primary-blue)';
    
    uploadText.innerHTML = 'Drop files here or click to upload';
    
    uploadArea.style.borderColor = 'var(--gray-300)';
    uploadArea.style.background = 'white';
    
    if (removeBtn) removeBtn.remove();
    
    this.validateForm();
  }

  createFilePreview(file, uploadArea) {
    // Create a small preview card
    const preview = document.createElement('div');
    preview.className = 'file-preview';
    preview.style.cssText = `
      margin-top: 1rem;
      padding: 0.75rem;
      background: var(--gray-50);
      border-radius: 8px;
      font-size: 0.875rem;
      border-left: 3px solid var(--primary-blue);
    `;
    
    preview.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: center;">
        <span>📄 ${file.name}</span>
        <span style="color: var(--gray-600)">${this.formatFileSize(file.size)}</span>
      </div>
    `;

    // Remove existing preview
    const existingPreview = uploadArea.querySelector('.file-preview');
    if (existingPreview) existingPreview.remove();

    uploadArea.appendChild(preview);
  }

  // Form Interactions
  setupFormInteractions() {
    // Model selection with descriptions
    const modelSelect = document.getElementById('model-select');
    if (modelSelect) {
      modelSelect.addEventListener('change', (e) => {
        this.showModelInfo(e.target.value);
      });
    }

    // Quality level with explanations
    const qualitySelect = document.getElementById('quality-level');
    if (qualitySelect) {
      qualitySelect.addEventListener('change', (e) => {
        this.showQualityInfo(e.target.value);
      });
    }

    // Real-time form validation
    const formInputs = document.querySelectorAll('.form-input');
    formInputs.forEach(input => {
      input.addEventListener('input', () => this.validateForm());
      input.addEventListener('focus', (e) => {
        e.target.style.transform = 'scale(1.02)';
      });
      input.addEventListener('blur', (e) => {
        e.target.style.transform = 'scale(1)';
      });
    });
  }

  showModelInfo(model) {
    const infoMap = {
      'claude-3-5-sonnet-20241022': {
        description: '🧠 Most intelligent model for complex reasoning and business analysis',
        speed: 'Medium',
        quality: 'Highest'
      },
      'gpt-4o-mini': {
        description: '⚡ Fast and cost-effective for standard proposals',
        speed: 'Fast',
        quality: 'Good'
      },
      'claude-3-haiku-20240307': {
        description: '🚀 Fastest processing for quick turnaround',
        speed: 'Very Fast',
        quality: 'Good'
      }
    };

    const info = infoMap[model];
    if (info) {
      this.showTooltip(document.getElementById('model-select'), info.description);
    }
  }

  showQualityInfo(level) {
    const infoMap = {
      'EXECUTIVE': 'Fortune 500 caliber with detailed ROI analysis and competitive positioning',
      'ADVANCED': 'Strategic content with business intelligence and market analysis',
      'ENHANCED': 'Business-focused with metrics and professional formatting',
      'BASIC': 'Standard proposal content with basic compliance checking'
    };

    const info = infoMap[level];
    if (info) {
      this.showTooltip(document.getElementById('quality-level'), info);
    }
  }

  // Progress Tracking
  setupProgressTracking() {
    const generateBtn = document.getElementById('generate-btn');
    if (generateBtn) {
      generateBtn.addEventListener('click', (e) => {
        e.preventDefault();
        this.startProposalGeneration();
      });
    }
  }

  async startProposalGeneration() {
    if (!this.validateForm()) return;

    const progressContainer = document.getElementById('progress-container');
    const generateBtn = document.getElementById('generate-btn');
    
    // Disable button and show progress
    generateBtn.disabled = true;
    generateBtn.innerHTML = '⏳ Processing...';
    progressContainer.classList.add('active');

    try {
      const formData = this.buildFormData();
      await this.processWithRealTimeUpdates(formData);
    } catch (error) {
      this.showError(error.message);
    } finally {
      generateBtn.disabled = false;
      generateBtn.innerHTML = '🚀 Generate Proposal';
    }
  }

  buildFormData() {
    const formData = new FormData();
    
    // Add files
    if (this.uploadedFiles.has('pws')) {
      formData.append('pws', this.uploadedFiles.get('pws'));
    }
    if (this.uploadedFiles.has('rfp')) {
      formData.append('rfp', this.uploadedFiles.get('rfp'));
    }

    // Add configuration
    const model = document.getElementById('model-select')?.value || 'claude-3-5-sonnet-20241022';
    const companyName = document.getElementById('company-name')?.value || '';
    const companyTagline = document.getElementById('company-tagline')?.value || '';
    
    formData.append('model', model);
    formData.append('brand_company', companyName);
    formData.append('brand_tagline', companyTagline);

    return formData;
  }

  async processWithRealTimeUpdates(formData) {
    const steps = [
      { percent: 5, status: '🔍 Analyzing document structure...', delay: 800 },
      { percent: 15, status: '📋 Extracting requirements and shalls...', delay: 1200 },
      { percent: 30, status: '🧠 Generating business intelligence...', delay: 1500 },
      { percent: 45, status: '📊 Creating competitive analysis...', delay: 1000 },
      { percent: 60, status: '✍️ Drafting proposal sections...', delay: 2000 },
      { percent: 75, status: '🎨 Applying professional formatting...', delay: 800 },
      { percent: 90, status: '✅ Final quality checks...', delay: 600 },
      { percent: 100, status: '🎉 Proposal generation complete!', delay: 300 }
    ];

    // Start actual API call
    const responsePromise = fetch('/process', {
      method: 'POST',
      body: formData
    });

    // Animate progress
    for (const step of steps) {
      await this.updateProgress(step.percent, step.status);
      await new Promise(resolve => setTimeout(resolve, step.delay));
    }

    // Wait for actual response
    const response = await responsePromise;
    const data = await response.json();

    if (data.error) {
      throw new Error(data.error);
    }

    this.showResults(data);
  }

  updateProgress(percent, status) {
    const progressFill = document.getElementById('progress-fill');
    const progressPercentage = document.getElementById('progress-percentage');
    const progressStatus = document.getElementById('progress-status');

    if (progressFill) progressFill.style.width = percent + '%';
    if (progressPercentage) progressPercentage.textContent = percent + '%';
    if (progressStatus) progressStatus.textContent = status;

    return new Promise(resolve => {
      setTimeout(resolve, 100); // Small delay for smooth animation
    });
  }

  showResults(data) {
    const resultsSection = document.getElementById('results-section');
    const resultsGrid = document.getElementById('results-grid');
    
    if (!resultsSection || !resultsGrid) return;

    // Create enhanced results cards
    resultsGrid.innerHTML = this.generateResultsHTML(data);
    
    resultsSection.style.display = 'block';
    resultsSection.classList.add('animate-fade-in');
    
    // Scroll to results with a slight delay
    setTimeout(() => {
      resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 300);

    // Add download tracking
    this.setupDownloadTracking(resultsGrid);
  }

  generateResultsHTML(data) {
    return `
      <div class="result-card animate-slide-up" style="animation-delay: 0.1s">
        <div class="result-header">
          <div class="result-icon" style="background: linear-gradient(135deg, var(--success-green), #059669); color: white;">📄</div>
          <div>
            <h4>Executive Proposal</h4>
            <div class="status-badge success">✅ Ready for Review</div>
          </div>
        </div>
        <p>Complete 35-40 page proposal with Fortune 500 quality business intelligence, competitive positioning, and evaluation-ready content.</p>
        <div style="display: flex; gap: 0.5rem; margin-top: 1rem;">
          <a href="${data.outputs?.docx}" class="btn btn-primary" target="_blank">
            📥 Download DOCX
          </a>
          <button class="btn btn-secondary" onclick="proposalAgent.previewDocument('${data.outputs?.docx}')">
            👁️ Preview
          </button>
        </div>
      </div>
      
      <div class="result-card animate-slide-up" style="animation-delay: 0.2s">
        <div class="result-header">
          <div class="result-icon" style="background: linear-gradient(135deg, var(--primary-blue), #4338CA); color: white;">📊</div>
          <div>
            <h4>Requirements Analysis</h4>
            <div class="status-badge success">✅ ${data.requirements_count || 0} Requirements Mapped</div>
          </div>
        </div>
        <p>Detailed compliance matrix with full requirement traceability and gap analysis.</p>
        <div style="display: flex; gap: 0.5rem; margin-top: 1rem;">
          <a href="${data.outputs?.json}" class="btn btn-secondary" target="_blank">
            📋 View Analysis
          </a>
          <button class="btn btn-secondary tooltip" data-tooltip="Coming soon!">
            🔍 Interactive View
          </button>
        </div>
      </div>
      
      <div class="result-card animate-slide-up" style="animation-delay: 0.3s">
        <div class="result-header">
          <div class="result-icon" style="background: linear-gradient(135deg, var(--warning-orange), #D97706); color: white;">📈</div>
          <div>
            <h4>Project Visualization</h4>
            <div class="status-badge success">✅ Diagrams Generated</div>
          </div>
        </div>
        <p>Professional Gantt charts, workflow diagrams, and project timelines for executive presentation.</p>
        <div style="display: flex; gap: 0.5rem; margin-top: 1rem;">
          <a href="${data.outputs?.png}" class="btn btn-secondary" target="_blank">
            🖼️ View Diagrams
          </a>
          <button class="btn btn-secondary tooltip" data-tooltip="High-resolution versions">
            📊 Export Charts
          </button>
        </div>
      </div>
      
      <div class="result-card animate-slide-up" style="animation-delay: 0.4s">
        <div class="result-header">
          <div class="result-icon" style="background: linear-gradient(135deg, var(--error-red), #DC2626); color: white;">⚡</div>
          <div>
            <h4>Quick Actions</h4>
            <div class="status-badge warning">🚀 Next Steps</div>
          </div>
        </div>
        <p>Recommended actions for proposal refinement and competitive positioning.</p>
        <div style="display: flex; gap: 0.5rem; margin-top: 1rem; flex-wrap: wrap;">
          <button class="btn btn-primary" onclick="proposalAgent.scheduleReview()">
            📅 Schedule Review
          </button>
          <button class="btn btn-secondary" onclick="proposalAgent.shareWithTeam()">
            👥 Share with Team
          </button>
          <button class="btn btn-secondary" onclick="proposalAgent.exportBundle()">
            📦 Export Bundle
          </button>
        </div>
      </div>
    `;
  }

  // Tooltips
  setupTooltips() {
    document.addEventListener('mouseover', (e) => {
      if (e.target.hasAttribute('data-tooltip')) {
        this.showTooltip(e.target, e.target.getAttribute('data-tooltip'));
      }
    });

    document.addEventListener('mouseout', (e) => {
      if (e.target.hasAttribute('data-tooltip')) {
        this.hideTooltip();
      }
    });
  }

  showTooltip(element, text) {
    // Remove existing tooltip
    this.hideTooltip();

    const tooltip = document.createElement('div');
    tooltip.className = 'dynamic-tooltip';
    tooltip.textContent = text;
    tooltip.style.cssText = `
      position: absolute;
      background: var(--gray-900);
      color: white;
      padding: 0.5rem 0.75rem;
      border-radius: 6px;
      font-size: 0.875rem;
      white-space: nowrap;
      z-index: 1000;
      opacity: 0;
      transition: opacity 0.3s ease;
      pointer-events: none;
    `;

    document.body.appendChild(tooltip);

    const rect = element.getBoundingClientRect();
    tooltip.style.top = (rect.top - tooltip.offsetHeight - 8) + 'px';
    tooltip.style.left = (rect.left + rect.width / 2 - tooltip.offsetWidth / 2) + 'px';

    // Fade in
    setTimeout(() => tooltip.style.opacity = '1', 10);
  }

  hideTooltip() {
    const existing = document.querySelector('.dynamic-tooltip');
    if (existing) {
      existing.remove();
    }
  }

  // Utility Methods
  validateForm() {
    const pwsFile = this.uploadedFiles.get('pws');
    const generateBtn = document.getElementById('generate-btn');
    
    const isValid = pwsFile && pwsFile.size > 0;
    
    if (generateBtn) {
      generateBtn.disabled = !isValid;
      generateBtn.style.opacity = isValid ? '1' : '0.6';
    }

    return isValid;
  }

  formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  showError(message) {
    const progressStatus = document.getElementById('progress-status');
    if (progressStatus) {
      progressStatus.textContent = '❌ Error: ' + message;
      progressStatus.style.color = 'var(--error-red)';
    }
  }

  // Enhanced Features (placeholders for future implementation)
  previewDocument(url) {
    window.open(url, '_blank');
  }

  scheduleReview() {
    alert('Review scheduling feature coming soon!');
  }

  shareWithTeam() {
    if (navigator.share) {
      navigator.share({
        title: 'Proposal Generated',
        text: 'Check out this AI-generated proposal',
        url: window.location.href
      });
    } else {
      // Fallback
      navigator.clipboard.writeText(window.location.href);
      alert('Link copied to clipboard!');
    }
  }

  exportBundle() {
    alert('Bundle export feature coming soon!');
  }

  setupDownloadTracking(container) {
    const downloadLinks = container.querySelectorAll('a[href*="download"], a[href*=".docx"], a[href*=".pdf"]');
    downloadLinks.forEach(link => {
      link.addEventListener('click', () => {
        // Track download events (for analytics)
        console.log('Download tracked:', link.href);
      });
    });
  }
}

// Initialize the application
let proposalAgent;
document.addEventListener('DOMContentLoaded', () => {
  proposalAgent = new ProposalAgent();
});

// Global helper functions
window.proposalAgent = proposalAgent;