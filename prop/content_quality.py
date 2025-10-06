"""Advanced Content Quality Controller for Enhanced Document Generation.

This module provides sophisticated content enhancement capabilities to ensure
Fortune 500-level proposal quality with business analyst focus.
"""

import os
import json
from typing import Dict, List, Any
from .llm_openai import LLMClient


class ContentQualityController:
    """Controls and enhances content quality for business-focused proposals."""
    
    def __init__(self, model: str = "claude-3-5-sonnet-20241022"):
        self.llm = LLMClient(model)
        self.quality_standards = self._load_quality_standards()
    
    def _load_quality_standards(self) -> str:
        """Load quality standards and enhancement rules."""
        try:
            rules_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), 
                "prompts", "enhanced_content_rules.md"
            )
            if os.path.exists(rules_path):
                with open(rules_path, "r", encoding="utf-8") as f:
                    return f.read()
        except Exception:
            pass
        return ""
    
    def enhance_content_quality(self, content: str, content_type: str = "paragraph") -> str:
        """Enhance content quality with business sophistication."""
        enhancement_prompt = f"""
{self.quality_standards}

**CONTENT TO ENHANCE**: {content}

**ENHANCEMENT MISSION**: 
Transform this content into Fortune 500-caliber proposal material that would win $100M+ government contracts.

**SPECIFIC IMPROVEMENTS REQUIRED**:
1. **Business Value Amplification**: Add quantified ROI metrics and competitive advantages
2. **Executive Language Upgrade**: Use sophisticated business terminology appropriate for C-suite evaluation
3. **Risk Intelligence Integration**: Include proactive risk identification and mitigation strategies  
4. **Implementation Excellence**: Add detailed methodology with milestone-driven approach
5. **Competitive Differentiation**: Emphasize unique value propositions and market advantages
6. **Evidence-Based Claims**: Support all assertions with industry benchmarks and best practices

**QUALITY CHECKPOINTS**:
- Would this content impress a Fortune 500 CEO?
- Does it demonstrate deep domain expertise?
- Are the business benefits quantified and compelling?
- Is the implementation approach realistic and detailed?
- Would evaluators score this content as "Excellent"?

**OUTPUT REQUIREMENTS**:
- Maintain same length but dramatically increase business sophistication
- Use metrics, percentages, timeframes, and dollar amounts where applicable
- Include industry-leading best practices and methodologies
- Ensure content reads like it was written by a senior business analyst with 20+ years experience

Generate enhanced content that wins contracts:
"""
        
        try:
            enhanced = self.llm.complete(enhancement_prompt)
            return enhanced.strip()
        except Exception:
            return content  # Fallback to original if enhancement fails
    
    def add_business_intelligence(self, bullets: List[str]) -> List[str]:
        """Add business intelligence and competitive analysis to bullet points."""
        enhancement_prompt = f"""
{self.quality_standards}

**BULLETS TO ENHANCE**: {json.dumps(bullets, indent=2)}

**BUSINESS INTELLIGENCE MISSION**:
Transform these bullets into business-intelligent content that demonstrates:
- Strategic market understanding
- Competitive positioning
- ROI and cost-benefit analysis
- Risk management expertise
- Implementation excellence

**ENHANCEMENT FRAMEWORK**:
1. Add quantified business benefits (%, $, time savings)
2. Include competitive intelligence and market positioning
3. Reference industry best practices and benchmarks
4. Add risk mitigation strategies
5. Include success metrics and KPIs
6. Demonstrate thought leadership

**OUTPUT FORMAT**: Return enhanced bullets in same structure but with 2-3x more business sophistication.

Generate business-intelligent bullets:
"""
        
        try:
            enhanced_response = self.llm.complete(enhancement_prompt)
            # Parse the response to extract enhanced bullets
            return self._parse_enhanced_bullets(enhanced_response, bullets)
        except Exception:
            return bullets  # Fallback to original if enhancement fails
    
    def _parse_enhanced_bullets(self, response: str, original_bullets: List[str]) -> List[str]:
        """Parse enhanced bullets from LLM response."""
        try:
            # Try to extract bullets from response
            lines = response.split('\n')
            enhanced_bullets = []
            
            for line in lines:
                line = line.strip()
                if ':' in line and any(category in line.lower() for category in 
                    ['executive-value', 'technical-solution', 'financial-impact', 
                     'risk-control', 'implementation-plan', 'success-metrics', 'competitive-edge']):
                    enhanced_bullets.append(line)
            
            # If we got good enhanced bullets, return them
            if len(enhanced_bullets) >= len(original_bullets) * 0.7:
                return enhanced_bullets
            else:
                return original_bullets
        except Exception:
            return original_bullets
    
    def validate_business_quality(self, content: str) -> Dict[str, Any]:
        """Validate content against business quality standards."""
        validation_criteria = {
            "business_value_present": "ROI" in content or "benefit" in content.lower(),
            "metrics_included": any(char in content for char in ['%', '$', '+']),
            "risk_addressed": "risk" in content.lower() or "mitigation" in content.lower(),
            "implementation_detailed": "approach" in content.lower() or "methodology" in content.lower(),
            "competitive_edge": "advantage" in content.lower() or "differentiator" in content.lower(),
            "professional_language": len(content.split()) > 100,  # Sufficient detail
        }
        
        score = sum(validation_criteria.values()) / len(validation_criteria) * 100
        
        return {
            "quality_score": score,
            "criteria_met": validation_criteria,
            "recommendations": self._generate_recommendations(validation_criteria)
        }
    
    def _generate_recommendations(self, criteria: Dict[str, bool]) -> List[str]:
        """Generate improvement recommendations based on criteria."""
        recommendations = []
        
        if not criteria["business_value_present"]:
            recommendations.append("Add quantified business benefits and ROI analysis")
        if not criteria["metrics_included"]:
            recommendations.append("Include specific metrics, percentages, and dollar amounts")
        if not criteria["risk_addressed"]:
            recommendations.append("Address risks with specific mitigation strategies")
        if not criteria["implementation_detailed"]:
            recommendations.append("Provide more detailed implementation methodology")
        if not criteria["competitive_edge"]:
            recommendations.append("Emphasize competitive advantages and differentiators")
        if not criteria["professional_language"]:
            recommendations.append("Expand content with more professional detail")
        
        return recommendations