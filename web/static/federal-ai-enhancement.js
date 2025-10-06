/**
 * Federal Contracting AI Enhancement
 * Addresses specific shortcomings of general AI in government proposals
 * Based on GovDash analysis of general AI limitations
 */

class FederalContractingAI {
    constructor() {
        this.context = {
            rfpAnalysis: null,
            companyProfile: null,
            requirementsMatrix: [],
            evaluationCriteria: [],
            complianceAreas: [],
            sessionMemory: new Map() // Addresses memory loss between prompts
        };
        
        this.federalPatterns = {
            sectionL: /SECTION L[\:\-\s]*(.+?)(?=SECTION [A-Z]|$)/gis,
            sectionM: /SECTION M[\:\-\s]*(.+?)(?=SECTION [A-Z]|$)/gis,
            sectionC: /SECTION C[\:\-\s]*(.+?)(?=SECTION [A-Z]|$)/gis,
            shallStatements: /(?:contractor|offeror|vendor)\s+shall\s+([^.]+\.)/gi,
            evaluationFactors: /(factor\s+\d+|criteria\s+\d+)[\:\-\s]*([^.]+)/gi,
            pageLimit: /(\d+)\s*page[s]?\s*(?:limit|maximum|max)/gi
        };
        
        this.complianceKeywords = {
            section508: ['accessibility', 'section 508', 'WCAG', 'ADA compliance'],
            security: ['FISMA', 'FedRAMP', 'NIST', 'cybersecurity', 'security controls'],
            farCompliance: ['FAR', 'DFARS', 'Federal Acquisition', 'procurement'],
            smallBusiness: ['small business', 'SBA', 'WOSB', 'SDVOSB', '8(a)', 'HUBZone']
        };
        
        this.riskIndicators = {
            tightTimeline: ['expedited', 'urgent', /\b\d+\s*days?\s*(?:after|from)/],
            securityClearance: ['security clearance', 'classified', 'secret'],
            performanceBond: ['performance bond', 'surety', 'bonding'],
            liquidatedDamages: ['liquidated damages', 'penalty', 'damages'],
            unlimitedLiability: ['unlimited liability', 'indemnification']
        };
    }

    // Address Issue #1: Context Retention and Memory Loss
    maintainSessionContext(key, data) {
        this.context.sessionMemory.set(key, {
            data: data,
            timestamp: Date.now(),
            sessionId: this.getSessionId()
        });
        
        console.log(`📝 Context saved: ${key}`);
        return this.context.sessionMemory.get(key);
    }

    getSessionContext(key) {
        const contextData = this.context.sessionMemory.get(key);
        if (contextData) {
            console.log(`🔍 Context retrieved: ${key}`);
            return contextData.data;
        }
        return null;
    }

