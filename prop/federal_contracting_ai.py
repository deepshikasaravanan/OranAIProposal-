"""
Federal Contracting AI Enhancement Module
Addresses specific shortcomings of general AI in government proposal creation
Based on GovDash analysis of general AI limitations
"""

from typing import Dict, List, Any, Optional
import re
import json
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ComplianceRequirement:
    """Structure for tracking compliance requirements"""
    section: str
    requirement_id: str
    description: str
    source_section: str  # L, M, C, etc.
    compliance_status: str  # "met", "partial", "missing", "pending"
    response_location: str
    risk_level: str  # "high", "medium", "low"

@dataclass
class FederalSection:
    """Structure for federal RFP sections"""
    section_id: str  # L-1, M-1, C-1, etc.
    title: str
    content: str
    section_type: str  # "instruction", "evaluation", "requirements"
    requirements: List[ComplianceRequirement]
    page_limit: Optional[int]
    evaluation_weight: Optional[float]

class FederalContractingAI:
    """
    Specialized AI assistant for federal contracting that addresses
    the shortcomings of general AI identified by GovDash
    """
    
    def __init__(self):
        self.federal_frameworks = {
            "FAR": "Federal Acquisition Regulation",
            "DFARS": "Defense Federal Acquisition Regulation Supplement", 
            "GSA": "General Services Administration",
            "CIO-SP3": "Chief Information Officer-Solutions and Partners 3",
            "SEWP": "Solutions for Enterprise-Wide Procurement"
        }
        
        self.section_patterns = {
            "section_l": r"SECTION L[:\-\s]*(.+?)(?=SECTION [A-Z]|$)",
            "section_m": r"SECTION M[:\-\s]*(.+?)(?=SECTION [A-Z]|$)", 
            "section_c": r"SECTION C[:\-\s]*(.+?)(?=SECTION [A-Z]|$)",
            "requirements": r"(?i)(shall|must|will|required?|mandatory)",
            "evaluation_criteria": r"(?i)(evaluat|scor|weight|factor|criteri)",
            "page_limits": r"(?i)(\d+)\s*page[s]?\s*(?:limit|maximum|max)"
        }
        
        self.compliance_keywords = {
            "section_508": ["accessibility", "section 508", "WCAG", "ADA compliance"],
            "security": ["FISMA", "FedRAMP", "NIST", "cybersecurity", "security controls"],
            "far_compliance": ["FAR", "Federal Acquisition", "procurement", "contract terms"],
            "small_business": ["small business", "SBA", "WOSB", "SDVOSB", "8(a)", "HUBZone"],
            "past_performance": ["past performance", "reference", "prior work", "experience"]
        }
        
    def analyze_federal_structure(self, rfp_content: str) -> Dict[str, Any]:
        """
        Analyzes RFP structure specifically for federal format
        Addresses: Structural awareness gaps identified by GovDash
        """
        analysis = {
            "sections_found": {},
            "requirements_matrix": [],
            "evaluation_structure": {},
            "compliance_areas": [],
            "page_limits": {},
            "risk_factors": []
        }
        
        # Extract and analyze federal sections
        for section_type, pattern in self.section_patterns.items():
            matches = re.finditer(pattern, rfp_content, re.DOTALL | re.IGNORECASE)
            for match in matches:
                if section_type in ["section_l", "section_m", "section_c"]:
                    section_content = match.group(1)
                    analysis["sections_found"][section_type] = {
                        "content": section_content[:1000] + "..." if len(section_content) > 1000 else section_content,
                        "length": len(section_content),
                        "requirements_count": len(re.findall(self.section_patterns["requirements"], section_content))
                    }
        
        # Extract compliance requirements
        analysis["compliance_areas"] = self._extract_compliance_requirements(rfp_content)
        
        # Build requirements matrix
        analysis["requirements_matrix"] = self._build_requirements_matrix(rfp_content)
        
        # Extract evaluation criteria
        analysis["evaluation_structure"] = self._extract_evaluation_criteria(rfp_content)
        
        # Identify risk factors
        analysis["risk_factors"] = self._identify_risk_factors(rfp_content)
        
        return analysis
    
    def _extract_compliance_requirements(self, content: str) -> List[Dict[str, Any]]:
        """Extract compliance areas mentioned in RFP"""
        compliance_areas = []
        
        for area, keywords in self.compliance_keywords.items():
            mentions = []
            for keyword in keywords:
                pattern = rf"(?i)\b{re.escape(keyword)}\b"
                matches = re.finditer(pattern, content)
                mentions.extend([match.span() for match in matches])
            
            if mentions:
                compliance_areas.append({
                    "area": area,
                    "keyword_matches": len(mentions),
                    "risk_level": "high" if area in ["security", "section_508"] else "medium",
                    "description": f"Compliance requirements for {area.replace('_', ' ').title()}"
                })
        
        return compliance_areas
    
    def _build_requirements_matrix(self, content: str) -> List[ComplianceRequirement]:
        """Build comprehensive requirements matrix"""
        requirements = []
        
        # Extract "shall" statements (mandatory requirements)
        shall_pattern = r"(?i)(?:contractor|offeror|vendor)\s+shall\s+([^.]+\.)"
        shall_matches = re.finditer(shall_pattern, content)
        
        for i, match in enumerate(shall_matches):
            requirement = ComplianceRequirement(
                section=f"REQ-{i+1}",
                requirement_id=f"SHALL-{i+1}",
                description=match.group(1).strip(),
                source_section="Unknown",  # Would be determined by position analysis
                compliance_status="pending",
                response_location="TBD",
                risk_level="high"
            )
            requirements.append(requirement)
        
        return requirements[:20]  # Limit for example
    
    def _extract_evaluation_criteria(self, content: str) -> Dict[str, Any]:
        """Extract evaluation criteria and weights"""
        evaluation = {
            "factors": [],
            "total_weight": 0,
            "scoring_method": "unknown"
        }
        
        # Look for evaluation factors
        factor_pattern = r"(?i)(factor\s+\d+|criteria\s+\d+)[:\-\s]*([^.]+)"
        factor_matches = re.finditer(factor_pattern, content)
        
        for match in factor_matches:
            factor_name = match.group(2).strip()
            
            # Try to extract weight
            weight_pattern = rf"(?i){re.escape(factor_name)}[^0-9]*(\d+)%?"
            weight_match = re.search(weight_pattern, content)
            weight = int(weight_match.group(1)) if weight_match else 0
            
            evaluation["factors"].append({
                "name": factor_name,
                "weight": weight,
                "description": factor_name
            })
            evaluation["total_weight"] += weight
        
        return evaluation
    
    def _identify_risk_factors(self, content: str) -> List[Dict[str, str]]:
        """Identify potential risk factors in RFP"""
        risks = []
        
        risk_indicators = {
            "tight_timeline": [r"(?i)\b\d+\s*days?\s*(?:after|from)", r"(?i)expedited", r"(?i)urgent"],
            "security_clearance": [r"(?i)security clearance", r"(?i)classified", r"(?i)secret"],
            "performance_bond": [r"(?i)performance bond", r"(?i)surety", r"(?i)bonding"],
            "liquidated_damages": [r"(?i)liquidated damages", r"(?i)penalty", r"(?i)damages"],
            "unlimited_liability": [r"(?i)unlimited liability", r"(?i)indemnif"]
        }
        
        for risk_type, patterns in risk_indicators.items():
            for pattern in patterns:
                if re.search(pattern, content):
                    risks.append({
                        "type": risk_type.replace("_", " ").title(),
                        "level": "high" if risk_type in ["unlimited_liability", "liquidated_damages"] else "medium",
                        "description": f"RFP contains {risk_type.replace('_', ' ')} requirements"
                    })
                    break
        
        return risks
    
    def generate_federal_proposal_structure(self, rfp_analysis: Dict[str, Any], 
                                          company_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate proposal structure based on federal requirements
        Addresses: Generic language and compliance issues
        """
        structure = {
            "executive_summary": {
                "focus": "Government evaluation criteria alignment",
                "compliance_callouts": [],
                "win_themes": [],
                "length": "2-3 pages"
            },
            "technical_approach": {
                "sections": [],
                "compliance_matrix": [],
                "methodology": "Federal best practices"
            },
            "management_approach": {
                "organizational_structure": {},
                "key_personnel": [],
                "past_performance_alignment": []
            },
            "past_performance": {
                "relevant_contracts": [],
                "government_references": [],
                "performance_metrics": []
            },
            "pricing": {
                "structure": "Government CLIN format",
                "labor_categories": [],
                "cost_narrative": []
            }
        }
        
        # Map requirements to sections
        for req in rfp_analysis.get("requirements_matrix", []):
            if "technical" in req.description.lower():
                structure["technical_approach"]["compliance_matrix"].append({
                    "requirement": req.description,
                    "response_section": "Technical Approach",
                    "compliance_method": "Direct response with supporting evidence"
                })
        
        # Add compliance callouts for executive summary
        for compliance_area in rfp_analysis.get("compliance_areas", []):
            structure["executive_summary"]["compliance_callouts"].append({
                "area": compliance_area["area"],
                "statement": f"Full compliance with {compliance_area['area'].replace('_', ' ').title()} requirements",
                "risk_mitigation": "Detailed in technical approach section"
            })
        
        return structure
    
    def generate_context_aware_prompts(self, section_type: str, rfp_analysis: Dict[str, Any], 
                                     company_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate context-aware prompts that maintain consistency
        Addresses: Prompt-by-prompt workflow issues and memory loss
        """
        base_context = f"""
        FEDERAL CONTRACTING CONTEXT:
        - RFP contains {len(rfp_analysis.get('requirements_matrix', []))} compliance requirements
        - Evaluation factors: {', '.join([f['name'] for f in rfp_analysis.get('evaluation_structure', {}).get('factors', [])])}
        - Compliance areas: {', '.join([area['area'] for area in rfp_analysis.get('compliance_areas', [])])}
        - Risk factors: {', '.join([risk['type'] for risk in rfp_analysis.get('risk_factors', [])])}
        
        COMPANY PROFILE:
        - Name: {company_data.get('name', 'Company')}
        - Capabilities: {', '.join(company_data.get('capabilities', []))}
        - Past Performance: {len(company_data.get('past_contracts', []))} relevant contracts
        """
        
        prompts = {
            "executive_summary": f"""
            {base_context}
            
            Write an executive summary for a federal proposal that:
            1. Directly addresses the government's stated evaluation criteria
            2. Highlights compliance with all major requirements
            3. Uses formal government contracting language
            4. Includes specific past performance references
            5. Demonstrates understanding of the mission criticality
            
            TONE: Formal, confident, compliance-focused
            LENGTH: 2-3 pages maximum
            FOCUS: Win themes tied to evaluation factors
            """,
            
            "technical_approach": f"""
            {base_context}
            
            Write a technical approach section that:
            1. Responds to each technical requirement explicitly
            2. Uses government-standard methodology descriptions
            3. Includes compliance verification methods
            4. References applicable standards (NIST, ISO, etc.)
            5. Demonstrates understanding of federal IT architecture
            
            TONE: Technical but accessible to government evaluators
            STRUCTURE: Requirement → Approach → Validation → Risk Mitigation
            COMPLIANCE: Address each "shall" statement directly
            """,
            
            "management_approach": f"""
            {base_context}
            
            Write a management approach section that:
            1. Describes project management methodology
            2. Shows organizational structure with clear roles
            3. Demonstrates government contracting experience
            4. Includes quality assurance and risk management
            5. Addresses security and compliance oversight
            
            TONE: Professional, structured, government-focused
            ELEMENTS: RACI matrix, communication plan, milestone tracking
            EMPHASIS: Proven government project management experience
            """
        }
        
        return prompts.get(section_type, prompts["technical_approach"])
    
    def validate_compliance_coverage(self, proposal_content: str, 
                                   requirements_matrix: List[ComplianceRequirement]) -> Dict[str, Any]:
        """
        Validate that proposal covers all compliance requirements
        Addresses: Missing requirements and compliance gaps
        """
        validation = {
            "coverage_score": 0,
            "missing_requirements": [],
            "partial_coverage": [],
            "well_covered": [],
            "recommendations": []
        }
        
        covered_count = 0
        
        for req in requirements_matrix:
            # Check if requirement is addressed in proposal
            req_keywords = req.description.lower().split()
            coverage_score = 0
            
            for keyword in req_keywords[:5]:  # Check first 5 keywords
                if keyword in proposal_content.lower():
                    coverage_score += 1
            
            coverage_percentage = (coverage_score / min(5, len(req_keywords))) * 100
            
            if coverage_percentage >= 80:
                validation["well_covered"].append({
                    "requirement": req.description,
                    "coverage": f"{coverage_percentage:.0f}%"
                })
                covered_count += 1
            elif coverage_percentage >= 40:
                validation["partial_coverage"].append({
                    "requirement": req.description,
                    "coverage": f"{coverage_percentage:.0f}%",
                    "suggestion": "Add more specific details addressing this requirement"
                })
            else:
                validation["missing_requirements"].append({
                    "requirement": req.description,
                    "risk_level": req.risk_level,
                    "recommendation": "Must add dedicated section addressing this requirement"
                })
        
        validation["coverage_score"] = (covered_count / len(requirements_matrix)) * 100 if requirements_matrix else 100
        
        # Generate recommendations
        if validation["coverage_score"] < 80:
            validation["recommendations"].append("CRITICAL: Add sections for missing high-risk requirements")
        if validation["partial_coverage"]:
            validation["recommendations"].append("Enhance sections with partial coverage")
        if validation["coverage_score"] >= 90:
            validation["recommendations"].append("Excellent compliance coverage - ready for review")
        
        return validation
    
    def get_federal_enhancement_suggestions(self, content: str) -> List[Dict[str, str]]:
        """
        Suggest enhancements for federal compliance and tone
        Addresses: Generic language issues
        """
        suggestions = []
        
        # Check for informal language
        informal_patterns = [
            (r"\bkinda\b|\bsorta\b|\bgonna\b", "Remove informal contractions"),
            (r"\byou guys\b|\byou all\b", "Use 'the Government' or 'the Agency'"),
            (r"\bawesome\b|\bcool\b|\bnice\b", "Use professional descriptors"),
            (r"!", "Minimize exclamation points in formal proposals")
        ]
        
        for pattern, suggestion in informal_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                suggestions.append({
                    "type": "Tone Enhancement",
                    "issue": f"Found informal language: {pattern}",
                    "suggestion": suggestion,
                    "priority": "Medium"
                })
        
        # Check for missing federal language
        federal_language_checks = [
            ("past performance", "Include past performance references"),
            ("compliance", "Add compliance verification statements"),
            ("federal|government", "Reference government standards and frameworks"),
            ("security", "Address security requirements if applicable")
        ]
        
        for term, suggestion in federal_language_checks:
            if not re.search(term, content, re.IGNORECASE):
                suggestions.append({
                    "type": "Federal Enhancement",
                    "issue": f"Missing {term} language",
                    "suggestion": suggestion,
                    "priority": "High"
                })
        
        return suggestions
    
    def get_implementation_config(self) -> Dict[str, Any]:
        """Configuration for implementing federal contracting AI enhancements"""
        return {
            "workflow_improvements": {
                "context_retention": "Maintain RFP analysis context throughout proposal generation",
                "section_awareness": "Reference previous sections to maintain consistency",
                "compliance_tracking": "Track requirement coverage in real-time",
                "automated_validation": "Check compliance before final output"
            },
            "specialized_capabilities": {
                "federal_structure_analysis": "Parse Sections L, M, C automatically",
                "requirements_matrix": "Generate comprehensive compliance matrix",
                "evaluation_alignment": "Align content to evaluation criteria",
                "risk_identification": "Flag high-risk requirements early"
            },
            "quality_controls": {
                "compliance_verification": "Validate all 'shall' statements addressed",
                "tone_consistency": "Ensure formal government language throughout",
                "section_cohesion": "Maintain narrative flow between sections",
                "reference_accuracy": "Verify all citations and references"
            }
        }