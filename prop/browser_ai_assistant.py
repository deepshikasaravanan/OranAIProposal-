"""
Browser AI Writing Assistant
Integrates with Web Machine Learning Writing Assistance APIs for local AI processing
"""

from typing import Dict, List, Optional, Any
import json
import logging

logger = logging.getLogger(__name__)

class BrowserAIAssistant:
    """
    Manages integration with browser-native Writing Assistance APIs
    Provides local AI capabilities for government proposal writing
    """
    
    def __init__(self):
        self.capabilities = {
            "summarizer": {
                "types": ["headline", "key-points", "teaser", "tl;dr"],
                "use_cases": [
                    "RFP requirement extraction",
                    "Section summarization", 
                    "Executive summary generation",
                    "Compliance point identification"
                ]
            },
            "writer": {
                "tones": ["formal", "casual", "professional"],
                "use_cases": [
                    "Technical approach sections",
                    "Management approach content",
                    "Past performance narratives",
                    "Executive summaries"
                ]
            },
            "rewriter": {
                "styles": ["formal", "shorter", "longer", "simpler"],
                "use_cases": [
                    "Compliance tone adjustment",
                    "Section 508 language",
                    "Government style formatting",
                    "Clarity improvements"
                ]
            }
        }
    
    def get_rfp_analysis_config(self) -> Dict[str, Any]:
        """Configuration for RFP document analysis"""
        return {
            "summarizer_config": {
                "type": "key-points",
                "sharedContext": "Government RFP document requiring detailed analysis for proposal response",
                "expectedInputLanguages": ["en"],
                "outputLanguage": "en"
            },
            "context_templates": {
                "requirements": "Extract specific requirements, deliverables, and compliance needs",
                "deadlines": "Identify all submission deadlines, milestone dates, and timeline requirements", 
                "evaluation": "Summarize evaluation criteria, scoring factors, and award methodology",
                "compliance": "Extract compliance requirements including Section 508, security, and regulatory needs"
            }
        }
    
    def get_proposal_writing_config(self, section_type: str) -> Dict[str, Any]:
        """Configuration for proposal section generation"""
        configs = {
            "technical_approach": {
                "tone": "formal",
                "sharedContext": "Technical approach section for government contract proposal",
                "style": "detailed and comprehensive"
            },
            "management_approach": {
                "tone": "professional", 
                "sharedContext": "Management approach demonstrating project leadership and organization",
                "style": "structured and authoritative"
            },
            "past_performance": {
                "tone": "formal",
                "sharedContext": "Past performance narrative highlighting relevant contract experience",
                "style": "results-focused and quantified"
            },
            "executive_summary": {
                "tone": "formal",
                "sharedContext": "Executive summary for government proposal highlighting key differentiators",
                "style": "concise and compelling"
            }
        }
        return configs.get(section_type, configs["technical_approach"])
    
    def get_compliance_rewriting_config(self) -> Dict[str, Any]:
        """Configuration for compliance and style improvements"""
        return {
            "government_tone": {
                "sharedContext": "Government proposal requiring formal business tone and compliance language",
                "target_style": "formal",
                "requirements": [
                    "Use formal government contracting language",
                    "Ensure Section 508 compliance terminology",
                    "Remove informal expressions",
                    "Maintain professional tone throughout"
                ]
            },
            "section_508": {
                "sharedContext": "Content requiring Section 508 accessibility compliance",
                "target_style": "accessible",
                "requirements": [
                    "Use clear, simple language",
                    "Ensure accessibility terminology",
                    "Include accommodation language",
                    "Follow federal accessibility guidelines"
                ]
            },
            "clarity": {
                "sharedContext": "Technical content requiring improved clarity for government evaluators",
                "target_style": "simpler",
                "requirements": [
                    "Simplify complex technical terms",
                    "Improve readability",
                    "Maintain technical accuracy",
                    "Enhance logical flow"
                ]
            }
        }
    
    def generate_api_integration_code(self, api_type: str, config: Dict[str, Any]) -> str:
        """Generate JavaScript code for browser API integration"""
        
        if api_type == "summarizer":
            return f"""
// RFP Analysis with Browser AI
async function analyzeRFPWithBrowserAI(rfpContent, analysisType = 'requirements') {{
    try {{
        // Check if Summarizer API is available
        const availability = await Summarizer.availability({{
            type: "{config.get('type', 'key-points')}",
            expectedInputLanguages: {json.dumps(config.get('expectedInputLanguages', ['en']))},
            outputLanguage: "{config.get('outputLanguage', 'en')}"
        }});
        
        if (availability === 'unavailable') {{
            throw new Error('Browser AI Summarizer not available');
        }}
        
        if (availability === 'downloadable') {{
            showNotification('Downloading AI model for local processing...', 'info');
        }}
        
        const summarizer = await Summarizer.create({{
            type: "{config.get('type', 'key-points')}",
            sharedContext: "{config.get('sharedContext', '')}",
            expectedInputLanguages: {json.dumps(config.get('expectedInputLanguages', ['en']))},
            outputLanguage: "{config.get('outputLanguage', 'en')}",
            monitor(m) {{
                m.addEventListener("downloadprogress", e => {{
                    console.log(`AI model download: ${{(e.loaded * 100).toFixed(1)}}%`);
                }});
            }}
        }});
        
        const contextTemplates = {json.dumps(config.get('context_templates', {}))};
        const context = contextTemplates[analysisType] || contextTemplates.requirements;
        
        const summary = await summarizer.summarize(rfpContent, {{
            context: context
        }});
        
        return {{
            success: true,
            analysis: summary,
            processingTime: 'Local AI processing',
            privacy: 'Data processed locally - never sent to cloud'
        }};
        
    }} catch (error) {{
        console.error('Browser AI analysis failed:', error);
        return {{
            success: false,
            error: error.message,
            fallback: 'Using cloud-based analysis as fallback'
        }};
    }}
}}
"""
        
        elif api_type == "writer":
            return f"""
// Proposal Writing with Browser AI  
async function generateProposalContent(prompt, sectionType = 'technical_approach') {{
    try {{
        const config = {json.dumps(config)};
        
        const availability = await Writer.availability({{
            tone: config.tone,
            expectedOutputLanguage: "en"
        }});
        
        if (availability === 'unavailable') {{
            throw new Error('Browser AI Writer not available');
        }}
        
        const writer = await Writer.create({{
            tone: config.tone,
            sharedContext: config.sharedContext,
            expectedOutputLanguage: "en"
        }});
        
        const content = await writer.write(prompt);
        
        return {{
            success: true,
            content: content,
            section_type: sectionType,
            processing: 'Generated locally with browser AI',
            privacy: 'No data sent to external servers'
        }};
        
    }} catch (error) {{
        console.error('Browser AI writing failed:', error);
        return {{
            success: false,
            error: error.message,
            fallback: 'Using cloud-based generation as fallback'
        }};
    }}
}}

// Streaming proposal generation
async function generateProposalContentStreaming(prompt, outputElement) {{
    try {{
        const writer = await Writer.create({{
            tone: "formal",
            sharedContext: "Government proposal section requiring detailed technical content"
        }});
        
        const stream = writer.writeStreaming(prompt);
        
        for await (const chunk of stream) {{
            outputElement.textContent += chunk;
        }}
        
    }} catch (error) {{
        console.error('Streaming generation failed:', error);
    }}
}}
"""
        
        elif api_type == "rewriter":
            return f"""
// Compliance & Style Enhancement with Browser AI
async function enhanceComplianceWithBrowserAI(content, enhancementType = 'government_tone') {{
    try {{
        const config = {json.dumps(config)};
        const enhancement = config[enhancementType];
        
        const availability = await Rewriter.availability({{
            expectedInputLanguages: ["en"],
            outputLanguage: "en"
        }});
        
        if (availability === 'unavailable') {{
            throw new Error('Browser AI Rewriter not available');
        }}
        
        const rewriter = await Rewriter.create({{
            sharedContext: enhancement.sharedContext,
            expectedInputLanguages: ["en"],
            outputLanguage: "en"
        }});
        
        const context = `Style: ${{enhancement.target_style}}. Requirements: ${{enhancement.requirements.join(', ')}}`;
        
        const improvedContent = await rewriter.rewrite(content, {{
            context: context
        }});
        
        return {{
            success: true,
            original_content: content,
            improved_content: improvedContent,
            enhancement_type: enhancementType,
            processing: 'Enhanced locally with browser AI',
            privacy: 'Sensitive content processed locally only'
        }};
        
    }} catch (error) {{
        console.error('Browser AI enhancement failed:', error);
        return {{
            success: false,
            error: error.message,
            fallback: 'Using cloud-based enhancement as fallback'
        }};
    }}
}}
"""
    
    def get_feature_detection_code(self) -> str:
        """Generate code to detect browser AI capabilities"""
        return """
// Browser AI Feature Detection
class BrowserAIDetector {
    static async checkAvailability() {
        const features = {
            summarizer: false,
            writer: false, 
            rewriter: false
        };
        
        try {
            // Check Summarizer API
            if (typeof Summarizer !== 'undefined') {
                const summarizerAvailability = await Summarizer.availability({
                    type: "key-points",
                    expectedInputLanguages: ["en"]
                });
                features.summarizer = summarizerAvailability !== 'unavailable';
            }
            
            // Check Writer API
            if (typeof Writer !== 'undefined') {
                const writerAvailability = await Writer.availability({
                    tone: "formal",
                    expectedOutputLanguage: "en"
                });
                features.writer = writerAvailability !== 'unavailable';
            }
            
            // Check Rewriter API
            if (typeof Rewriter !== 'undefined') {
                const rewriterAvailability = await Rewriter.availability({
                    expectedInputLanguages: ["en"],
                    outputLanguage: "en"
                });
                features.rewriter = rewriterAvailability !== 'unavailable';
            }
            
        } catch (error) {
            console.warn('Browser AI detection failed:', error);
        }
        
        return features;
    }
    
    static async showCapabilityStatus() {
        const features = await this.checkAvailability();
        const totalFeatures = Object.keys(features).length;
        const availableFeatures = Object.values(features).filter(Boolean).length;
        
        console.log('🤖 Browser AI Capabilities:');
        console.log(`✅ Summarizer API: ${features.summarizer ? 'Available' : 'Not Available'}`);
        console.log(`✅ Writer API: ${features.writer ? 'Available' : 'Not Available'}`);
        console.log(`✅ Rewriter API: ${features.rewriter ? 'Available' : 'Not Available'}`);
        console.log(`🎯 Overall: ${availableFeatures}/${totalFeatures} APIs available`);
        
        return features;
    }
}
"""
    
    def get_integration_benefits(self) -> Dict[str, List[str]]:
        """List of benefits from browser AI integration"""
        return {
            "privacy_security": [
                "Local processing - no government data sent to cloud APIs",
                "Meets federal data protection requirements",
                "End-to-end encryption compatible",
                "No API keys or external authentication needed"
            ],
            "performance": [
                "No network latency - instant AI responses", 
                "Offline capability for secure environments",
                "No rate limiting or API costs",
                "Faster iteration on proposal development"
            ],
            "compliance": [
                "FedRAMP compliance through local processing",
                "Section 508 accessibility enhancements",
                "Government tone and style consistency",
                "Automatic compliance language integration"
            ],
            "cost_efficiency": [
                "Eliminates cloud AI API costs",
                "Unlimited usage without quotas",
                "Reduces infrastructure dependencies",
                "Lower total cost of ownership"
            ]
        }
    
    def generate_implementation_roadmap(self) -> Dict[str, Any]:
        """Implementation roadmap for browser AI integration"""
        return {
            "phase_1_detection": {
                "timeline": "Week 1",
                "tasks": [
                    "Add browser AI capability detection",
                    "Create fallback mechanisms for unsupported browsers",
                    "Implement graceful degradation to cloud APIs",
                    "Add user notifications for AI availability"
                ]
            },
            "phase_2_summarization": {
                "timeline": "Week 2-3", 
                "tasks": [
                    "Integrate Summarizer API for RFP analysis",
                    "Add context-aware requirement extraction",
                    "Implement multi-language support",
                    "Create custom summarization templates"
                ]
            },
            "phase_3_generation": {
                "timeline": "Week 4-5",
                "tasks": [
                    "Integrate Writer API for proposal sections",
                    "Add streaming content generation",
                    "Implement section-specific writing configs",
                    "Create proposal template integration"
                ]
            },
            "phase_4_enhancement": {
                "timeline": "Week 6",
                "tasks": [
                    "Integrate Rewriter API for compliance",
                    "Add government tone standardization", 
                    "Implement Section 508 language enhancement",
                    "Create style consistency checking"
                ]
            },
            "phase_5_optimization": {
                "timeline": "Week 7-8",
                "tasks": [
                    "Optimize model downloading and caching",
                    "Add progress indicators for model downloads",
                    "Implement hybrid cloud/local AI strategies",
                    "Create performance monitoring"
                ]
            }
        }