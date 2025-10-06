"""
Enhanced AI GovCon Agent - Additional Processing Methods
Supporting methods for comprehensive document analysis and insight generation
"""

from typing import List, Dict, Any
from datetime import datetime


class GovConAgentExtensions:
    """Additional methods for the Enhanced GovCon Agent"""
    
    async def _create_compliance_matrix(self, requirements: List[Any], sections: List[Any]) -> Dict[str, Any]:
        """Create comprehensive compliance matrix"""
        compliance_matrix = {
            "total_requirements": len(requirements),
            "by_compliance_type": {
                "mandatory": 0,
                "desirable": 0,
                "optional": 0
            },
            "by_category": {
                "technical": 0,
                "management": 0,
                "compliance": 0,
                "security": 0,
                "performance": 0
            },
            "by_priority": {
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0
            },
            "verification_methods": {
                "testing": 0,
                "demonstration": 0,
                "documentation": 0,
                "audit": 0,
                "review": 0
            },
            "risk_assessment": {
                "high_risk_requirements": 0,
                "medium_risk_requirements": 0,
                "low_risk_requirements": 0
            },
            "coverage_analysis": self._analyze_requirement_coverage(requirements, sections)
        }
        
        # Count requirements by type
        for req in requirements:
            # Compliance type
            compliance_type = getattr(req, 'compliance_type', 'Optional').lower()
            if compliance_type in compliance_matrix["by_compliance_type"]:
                compliance_matrix["by_compliance_type"][compliance_type] += 1
            
            # Category
            category = getattr(req, 'category', 'General').lower()
            if category in compliance_matrix["by_category"]:
                compliance_matrix["by_category"][category] += 1
            
            # Priority
            priority = getattr(req, 'priority', 'Low').lower()
            if priority in compliance_matrix["by_priority"]:
                compliance_matrix["by_priority"][priority] += 1
            
            # Verification method
            verification = getattr(req, 'verification_method', 'Review').lower()
            if verification in compliance_matrix["verification_methods"]:
                compliance_matrix["verification_methods"][verification] += 1
            
            # Risk assessment
            risks = getattr(req, 'associated_risks', [])
            if len(risks) >= 3:
                compliance_matrix["risk_assessment"]["high_risk_requirements"] += 1
            elif len(risks) >= 1:
                compliance_matrix["risk_assessment"]["medium_risk_requirements"] += 1
            else:
                compliance_matrix["risk_assessment"]["low_risk_requirements"] += 1
        
        return compliance_matrix
    
    def _analyze_requirement_coverage(self, requirements: List[Any], sections: List[Any]) -> Dict[str, Any]:
        """Analyze requirement coverage across sections"""
        coverage = {
            "section_coverage": {},
            "gaps_identified": [],
            "dense_sections": [],
            "sparse_sections": []
        }
        
        # Analyze coverage by section
        for section in sections:
            section_id = getattr(section, 'id', 'unknown')
            req_count = getattr(section, 'requirements_count', 0)
            
            coverage["section_coverage"][section_id] = {
                "requirements_count": req_count,
                "section_title": getattr(section, 'title', 'Unknown'),
                "coverage_density": req_count / max(1, (getattr(section, 'page_end', 1) - getattr(section, 'page_start', 1) + 1))
            }
            
            # Identify dense and sparse sections
            if req_count > 15:
                coverage["dense_sections"].append(section_id)
            elif req_count < 3:
                coverage["sparse_sections"].append(section_id)
        
        # Identify potential gaps
        expected_sections = ["technical", "management", "pricing", "past_performance"]
        found_sections = [getattr(s, 'section_type', '') for s in sections]
        
        for expected in expected_sections:
            if expected not in found_sections:
                coverage["gaps_identified"].append(f"Missing {expected} section")
        
        return coverage
    
    def _create_navigation_structure(self, sections: List[Any]) -> Dict[str, Any]:
        """Create interactive navigation structure"""
        navigation = {
            "table_of_contents": [],
            "page_index": {},
            "section_hierarchy": {},
            "cross_references": [],
            "bookmarks": [],
            "quick_access": {
                "high_priority_requirements": [],
                "compliance_items": [],
                "deadlines": [],
                "key_sections": []
            }
        }
        
        # Build table of contents
        for section in sections:
            toc_entry = {
                "id": getattr(section, 'id', ''),
                "title": getattr(section, 'title', ''),
                "page_start": getattr(section, 'page_start', 1),
                "page_end": getattr(section, 'page_end', 1),
                "section_type": getattr(section, 'section_type', 'general'),
                "requirements_count": getattr(section, 'requirements_count', 0),
                "subsections": getattr(section, 'subsections', [])
            }
            navigation["table_of_contents"].append(toc_entry)
            
            # Build page index
            for page in range(toc_entry["page_start"], toc_entry["page_end"] + 1):
                if page not in navigation["page_index"]:
                    navigation["page_index"][page] = []
                navigation["page_index"][page].append(toc_entry["id"])
            
            # Add to quick access if important
            if toc_entry["requirements_count"] > 10:
                navigation["quick_access"]["key_sections"].append({
                    "section_id": toc_entry["id"],
                    "title": toc_entry["title"],
                    "reason": f"High requirement density ({toc_entry['requirements_count']} requirements)"
                })
        
        # Build section hierarchy
        for section in sections:
            section_type = getattr(section, 'section_type', 'general')
            if section_type not in navigation["section_hierarchy"]:
                navigation["section_hierarchy"][section_type] = []
            
            navigation["section_hierarchy"][section_type].append({
                "id": getattr(section, 'id', ''),
                "title": getattr(section, 'title', ''),
                "page_range": f"{getattr(section, 'page_start', 1)}-{getattr(section, 'page_end', 1)}"
            })
        
        return navigation
    
    async def _assess_document_risks(self, requirements: List[Any], sections: List[Any]) -> Dict[str, Any]:
        """Assess risks in document requirements and structure"""
        risk_assessment = {
            "overall_risk_score": 0,
            "risk_categories": {
                "technical_complexity": {"score": 0, "risks": []},
                "timeline_pressure": {"score": 0, "risks": []},
                "compliance_burden": {"score": 0, "risks": []},
                "resource_intensity": {"score": 0, "risks": []},
                "integration_challenges": {"score": 0, "risks": []}
            },
            "high_risk_requirements": [],
            "mitigation_strategies": [],
            "risk_matrix": self._create_risk_matrix(requirements)
        }
        
        # Analyze technical complexity risks
        technical_indicators = ["complex", "advanced", "sophisticated", "cutting-edge", "state-of-the-art"]
        tech_risk_count = 0
        
        for req in requirements:
            req_text = getattr(req, 'text', '').lower()
            risk_indicators = sum(1 for indicator in technical_indicators if indicator in req_text)
            
            if risk_indicators > 0:
                tech_risk_count += risk_indicators
                if risk_indicators >= 2:
                    risk_assessment["high_risk_requirements"].append({
                        "requirement_id": getattr(req, 'id', ''),
                        "text": getattr(req, 'text', ''),
                        "risk_type": "Technical Complexity",
                        "risk_level": "High" if risk_indicators >= 3 else "Medium"
                    })
        
        risk_assessment["risk_categories"]["technical_complexity"]["score"] = min(10, tech_risk_count)
        
        # Analyze timeline pressure
        timeline_indicators = ["immediate", "urgent", "asap", "quickly", "short timeline", "tight schedule"]
        timeline_risk_count = 0
        
        for req in requirements:
            req_text = getattr(req, 'text', '').lower()
            timeline_risks = sum(1 for indicator in timeline_indicators if indicator in req_text)
            timeline_risk_count += timeline_risks
        
        risk_assessment["risk_categories"]["timeline_pressure"]["score"] = min(10, timeline_risk_count)
        
        # Analyze compliance burden
        compliance_count = sum(1 for req in requirements 
                             if getattr(req, 'compliance_type', '') == 'Mandatory')
        compliance_score = min(10, compliance_count / 5)  # Normalize to scale of 10
        risk_assessment["risk_categories"]["compliance_burden"]["score"] = compliance_score
        
        # Calculate overall risk score
        category_scores = [cat["score"] for cat in risk_assessment["risk_categories"].values()]
        risk_assessment["overall_risk_score"] = sum(category_scores) / len(category_scores)
        
        # Generate mitigation strategies
        risk_assessment["mitigation_strategies"] = self._generate_mitigation_strategies(risk_assessment)
        
        return risk_assessment
    
    def _create_risk_matrix(self, requirements: List[Any]) -> Dict[str, Any]:
        """Create risk matrix for requirements"""
        risk_matrix = {
            "high_impact_high_probability": [],
            "high_impact_low_probability": [],
            "low_impact_high_probability": [],
            "low_impact_low_probability": []
        }
        
        for req in requirements:
            risks = getattr(req, 'associated_risks', [])
            priority = getattr(req, 'priority', 'Low')
            
            # Simplified risk categorization
            if len(risks) >= 2 and priority in ['High', 'Critical']:
                risk_matrix["high_impact_high_probability"].append({
                    "requirement_id": getattr(req, 'id', ''),
                    "risks": risks,
                    "priority": priority
                })
            elif len(risks) >= 2:
                risk_matrix["high_impact_low_probability"].append({
                    "requirement_id": getattr(req, 'id', ''),
                    "risks": risks,
                    "priority": priority
                })
            elif priority in ['High', 'Critical']:
                risk_matrix["low_impact_high_probability"].append({
                    "requirement_id": getattr(req, 'id', ''),
                    "risks": risks,
                    "priority": priority
                })
            else:
                risk_matrix["low_impact_low_probability"].append({
                    "requirement_id": getattr(req, 'id', ''),
                    "risks": risks,
                    "priority": priority
                })
        
        return risk_matrix
    
    def _generate_mitigation_strategies(self, risk_assessment: Dict[str, Any]) -> List[str]:
        """Generate mitigation strategies based on identified risks"""
        strategies = []
        
        # Technical complexity mitigation
        if risk_assessment["risk_categories"]["technical_complexity"]["score"] > 6:
            strategies.extend([
                "Conduct technical feasibility study before proposal submission",
                "Identify and engage with technical subject matter experts",
                "Consider partnering with organizations having relevant expertise",
                "Plan for proof-of-concept development in early project phases"
            ])
        
        # Timeline pressure mitigation
        if risk_assessment["risk_categories"]["timeline_pressure"]["score"] > 6:
            strategies.extend([
                "Implement agile development methodology for rapid delivery",
                "Identify critical path items and allocate additional resources",
                "Establish clear milestone checkpoints with buffer time",
                "Consider phased delivery approach to meet early deadlines"
            ])
        
        # Compliance burden mitigation
        if risk_assessment["risk_categories"]["compliance_burden"]["score"] > 6:
            strategies.extend([
                "Engage compliance specialists early in project planning",
                "Establish dedicated compliance review processes",
                "Create compliance tracking and reporting mechanisms",
                "Plan for additional time and resources for compliance activities"
            ])
        
        return strategies
    
    async def _generate_actionable_insights(self, sections: List[Any], requirements: List[Any], deadlines: List[Dict[str, Any]]) -> List[str]:
        """Generate actionable insights from document analysis"""
        insights = []
        
        # Section-based insights
        section_types = [getattr(s, 'section_type', '') for s in sections]
        if 'technical' in section_types:
            tech_sections = [s for s in sections if getattr(s, 'section_type', '') == 'technical']
            total_tech_reqs = sum(getattr(s, 'requirements_count', 0) for s in tech_sections)
            if total_tech_reqs > 20:
                insights.append(f"High technical complexity detected: {total_tech_reqs} technical requirements identified. Consider assembling specialized technical team.")
        
        # Requirement-based insights
        critical_reqs = [r for r in requirements if getattr(r, 'priority', '') == 'Critical']
        if len(critical_reqs) > 10:
            insights.append(f"Attention: {len(critical_reqs)} critical requirements identified. These require immediate focus and dedicated resources.")
        
        mandatory_reqs = [r for r in requirements if getattr(r, 'compliance_type', '') == 'Mandatory']
        if len(mandatory_reqs) > 15:
            insights.append(f"Compliance Alert: {len(mandatory_reqs)} mandatory requirements. Recommend early compliance review and validation process.")
        
        # Deadline-based insights
        urgent_deadlines = [d for d in deadlines if d.get('days_remaining', 100) <= 14]
        if urgent_deadlines:
            insights.append(f"Urgent Timeline: {len(urgent_deadlines)} deadlines within 2 weeks. Immediate action required for proposal timeline.")
        
        # Risk-based insights
        high_risk_reqs = [r for r in requirements if len(getattr(r, 'associated_risks', [])) >= 2]
        if len(high_risk_reqs) > 5:
            insights.append(f"Risk Management: {len(high_risk_reqs)} high-risk requirements identified. Develop comprehensive risk mitigation plan.")
        
        # Verification method insights
        testing_reqs = [r for r in requirements if getattr(r, 'verification_method', '') == 'Testing']
        if len(testing_reqs) > 10:
            insights.append(f"Testing Focus: {len(testing_reqs)} requirements require testing verification. Plan comprehensive testing strategy and infrastructure.")
        
        # Integration insights
        integration_keywords = ['integrate', 'interface', 'connect', 'interoperate']
        integration_reqs = []
        for req in requirements:
            req_text = getattr(req, 'text', '').lower()
            if any(keyword in req_text for keyword in integration_keywords):
                integration_reqs.append(req)
        
        if len(integration_reqs) > 5:
            insights.append(f"Integration Complexity: {len(integration_reqs)} integration requirements identified. Plan for system integration testing and compatibility validation.")
        
        return insights[:10]  # Return top 10 insights
    
    async def _generate_consolidated_insights(self, results: List[Any]) -> Dict[str, Any]:
        """Generate consolidated insights across multiple documents"""
        consolidated = {
            "document_summary": {
                "total_documents": len(results),
                "total_pages": sum(getattr(doc, 'total_pages', 0) for doc in results),
                "total_sections": sum(len(getattr(doc, 'sections', [])) for doc in results),
                "total_requirements": sum(len(getattr(doc, 'requirements', [])) for doc in results)
            },
            "cross_document_patterns": [],
            "common_themes": [],
            "conflicting_requirements": [],
            "coverage_gaps": [],
            "priority_recommendations": []
        }
        
        # Identify common themes across documents
        all_requirements = []
        for doc in results:
            all_requirements.extend(getattr(doc, 'requirements', []))
        
        # Group requirements by category
        categories = {}
        for req in all_requirements:
            category = getattr(req, 'category', 'General')
            if category not in categories:
                categories[category] = []
            categories[category].append(req)
        
        # Identify dominant categories
        for category, reqs in categories.items():
            if len(reqs) > 5:
                consolidated["common_themes"].append({
                    "theme": category,
                    "frequency": len(reqs),
                    "documents_affected": len(set(getattr(req, 'document_id', '') for req in reqs if hasattr(req, 'document_id')))
                })
        
        # Priority recommendations based on analysis
        total_critical = sum(1 for req in all_requirements if getattr(req, 'priority', '') == 'Critical')
        if total_critical > 15:
            consolidated["priority_recommendations"].append({
                "recommendation": "Establish Critical Requirements Review Board",
                "rationale": f"{total_critical} critical requirements identified across documents",
                "priority": "High"
            })
        
        return consolidated
    
    def _create_navigation_hub(self, results: List[Any]) -> Dict[str, Any]:
        """Create unified navigation hub for all processed documents"""
        navigation_hub = {
            "document_index": [],
            "unified_toc": [],
            "requirement_index": [],
            "deadline_calendar": [],
            "compliance_dashboard": {},
            "search_index": {}
        }
        
        # Build document index
        for doc in results:
            doc_entry = {
                "document_id": getattr(doc, 'document_id', ''),
                "filename": getattr(doc, 'filename', ''),
                "pages": getattr(doc, 'total_pages', 0),
                "sections": len(getattr(doc, 'sections', [])),
                "requirements": len(getattr(doc, 'requirements', [])),
                "processing_time": getattr(doc, 'processing_time', 0),
                "confidence": getattr(doc, 'overall_confidence', 0)
            }
            navigation_hub["document_index"].append(doc_entry)
        
        # Build unified table of contents
        for doc in results:
            doc_sections = getattr(doc, 'sections', [])
            for section in doc_sections:
                toc_entry = {
                    "document_id": getattr(doc, 'document_id', ''),
                    "section_id": getattr(section, 'id', ''),
                    "title": getattr(section, 'title', ''),
                    "section_type": getattr(section, 'section_type', ''),
                    "page_start": getattr(section, 'page_start', 1),
                    "requirements_count": getattr(section, 'requirements_count', 0)
                }
                navigation_hub["unified_toc"].append(toc_entry)
        
        return navigation_hub
    
    def _create_actionable_dashboard(self, results: List[Any]) -> Dict[str, Any]:
        """Create actionable dashboard with key metrics and next steps"""
        dashboard = {
            "key_metrics": {
                "documents_processed": len(results),
                "avg_processing_time": sum(getattr(doc, 'processing_time', 0) for doc in results) / max(1, len(results)),
                "total_requirements": sum(len(getattr(doc, 'requirements', [])) for doc in results),
                "critical_requirements": 0,
                "compliance_items": 0,
                "upcoming_deadlines": 0
            },
            "action_items": [],
            "risk_alerts": [],
            "next_steps": [],
            "quick_actions": []
        }
        
        # Calculate key metrics
        all_requirements = []
        all_deadlines = []
        
        for doc in results:
            requirements = getattr(doc, 'requirements', [])
            deadlines = getattr(doc, 'deadlines', [])
            
            all_requirements.extend(requirements)
            all_deadlines.extend(deadlines)
        
        dashboard["key_metrics"]["critical_requirements"] = sum(
            1 for req in all_requirements if getattr(req, 'priority', '') == 'Critical'
        )
        
        dashboard["key_metrics"]["compliance_items"] = sum(
            1 for req in all_requirements if getattr(req, 'compliance_type', '') == 'Mandatory'
        )
        
        dashboard["key_metrics"]["upcoming_deadlines"] = sum(
            1 for deadline in all_deadlines if deadline.get('days_remaining', 100) <= 30
        )
        
        # Generate action items
        if dashboard["key_metrics"]["critical_requirements"] > 5:
            dashboard["action_items"].append({
                "priority": "High",
                "action": "Review Critical Requirements",
                "description": f"Review and validate {dashboard['key_metrics']['critical_requirements']} critical requirements",
                "timeline": "Within 3 days"
            })
        
        if dashboard["key_metrics"]["upcoming_deadlines"] > 0:
            dashboard["action_items"].append({
                "priority": "High",
                "action": "Deadline Planning",
                "description": f"Address {dashboard['key_metrics']['upcoming_deadlines']} upcoming deadlines",
                "timeline": "Immediate"
            })
        
        # Generate next steps
        dashboard["next_steps"] = [
            "Review extracted requirements for accuracy and completeness",
            "Validate section classifications and content organization",
            "Assess technical feasibility of identified requirements",
            "Develop compliance verification plan",
            "Create detailed project timeline based on identified deadlines"
        ]
        
        return dashboard