    getSessionId() {
        if (!this.sessionId) {
            this.sessionId = `federal-ai-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
        }
        return this.sessionId;
    }

    // Address Issue #2: Federal Structure Analysis (Sections L, M, C)
    async analyzeFederalStructure(rfpContent) {
        console.log('🏛️ Analyzing federal RFP structure...');
        
        const analysis = {
            sectionsFound: {},
            requirementsMatrix: [],
            evaluationStructure: {},
            complianceAreas: [],
            riskFactors: [],
            pageLimit: {},
            structureScore: 0
        };

        try {
            // Extract Section L (Instructions)
            const sectionLMatches = Array.from(rfpContent.matchAll(this.federalPatterns.sectionL));
            if (sectionLMatches.length > 0) {
                const sectionLContent = sectionLMatches[0][1];
                analysis.sectionsFound.sectionL = {
                    content: sectionLContent.substring(0, 1000) + '...',
                    length: sectionLContent.length,
                    requirementsCount: (sectionLContent.match(/shall|must|required/gi) || []).length,
                    pageLimit: this.extractPageLimits(sectionLContent)
                };
                analysis.structureScore += 30;
            }

            // Extract Section M (Evaluation)
            const sectionMMatches = Array.from(rfpContent.matchAll(this.federalPatterns.sectionM));
            if (sectionMMatches.length > 0) {
                const sectionMContent = sectionMMatches[0][1];
                analysis.sectionsFound.sectionM = {
                    content: sectionMContent.substring(0, 1000) + '...',
                    length: sectionMContent.length,
                    evaluationFactors: this.extractEvaluationFactors(sectionMContent)
                };
                analysis.evaluationStructure = analysis.sectionsFound.sectionM.evaluationFactors;
                analysis.structureScore += 40;
            }

            // Extract Section C (Requirements)
            const sectionCMatches = Array.from(rfpContent.matchAll(this.federalPatterns.sectionC));
            if (sectionCMatches.length > 0) {
                const sectionCContent = sectionCMatches[0][1];
                analysis.sectionsFound.sectionC = {
                    content: sectionCContent.substring(0, 1000) + '...',
                    length: sectionCContent.length,
                    requirementsCount: (sectionCContent.match(/shall|must|required/gi) || []).length
                };
                analysis.structureScore += 30;
            }

            // Build Requirements Matrix
            analysis.requirementsMatrix = this.buildRequirementsMatrix(rfpContent);
            
            // Extract Compliance Areas
            analysis.complianceAreas = this.extractComplianceAreas(rfpContent);
            
            // Identify Risk Factors
            analysis.riskFactors = this.identifyRiskFactors(rfpContent);

            // Save context for future use
            this.maintainSessionContext('rfpAnalysis', analysis);
            this.context.rfpAnalysis = analysis;

            console.log(`✅ Federal structure analysis complete. Score: ${analysis.structureScore}/100`);
            return analysis;

        } catch (error) {
            console.error('❌ Federal structure analysis failed:', error);
            throw new Error(`Federal structure analysis failed: ${error.message}`);
        }
    }

    extractPageLimits(content) {
        const limits = {};
        const matches = Array.from(content.matchAll(this.federalPatterns.pageLimit));
        
        matches.forEach(match => {
            const pages = parseInt(match[1]);
            const context = content.substring(Math.max(0, match.index - 100), match.index + 100);
            
            if (context.toLowerCase().includes('executive summary')) {
                limits.executiveSummary = pages;
            } else if (context.toLowerCase().includes('technical')) {
                limits.technicalApproach = pages;
            } else if (context.toLowerCase().includes('management')) {
                limits.managementApproach = pages;
            } else {
                limits.general = pages;
            }
        });
        
        return limits;
    }

    extractEvaluationFactors(content) {
        const factors = [];
        const matches = Array.from(content.matchAll(this.federalPatterns.evaluationFactors));
        
        matches.forEach(match => {
            const factorName = match[2].trim();
            
            // Try to extract weight
            const weightPattern = new RegExp(`${factorName.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}[^0-9]*(\\d+)%?`, 'i');
            const weightMatch = content.match(weightPattern);
            const weight = weightMatch ? parseInt(weightMatch[1]) : 0;
            
            factors.push({
                name: factorName,
                weight: weight,
                description: factorName,
                type: this.categorizeEvaluationFactor(factorName)
            });
        });
        
        return {
            factors: factors,
            totalWeight: factors.reduce((sum, f) => sum + f.weight, 0),
            scoringMethod: content.toLowerCase().includes('adjectival') ? 'adjectival' : 'numerical'
        };
    }

    categorizeEvaluationFactor(factorName) {
        const name = factorName.toLowerCase();
        if (name.includes('technical')) return 'technical';
        if (name.includes('management')) return 'management';
        if (name.includes('past performance')) return 'past_performance';
        if (name.includes('cost') || name.includes('price')) return 'cost';
        return 'other';
    }

    buildRequirementsMatrix(content) {
        const requirements = [];
        const matches = Array.from(content.matchAll(this.federalPatterns.shallStatements));
        
        matches.forEach((match, index) => {
            const requirement = {
                id: `REQ-${index + 1}`,
                type: 'mandatory',
                description: match[1].trim(),
                sourceSection: this.determineSourceSection(match.index, content),
                complianceStatus: 'pending',
                riskLevel: this.assessRequirementRisk(match[1]),
                responseLocation: 'TBD'
            };
            requirements.push(requirement);
        });
        
        return requirements.slice(0, 50); // Limit for performance
    }

    determineSourceSection(index, content) {
        const beforeText = content.substring(Math.max(0, index - 500), index);
        
        if (beforeText.toUpperCase().includes('SECTION L')) return 'Section L';
        if (beforeText.toUpperCase().includes('SECTION M')) return 'Section M';
        if (beforeText.toUpperCase().includes('SECTION C')) return 'Section C';
        return 'Unknown';
    }

    assessRequirementRisk(description) {
        const text = description.toLowerCase();
        
        if (text.includes('security') || text.includes('classified') || text.includes('clearance')) {
            return 'high';
        }
        if (text.includes('performance') || text.includes('penalty') || text.includes('liquidated')) {
            return 'high';
        }
        if (text.includes('accessibility') || text.includes('508') || text.includes('compliance')) {
            return 'medium';
        }
        
        return 'low';
    }

    extractComplianceAreas(content) {
        const areas = [];
        
        Object.entries(this.complianceKeywords).forEach(([area, keywords]) => {
            let mentions = 0;
            keywords.forEach(keyword => {
                const regex = new RegExp(`\\b${keyword}\\b`, 'gi');
                const matches = content.match(regex);
                if (matches) mentions += matches.length;
            });
            
            if (mentions > 0) {
                areas.push({
                    area: area,
                    mentions: mentions,
                    riskLevel: this.getComplianceRisk(area),
                    description: `Compliance requirements for ${area.replace(/([A-Z])/g, ' $1').trim()}`
                });
            }
        });
        
        return areas;
    }

    getComplianceRisk(area) {
        const highRiskAreas = ['security', 'section508'];
        return highRiskAreas.includes(area) ? 'high' : 'medium';
    }

    identifyRiskFactors(content) {
        const risks = [];
        
        Object.entries(this.riskIndicators).forEach(([riskType, indicators]) => {
            let found = false;
            
            indicators.forEach(indicator => {
                if (typeof indicator === 'string') {
                    if (content.toLowerCase().includes(indicator.toLowerCase())) {
                        found = true;
                    }
                } else if (indicator instanceof RegExp) {
                    if (indicator.test(content)) {
                        found = true;
                    }
                }
            });
            
            if (found) {
                risks.push({
                    type: riskType.replace(/([A-Z])/g, ' $1').trim(),
                    level: this.getRiskLevel(riskType),
                    description: `RFP contains ${riskType.replace(/([A-Z])/g, ' $1').trim().toLowerCase()} requirements`,
                    mitigation: this.getRiskMitigation(riskType)
                });
            }
        });
        
        return risks;
    }

    getRiskLevel(riskType) {
        const highRiskTypes = ['unlimitedLiability', 'liquidatedDamages', 'securityClearance'];
        return highRiskTypes.includes(riskType) ? 'high' : 'medium';
    }

    getRiskMitigation(riskType) {
        const mitigations = {
            tightTimeline: 'Develop accelerated project timeline with dedicated resources',
            securityClearance: 'Partner with cleared personnel or initiate clearance process',
            performanceBond: 'Secure bonding capacity and include in cost structure',
            liquidatedDamages: 'Review terms and negotiate reasonable damage caps',
            unlimitedLiability: 'Negotiate liability limitations and insurance coverage'
        };
        
        return mitigations[riskType] || 'Review requirements and develop mitigation strategy';
    }

    // Address Issue #3: Context-Aware Proposal Generation
    generateContextAwareProposal(sectionType, additionalContext = {}) {
        console.log(`📝 Generating context-aware ${sectionType} section...`);
        
        const rfpAnalysis = this.getSessionContext('rfpAnalysis') || this.context.rfpAnalysis;
        const companyProfile = this.getSessionContext('companyProfile') || this.context.companyProfile;
        
        if (!rfpAnalysis) {
            throw new Error('RFP analysis required before proposal generation');
        }
        
        const contextualPrompt = this.buildContextualPrompt(sectionType, rfpAnalysis, companyProfile, additionalContext);
        
        // Save generation context
        this.maintainSessionContext(`${sectionType}_context`, {
            prompt: contextualPrompt,
            rfpAnalysis: rfpAnalysis,
            timestamp: Date.now()
        });
        
        return {
            prompt: contextualPrompt,
            context: {
                requirements: rfpAnalysis.requirementsMatrix.length,
                evaluationFactors: rfpAnalysis.evaluationStructure.factors?.length || 0,
                complianceAreas: rfpAnalysis.complianceAreas.length,
                riskFactors: rfpAnalysis.riskFactors.length
            },
            metadata: {
                sectionType: sectionType,
                sessionId: this.getSessionId(),
                contextRetained: true
            }
        };
    }

    buildContextualPrompt(sectionType, rfpAnalysis, companyProfile = {}, additionalContext = {}) {
        const baseContext = `
FEDERAL CONTRACTING CONTEXT (Session: ${this.getSessionId()}):
📋 Requirements Matrix: ${rfpAnalysis.requirementsMatrix.length} mandatory requirements identified
⚖️ Compliance Areas: ${rfpAnalysis.complianceAreas.map(area => area.area).join(', ')}
📊 Evaluation Factors: ${rfpAnalysis.evaluationStructure.factors?.map(f => f.name).join(', ') || 'Not specified'}
⚠️ Risk Factors: ${rfpAnalysis.riskFactors.map(risk => risk.type).join(', ')}
📑 Federal Structure Score: ${rfpAnalysis.structureScore}/100

COMPANY CONTEXT:
🏢 Company: ${companyProfile.name || 'Your Company'}
🔧 Capabilities: ${companyProfile.capabilities?.join(', ') || 'Technology services'}
📈 Past Performance: ${companyProfile.pastContracts?.length || 0} relevant government contracts
`;

        const sectionPrompts = {
            executiveSummary: `${baseContext}

TASK: Write a federal proposal executive summary that addresses GovDash-identified shortcomings:

REQUIREMENTS:
1. DIRECTLY address each evaluation factor from Section M
2. EXPLICITLY reference compliance with identified requirements
3. Use FORMAL government contracting language (no generic business speak)
4. Include SPECIFIC past performance that aligns with this opportunity
5. Demonstrate MISSION UNDERSTANDING (not just technical capability)

STRUCTURE:
- Opening: Mission understanding and alignment
- Approach: How you meet each evaluation factor
- Differentiators: Unique value proposition
- Confidence: Past performance validation
- Compliance: Commitment to all requirements

TONE: Formal, confident, compliance-focused (NOT generic marketing copy)
LENGTH: 2-3 pages maximum
FOCUS: Government evaluator perspective - what they need to see`,

            technicalApproach: `${baseContext}

TASK: Write a technical approach section addressing federal contracting specifics:

CRITICAL ELEMENTS:
1. EXPLICIT response to each "shall" statement from requirements matrix
2. Reference to applicable federal standards (NIST, ISO, FedRAMP)
3. STRUCTURED methodology (not generic consulting approaches)
4. Risk mitigation for each identified risk factor
5. Compliance verification methods

STRUCTURE:
- Requirements Understanding: Show you "get it"
- Technical Solution: Architecture and methodology
- Implementation Plan: Phased approach with milestones
- Quality Assurance: Government-standard QA processes
- Risk Management: Specific to identified risks

COMPLIANCE FOCUS: Address these specific areas:
${rfpAnalysis.complianceAreas.map(area => `- ${area.description}`).join('\n')}

AVOID: Generic consulting methodology, commercial best practices without federal context`,

            managementApproach: `${baseContext}

TASK: Write a management approach demonstrating federal contracting expertise:

GOVERNMENT-SPECIFIC ELEMENTS:
1. Project management methodology adapted for federal environment
2. Organizational structure with CLEAR roles and responsibilities
3. Communication plan that includes government stakeholders
4. Quality management aligned with federal standards
5. Security and compliance oversight procedures

STRUCTURE:
- Project Management Framework: Government-appropriate methodology
- Organizational Chart: Clear hierarchy and responsibilities
- Communication Plan: Regular touchpoints with government team
- Quality Management: Federal QA standards and processes
- Risk Management: Proactive identification and mitigation

DEMONSTRATE: Previous government project management success
TONE: Professional, structured, government-experienced`,

            pastPerformance: `${baseContext}

TASK: Write past performance section that directly supports this opportunity:

SELECTION CRITERIA:
1. Choose contracts that DIRECTLY relate to this RFP's requirements
2. Include SPECIFIC performance metrics and outcomes
3. Provide government references with contact information
4. Demonstrate SIMILAR scope, complexity, and compliance requirements
5. Show PROGRESSION of capability and success

STRUCTURE:
- Contract Overview: Scope, value, timeframe
- Relevance: How it relates to current opportunity
- Performance: Specific metrics and achievements
- Challenges: How you overcame obstacles
- References: Government points of contact

FOCUS: Evaluator confidence - prove you can deliver on this specific opportunity`
        };

        const prompt = sectionPrompts[sectionType] || sectionPrompts.technicalApproach;
        
        // Add additional context if provided
        if (Object.keys(additionalContext).length > 0) {
            return prompt + `\n\nADDITIONAL CONTEXT:\n${JSON.stringify(additionalContext, null, 2)}`;
        }
        
        return prompt;
    }

    // Address Issue #4: Real-time Compliance Validation
    async validateCompliance(proposalContent, sectionType) {
        console.log(`🔍 Validating compliance for ${sectionType}...`);
        
        const rfpAnalysis = this.getSessionContext('rfpAnalysis') || this.context.rfpAnalysis;
        if (!rfpAnalysis) {
            throw new Error('RFP analysis required for compliance validation');
        }
        
        const validation = {
            overallScore: 0,
            requirementsCoverage: {},
            missingRequirements: [],
            complianceGaps: [],
            recommendations: [],
            federalLanguageCheck: {},
            riskMitigation: {}
        };
        
        // Check requirements coverage
        let coveredRequirements = 0;
        
        rfpAnalysis.requirementsMatrix.forEach((req, index) => {
            const keywords = this.extractKeywords(req.description);
            let coverageScore = 0;
            
            keywords.forEach(keyword => {
                if (proposalContent.toLowerCase().includes(keyword.toLowerCase())) {
                    coverageScore++;
                }
            });
            
            const coveragePercentage = (coverageScore / keywords.length) * 100;
            
            validation.requirementsCoverage[req.id] = {
                requirement: req.description,
                coverage: coveragePercentage,
                status: coveragePercentage >= 70 ? 'covered' : coveragePercentage >= 30 ? 'partial' : 'missing'
            };
            
            if (coveragePercentage >= 70) {
                coveredRequirements++;
            } else if (req.riskLevel === 'high') {
                validation.missingRequirements.push({
                    requirement: req.description,
                    risk: req.riskLevel,
                    recommendation: 'CRITICAL: Must add dedicated section addressing this requirement'
                });
            }
        });
        
        validation.overallScore = (coveredRequirements / rfpAnalysis.requirementsMatrix.length) * 100;
        
        // Check compliance areas
        rfpAnalysis.complianceAreas.forEach(area => {
            const mentioned = area.area.split(/(?=[A-Z])/).some(keyword => 
                proposalContent.toLowerCase().includes(keyword.toLowerCase())
            );
            
            if (!mentioned && area.riskLevel === 'high') {
                validation.complianceGaps.push({
                    area: area.area,
                    description: area.description,
                    recommendation: `Add explicit ${area.area} compliance language`
                });
            }
        });
        
        // Federal language validation
        validation.federalLanguageCheck = this.validateFederalLanguage(proposalContent);
        
        // Generate recommendations
        if (validation.overallScore < 80) {
            validation.recommendations.push('🚨 CRITICAL: Low requirements coverage - add missing sections');
        }
        if (validation.complianceGaps.length > 0) {
            validation.recommendations.push('⚖️ Add compliance language for identified gaps');
        }
        if (validation.federalLanguageCheck.informalLanguage > 0) {
            validation.recommendations.push('📝 Replace informal language with government-appropriate tone');
        }
        if (validation.overallScore >= 90) {
            validation.recommendations.push('✅ Excellent compliance coverage - ready for review');
        }
        
        console.log(`✅ Compliance validation complete. Score: ${validation.overallScore.toFixed(1)}%`);
        return validation;
    }

    extractKeywords(text) {
        return text.toLowerCase()
            .replace(/[^\w\s]/g, ' ')
            .split(/\s+/)
            .filter(word => word.length > 3)
            .slice(0, 5); // Top 5 keywords
    }

    validateFederalLanguage(content) {
        const validation = {
            informalLanguage: 0,
            missingFederalTerms: 0,
            toneScore: 0,
            suggestions: []
        };
        
        // Check for informal language
        const informalPatterns = [
            /\b(kinda|sorta|gonna|wanna)\b/gi,
            /\b(you guys|you all)\b/gi,
            /\b(awesome|cool|nice|great)\b/gi,
            /!/g
        ];
        
        informalPatterns.forEach(pattern => {
            const matches = content.match(pattern);
            if (matches) {
                validation.informalLanguage += matches.length;
                validation.suggestions.push(`Replace informal language: ${matches[0]}`);
            }
        });
        
        // Check for federal terms
        const federalTerms = ['government', 'federal', 'agency', 'compliance', 'past performance'];
        let federalTermCount = 0;
        
        federalTerms.forEach(term => {
            if (content.toLowerCase().includes(term)) {
                federalTermCount++;
            }
        });
        
        validation.missingFederalTerms = federalTerms.length - federalTermCount;
        validation.toneScore = Math.max(0, 100 - (validation.informalLanguage * 10) - (validation.missingFederalTerms * 5));
        
        return validation;
    }

    // Display comprehensive analysis results
    displayComprehensiveAnalysis(analysis) {
        return `
            <div class="federal-analysis-results">
                <div class="analysis-header">
                    <h3>🏛️ Federal Structure Analysis</h3>
                    <div class="structure-score">
                        <span class="score-value">${analysis.structureScore}/100</span>
                        <span class="score-label">Structure Score</span>
                    </div>
                </div>
                
                <div class="analysis-sections">
                    <div class="section-analysis">
                        <h4>📋 Federal Sections Found</h4>
                        ${Object.entries(analysis.sectionsFound).map(([section, data]) => `
                            <div class="section-item">
                                <strong>${section.toUpperCase()}:</strong> 
                                ${data.length} characters, ${data.requirementsCount || data.evaluationFactors?.factors?.length || 0} key elements
                            </div>
                        `).join('')}
                    </div>
                    
                    <div class="requirements-matrix">
                        <h4>⚖️ Requirements Matrix (${analysis.requirementsMatrix.length} items)</h4>
                        ${analysis.requirementsMatrix.slice(0, 5).map(req => `
                            <div class="requirement-item ${req.riskLevel}">
                                <span class="req-id">${req.id}</span>
                                <span class="req-desc">${req.description.substring(0, 100)}...</span>
                                <span class="risk-badge ${req.riskLevel}">${req.riskLevel.toUpperCase()}</span>
                            </div>
                        `).join('')}
                        ${analysis.requirementsMatrix.length > 5 ? `<div class="more-items">... and ${analysis.requirementsMatrix.length - 5} more requirements</div>` : ''}
                    </div>
                    
                    <div class="compliance-areas">
                        <h4>🔒 Compliance Areas (${analysis.complianceAreas.length} identified)</h4>
                        ${analysis.complianceAreas.map(area => `
                            <div class="compliance-item">
                                <span class="compliance-name">${area.area}</span>
                                <span class="compliance-mentions">${area.mentions} mentions</span>
                                <span class="risk-level ${area.riskLevel}">${area.riskLevel.toUpperCase()}</span>
                            </div>
                        `).join('')}
                    </div>
                    
                    <div class="risk-factors">
                        <h4>⚠️ Risk Factors (${analysis.riskFactors.length} identified)</h4>
                        ${analysis.riskFactors.map(risk => `
                            <div class="risk-item ${risk.level}">
                                <span class="risk-type">${risk.type}</span>
                                <span class="risk-desc">${risk.description}</span>
                                <div class="mitigation">${risk.mitigation}</div>
                            </div>
                        `).join('')}
                    </div>
                </div>
                
                <div class="analysis-summary">
                    <h4>📊 Analysis Summary</h4>
                    <p><strong>Federal Structure:</strong> ${analysis.structureScore >= 80 ? '✅ Excellent' : analysis.structureScore >= 60 ? '⚠️ Good' : '❌ Needs Improvement'}</p>
                    <p><strong>Requirements Complexity:</strong> ${analysis.requirementsMatrix.length} mandatory requirements identified</p>
                    <p><strong>Compliance Burden:</strong> ${analysis.complianceAreas.length} compliance areas requiring attention</p>
                    <p><strong>Risk Assessment:</strong> ${analysis.riskFactors.filter(r => r.level === 'high').length} high-risk factors identified</p>
                </div>
            </div>
        `;
    }
}

// Global instance
const federalAI = new FederalContractingAI();

// Export for use in platform
window.federalAI = federalAI;