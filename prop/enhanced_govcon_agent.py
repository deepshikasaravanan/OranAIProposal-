"""
Enhanced AI GovCon Agent - Advanced PDF Processing and Analysis
Turns 200+ page PDFs into navigable sections, distilled requirements, and actionable guidance
"""

import os
import json
import asyncio
from typing import List, Dict, Optional, Any, Union
from dataclasses import dataclass
from pathlib import Path
import re
from datetime import datetime, timedelta

# PDF processing imports
try:
    import PyPDF2
    import pdfplumber
    from PIL import Image
    import fitz  # PyMuPDF
    HAS_PDF_LIBS = True
except ImportError:
    HAS_PDF_LIBS = False

# NLP and ML imports
try:
    import spacy
    from transformers import pipeline, AutoTokenizer, AutoModel
    import torch
    HAS_ML_LIBS = True
except ImportError:
    HAS_ML_LIBS = False

# Import extensions
from .govcon_extensions import GovConAgentExtensions
from .rag_system import rag_system, RAGProposalGenerator

@dataclass
class DocumentSection:
    """Represents a document section with metadata"""
    id: str
    title: str
    page_start: int
    page_end: int
    content: str
    subsections: List[str]
    requirements_count: int
    key_points: List[str]
    section_type: str  # 'introduction', 'technical', 'management', 'pricing', etc.
    confidence_score: float

@dataclass
class Requirement:
    """Represents an extracted requirement"""
    id: str
    text: str
    priority: str  # 'Critical', 'High', 'Medium', 'Low'
    category: str  # 'Technical', 'Management', 'Compliance', 'Performance'
    section_reference: str
    page_number: int
    is_shall_statement: bool
    compliance_type: str  # 'Mandatory', 'Desirable', 'Optional'
    verification_method: str
    associated_risks: List[str]

@dataclass
class DocumentAnalysis:
    """Complete document analysis results"""
    document_id: str
    filename: str
    total_pages: int
    processing_time: float
    sections: List[DocumentSection]
    requirements: List[Requirement]
    deadlines: List[Dict[str, Any]]
    compliance_matrix: Dict[str, Any]
    navigation_structure: Dict[str, Any]
    risk_assessment: Dict[str, Any]
    actionable_insights: List[str]
    overall_confidence: float

class EnhancedGovConAgent(GovConAgentExtensions):
    """Enhanced AI GovCon Agent with advanced document processing and RAG capabilities"""
    
    def __init__(self):
        self.processed_documents = {}
        self.document_cache = {}
        self.analysis_history = []
        
        # Initialize RAG system
        try:
            from .rag_system import rag_system, RAGProposalGenerator
            self.rag_system = rag_system
            self.rag_generator = RAGProposalGenerator(rag_system)
            self.has_rag = True
            print("✅ RAG system initialized successfully")
        except Exception as e:
            print(f"⚠️ RAG system initialization failed: {e}")
            self.rag_system = None
            self.rag_generator = None
            self.has_rag = False
        
    def initialize_models(self):
        """Initialize AI models for document processing"""
        if HAS_ML_LIBS:
            try:
                # Load spaCy model for NLP
                self.nlp = spacy.load("en_core_web_sm")
            except:
                self.nlp = None
                
            try:
                # Initialize transformer models for requirement extraction
                self.requirement_classifier = pipeline(
                    "text-classification",
                    model="distilbert-base-uncased",
                    device=0 if torch.cuda.is_available() else -1
                )
                self.summarizer = pipeline(
                    "summarization",
                    model="facebook/bart-large-cnn",
                    device=0 if torch.cuda.is_available() else -1
                )
            except:
                self.requirement_classifier = None
                self.summarizer = None
        else:
            self.nlp = None
            self.requirement_classifier = None
            self.summarizer = None
    
    def _load_processing_templates(self) -> Dict[str, Any]:
        """Load document processing templates and patterns"""
        return {
            "section_patterns": {
                "introduction": [r"1\.0?\s+introduction", r"background", r"overview"],
                "technical": [r"2\.0?\s+technical", r"system\s+requirements", r"specifications"],
                "management": [r"3\.0?\s+management", r"project\s+management", r"program\s+management"],
                "past_performance": [r"4\.0?\s+past\s+performance", r"experience", r"qualifications"],
                "pricing": [r"5\.0?\s+pricing", r"cost", r"budget", r"financial"],
                "compliance": [r"compliance", r"regulatory", r"standards"]
            },
            "requirement_indicators": [
                r"\bshall\b", r"\bmust\b", r"\brequired\b", r"\bmandatory\b",
                r"\bwill\b", r"\bneeds?\s+to\b", r"\bis\s+required\b"
            ],
            "deadline_patterns": [
                r"due\s+(?:on\s+|by\s+)?(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})",
                r"deadline\s*:?\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})",
                r"submit(?:ted)?\s+(?:by\s+|on\s+)?(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})"
            ],
            "priority_keywords": {
                "critical": ["critical", "essential", "mandatory", "required"],
                "high": ["important", "significant", "key", "primary"],
                "medium": ["should", "recommended", "preferred"],
                "low": ["may", "optional", "if applicable", "where possible"]
            }
        }
    
    async def process_documents(self, files: List[Any], analysis_type: str = "full", output_format: str = "interactive") -> Dict[str, Any]:
        """Main document processing function"""
        start_time = datetime.now()
        
        if not HAS_PDF_LIBS:
            return await self._fallback_processing(files, analysis_type)
        
        try:
            results = []
            total_pages = 0
            total_requirements = 0
            
            for file in files:
                doc_analysis = await self._process_single_document(file, analysis_type)
                results.append(doc_analysis)
                total_pages += doc_analysis.total_pages
                total_requirements += len(doc_analysis.requirements)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Generate comprehensive results
            comprehensive_results = {
                "status": "success",
                "processing_time": processing_time,
                "documents_processed": len(files),
                "total_pages_analyzed": total_pages,
                "total_requirements_extracted": total_requirements,
                "analysis_type": analysis_type,
                "output_format": output_format,
                "documents": [self._serialize_analysis(doc) for doc in results],
                "consolidated_insights": await self._generate_consolidated_insights(results),
                "navigation_hub": self._create_navigation_hub(results),
                "actionable_dashboard": self._create_actionable_dashboard(results)
            }
            
            return comprehensive_results
            
        except Exception as e:
            return {
                "status": "error",
                "error_message": str(e),
                "fallback_results": await self._fallback_processing(files, analysis_type)
            }
    
    async def _process_single_document(self, file: Any, analysis_type: str) -> DocumentAnalysis:
        """Process a single PDF document with full analysis"""
        start_time = datetime.now()
        
        # Extract text and metadata from PDF
        pdf_content = await self._extract_pdf_content(file)
        
        # Analyze document structure
        sections = await self._extract_sections(pdf_content, analysis_type)
        
        # Extract requirements
        requirements = await self._extract_requirements(pdf_content, sections)
        
        # Extract deadlines and dates
        deadlines = await self._extract_deadlines(pdf_content)
        
        # Create compliance matrix
        compliance_matrix = await self._create_compliance_matrix(requirements, sections)
        
        # Generate navigation structure
        navigation_structure = self._create_navigation_structure(sections)
        
        # Assess risks
        risk_assessment = await self._assess_document_risks(requirements, sections)
        
        # Generate actionable insights
        actionable_insights = await self._generate_actionable_insights(sections, requirements, deadlines)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return DocumentAnalysis(
            document_id=self._generate_document_id(file),
            filename=getattr(file, 'filename', 'unknown.pdf'),
            total_pages=pdf_content.get('total_pages', 0),
            processing_time=processing_time,
            sections=sections,
            requirements=requirements,
            deadlines=deadlines,
            compliance_matrix=compliance_matrix,
            navigation_structure=navigation_structure,
            risk_assessment=risk_assessment,
            actionable_insights=actionable_insights,
            overall_confidence=self._calculate_confidence_score(sections, requirements)
        )
    
    async def _extract_pdf_content(self, file: Any) -> Dict[str, Any]:
        """Extract content from PDF using multiple methods"""
        content = {
            "text": "",
            "pages": [],
            "total_pages": 0,
            "metadata": {},
            "images": [],
            "tables": []
        }
        
        try:
            # Method 1: Try pdfplumber for better table extraction
            if hasattr(file, 'read'):
                file_content = await file.read() if hasattr(file.read, '__await__') else file.read()
            else:
                with open(file, 'rb') as f:
                    file_content = f.read()
            
            # Use PyMuPDF for comprehensive extraction
            doc = fitz.open(stream=file_content, filetype="pdf")
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                page_text = page.get_text()
                
                content["pages"].append({
                    "page_number": page_num + 1,
                    "text": page_text,
                    "images": len(page.get_images()),
                    "tables": self._extract_tables_from_page(page)
                })
                
                content["text"] += f"\n--- Page {page_num + 1} ---\n{page_text}\n"
            
            content["total_pages"] = len(doc)
            content["metadata"] = doc.metadata
            doc.close()
            
            return content
            
        except Exception as e:
            # Fallback to basic text extraction
            return {
                "text": f"Error extracting PDF content: {str(e)}",
                "pages": [],
                "total_pages": 0,
                "metadata": {},
                "images": [],
                "tables": []
            }
    
    def _extract_tables_from_page(self, page) -> List[Dict[str, Any]]:
        """Extract tables from a PDF page"""
        tables = []
        try:
            # Use pdfplumber-like logic for table detection
            # This is a simplified version - in production, use pdfplumber
            tables_found = page.find_tables()
            for i, table in enumerate(tables_found):
                tables.append({
                    "table_id": i + 1,
                    "rows": len(table.extract()) if table.extract() else 0,
                    "columns": len(table.extract()[0]) if table.extract() and table.extract()[0] else 0
                })
        except:
            pass
        return tables
    
    async def _extract_sections(self, pdf_content: Dict[str, Any], analysis_type: str) -> List[DocumentSection]:
        """Extract document sections with intelligent parsing"""
        sections = []
        text = pdf_content["text"]
        pages = pdf_content["pages"]
        
        # Find section headers using patterns
        section_matches = []
        for section_type, patterns in self.processing_templates["section_patterns"].items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    section_matches.append({
                        "start": match.start(),
                        "type": section_type,
                        "title": match.group(0),
                        "pattern": pattern
                    })
        
        # Sort by position in document
        section_matches.sort(key=lambda x: x["start"])
        
        # Create sections with content
        for i, match in enumerate(section_matches):
            start_pos = match["start"]
            end_pos = section_matches[i + 1]["start"] if i + 1 < len(section_matches) else len(text)
            
            section_content = text[start_pos:end_pos]
            
            # Find page range
            page_start = self._find_page_for_position(start_pos, pages)
            page_end = self._find_page_for_position(end_pos, pages)
            
            # Extract key points and subsections
            key_points = await self._extract_key_points(section_content)
            subsections = self._extract_subsections(section_content)
            requirements_count = len(re.findall(r'\bshall\b|\bmust\b|\brequired\b', section_content, re.IGNORECASE))
            
            section = DocumentSection(
                id=f"section_{i+1}",
                title=match["title"].strip(),
                page_start=page_start,
                page_end=page_end,
                content=section_content,
                subsections=subsections,
                requirements_count=requirements_count,
                key_points=key_points,
                section_type=match["type"],
                confidence_score=self._calculate_section_confidence(section_content, match["type"])
            )
            
            sections.append(section)
        
        return sections
    
    def _find_page_for_position(self, position: int, pages: List[Dict[str, Any]]) -> int:
        """Find which page a text position corresponds to"""
        current_pos = 0
        for page in pages:
            page_text_length = len(page["text"]) + 20  # Account for page headers
            if current_pos <= position < current_pos + page_text_length:
                return page["page_number"]
            current_pos += page_text_length
        return 1  # Default to page 1 if not found
    
    async def _extract_key_points(self, content: str) -> List[str]:
        """Extract key points from section content using AI"""
        if self.summarizer and len(content) > 100:
            try:
                # Chunk content if too long
                max_chunk_size = 1024
                chunks = [content[i:i+max_chunk_size] for i in range(0, len(content), max_chunk_size)]
                
                key_points = []
                for chunk in chunks[:3]:  # Limit to first 3 chunks
                    if len(chunk.strip()) > 50:
                        summary = self.summarizer(chunk, max_length=50, min_length=10, do_sample=False)
                        if summary:
                            key_points.append(summary[0]['summary_text'])
                
                return key_points
            except:
                pass
        
        # Fallback: Extract sentences with key indicators
        sentences = re.split(r'[.!?]+', content)
        key_points = []
        
        key_indicators = ['shall', 'must', 'required', 'critical', 'important', 'key', 'primary']
        
        for sentence in sentences[:10]:  # Limit to first 10 sentences
            sentence = sentence.strip()
            if len(sentence) > 20 and any(indicator in sentence.lower() for indicator in key_indicators):
                key_points.append(sentence)
        
        return key_points[:5]  # Return top 5 key points
    
    def _extract_subsections(self, content: str) -> List[str]:
        """Extract subsection titles from content"""
        # Look for numbered subsections like "2.1", "2.2.1", etc.
        subsection_pattern = r'^(\d+\.\d+(?:\.\d+)?)\s+([^\n]+)'
        matches = re.findall(subsection_pattern, content, re.MULTILINE)
        
        subsections = []
        for match in matches:
            subsection_num, subsection_title = match
            subsections.append(f"{subsection_num} {subsection_title.strip()}")
        
        return subsections[:10]  # Limit to first 10 subsections
    
    def _calculate_section_confidence(self, content: str, section_type: str) -> float:
        """Calculate confidence score for section classification"""
        base_score = 0.7
        
        # Check for type-specific keywords
        type_keywords = {
            "technical": ["system", "requirement", "specification", "architecture", "design"],
            "management": ["management", "approach", "methodology", "process", "team"],
            "pricing": ["cost", "price", "budget", "financial", "payment"],
            "compliance": ["compliance", "regulation", "standard", "requirement", "audit"]
        }
        
        if section_type in type_keywords:
            keyword_count = sum(1 for keyword in type_keywords[section_type] 
                              if keyword.lower() in content.lower())
            keyword_bonus = min(0.2, keyword_count * 0.05)
            base_score += keyword_bonus
        
        return min(1.0, base_score)
    
    async def _extract_requirements(self, pdf_content: Dict[str, Any], sections: List[DocumentSection]) -> List[Requirement]:
        """Extract requirements with advanced NLP processing"""
        requirements = []
        text = pdf_content["text"]
        pages = pdf_content["pages"]
        
        # Find requirement statements using patterns
        requirement_patterns = self.processing_templates["requirement_indicators"]
        
        for pattern in requirement_patterns:
            matches = re.finditer(f"[^.!?]*{pattern}[^.!?]*[.!?]", text, re.IGNORECASE)
            
            for i, match in enumerate(matches):
                requirement_text = match.group(0).strip()
                
                if len(requirement_text) < 20:  # Skip very short matches
                    continue
                
                # Find which section this requirement belongs to
                section_ref = self._find_requirement_section(match.start(), sections)
                page_num = self._find_page_for_position(match.start(), pages)
                
                # Classify requirement
                priority = self._classify_requirement_priority(requirement_text)
                category = self._classify_requirement_category(requirement_text)
                is_shall = bool(re.search(r'\bshall\b', requirement_text, re.IGNORECASE))
                compliance_type = self._classify_compliance_type(requirement_text)
                
                # Assess associated risks
                risks = self._identify_requirement_risks(requirement_text)
                
                requirement = Requirement(
                    id=f"REQ-{len(requirements)+1:03d}",
                    text=requirement_text,
                    priority=priority,
                    category=category,
                    section_reference=section_ref,
                    page_number=page_num,
                    is_shall_statement=is_shall,
                    compliance_type=compliance_type,
                    verification_method=self._suggest_verification_method(requirement_text, category),
                    associated_risks=risks
                )
                
                requirements.append(requirement)
        
        return requirements[:100]  # Limit to first 100 requirements
    
    def _find_requirement_section(self, position: int, sections: List[DocumentSection]) -> str:
        """Find which section a requirement belongs to"""
        for section in sections:
            # This is a simplified approach - in practice, you'd need more sophisticated position tracking
            if section.id:
                return section.id
        return "unknown_section"
    
    def _classify_requirement_priority(self, text: str) -> str:
        """Classify requirement priority based on keywords"""
        text_lower = text.lower()
        
        for priority, keywords in self.processing_templates["priority_keywords"].items():
            if any(keyword in text_lower for keyword in keywords):
                return priority.title()
        
        # Default priority based on requirement type
        if re.search(r'\bshall\b|\bmust\b', text_lower):
            return "High"
        elif re.search(r'\bshould\b|\brecommended\b', text_lower):
            return "Medium"
        else:
            return "Low"
    
    def _classify_requirement_category(self, text: str) -> str:
        """Classify requirement category"""
        text_lower = text.lower()
        
        categories = {
            "Technical": ["system", "software", "hardware", "performance", "interface", "api"],
            "Management": ["management", "process", "methodology", "reporting", "documentation"],
            "Compliance": ["compliance", "regulation", "standard", "audit", "certification"],
            "Security": ["security", "access", "authentication", "encryption", "privacy"],
            "Performance": ["performance", "speed", "throughput", "latency", "availability"]
        }
        
        for category, keywords in categories.items():
            if any(keyword in text_lower for keyword in keywords):
                return category
        
        return "General"
    
    def _classify_compliance_type(self, text: str) -> str:
        """Classify compliance type"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["shall", "must", "required", "mandatory"]):
            return "Mandatory"
        elif any(word in text_lower for word in ["should", "recommended", "preferred"]):
            return "Desirable"  
        else:
            return "Optional"
    
    def _suggest_verification_method(self, text: str, category: str) -> str:
        """Suggest verification method for requirement"""
        text_lower = text.lower()
        
        if "test" in text_lower or "testing" in text_lower:
            return "Testing"
        elif "demonstrate" in text_lower or "demonstration" in text_lower:
            return "Demonstration"
        elif "document" in text_lower or "documentation" in text_lower:
            return "Documentation"
        elif category == "Technical":
            return "Testing"
        elif category == "Management":
            return "Documentation"
        elif category == "Compliance":
            return "Audit"
        else:
            return "Review"
    
    def _identify_requirement_risks(self, text: str) -> List[str]:
        """Identify potential risks associated with requirement"""
        risks = []
        text_lower = text.lower()
        
        risk_indicators = {
            "Technical complexity": ["complex", "advanced", "sophisticated", "cutting-edge"],
            "Timeline risk": ["immediate", "urgent", "asap", "quickly", "short", "tight"],
            "Resource intensive": ["extensive", "large-scale", "comprehensive", "full"],
            "Integration challenge": ["integrate", "interface", "connect", "interoperate"],
            "Compliance risk": ["audit", "certify", "approve", "compliance", "regulation"]
        }
        
        for risk_type, indicators in risk_indicators.items():
            if any(indicator in text_lower for indicator in indicators):
                risks.append(risk_type)
        
        return risks
    
    async def _extract_deadlines(self, pdf_content: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract deadlines and important dates"""
        deadlines = []
        text = pdf_content["text"]
        
        # Common deadline patterns
        patterns = self.processing_templates["deadline_patterns"]
        
        deadline_types = {
            "proposal due": ["proposal due", "submission deadline", "response due"],
            "question period": ["question period", "questions due", "inquiry deadline"],
            "site visit": ["site visit", "facility tour", "location visit"],
            "award date": ["award date", "selection date", "contract award"]
        }
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                date_str = match.group(1)
                
                # Try to parse the date
                try:
                    # This is a simplified date parser
                    deadline_date = self._parse_date_string(date_str)
                    if deadline_date:
                        days_remaining = (deadline_date - datetime.now()).days
                        
                        # Determine deadline type
                        context = text[max(0, match.start()-100):match.end()+100].lower()
                        deadline_type = "general"
                        
                        for dtype, keywords in deadline_types.items():
                            if any(keyword in context for keyword in keywords):
                                deadline_type = dtype
                                break
                        
                        deadlines.append({
                            "type": deadline_type,
                            "date": deadline_date.strftime("%Y-%m-%d"),
                            "date_string": date_str,
                            "days_remaining": days_remaining,
                            "status": "upcoming" if days_remaining > 0 else "passed",
                            "context": match.group(0),
                            "urgency": "high" if days_remaining <= 7 else "medium" if days_remaining <= 30 else "low"
                        })
                except:
                    continue
        
        # Sort by date
        deadlines.sort(key=lambda x: x["date"])
        
        return deadlines[:10]  # Return first 10 deadlines
    
    def _parse_date_string(self, date_str: str) -> Optional[datetime]:
        """Parse various date string formats"""
        date_formats = ["%m/%d/%Y", "%m-%d-%Y", "%m/%d/%y", "%m-%d-%y"]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt)
            except:
                continue
        
        return None
    
    def _generate_document_id(self, file: Any) -> str:
        """Generate unique document ID"""
        import hashlib
        filename = getattr(file, 'filename', 'unknown.pdf')
        timestamp = datetime.now().isoformat()
        return hashlib.md5(f"{filename}_{timestamp}".encode()).hexdigest()[:12]
    
    def _calculate_confidence_score(self, sections: List[DocumentSection], requirements: List[Requirement]) -> float:
        """Calculate overall document processing confidence"""
        if not sections:
            return 0.0
        
        section_confidence = sum(section.confidence_score for section in sections) / len(sections)
        requirements_factor = min(1.0, len(requirements) / 50)  # Normalize to 50 requirements
        
        return (section_confidence * 0.7) + (requirements_factor * 0.3)
    
    async def _fallback_processing(self, files: List[Any], analysis_type: str) -> Dict[str, Any]:
        """Fallback processing when PDF libraries are not available"""
        return {
            "status": "limited_functionality",
            "message": "PDF processing libraries not available. Install: pip install PyPDF2 pdfplumber PyMuPDF",
            "documents_processed": len(files),
            "analysis_type": analysis_type,
            "mock_results": {
                "sections": [
                    {"title": "Section 1: Introduction", "page": 1, "requirements": 5},
                    {"title": "Section 2: Technical Requirements", "page": 15, "requirements": 23},
                    {"title": "Section 3: Management Approach", "page": 45, "requirements": 12}
                ],
                "requirements": [
                    {"id": "REQ-001", "text": "System shall support 10,000 concurrent users", "priority": "High"},
                    {"id": "REQ-002", "text": "Solution must be cloud-native", "priority": "High"}
                ],
                "deadlines": [
                    {"event": "Proposal Due", "date": "2024-12-01", "days_remaining": 60}
                ]
            }
        }
    
    def _serialize_analysis(self, analysis: DocumentAnalysis) -> Dict[str, Any]:
        """Convert DocumentAnalysis to serializable dictionary"""
        return {
            "document_id": analysis.document_id,
            "filename": analysis.filename,
            "total_pages": analysis.total_pages,
            "processing_time": analysis.processing_time,
            "sections": [
                {
                    "id": section.id,
                    "title": section.title,
                    "page_start": section.page_start,
                    "page_end": section.page_end,
                    "subsections": section.subsections,
                    "requirements_count": section.requirements_count,
                    "key_points": section.key_points,
                    "section_type": section.section_type,
                    "confidence_score": section.confidence_score
                }
                for section in analysis.sections
            ],
            "requirements": [
                {
                    "id": req.id,
                    "text": req.text,
                    "priority": req.priority,
                    "category": req.category,
                    "section_reference": req.section_reference,
                    "page_number": req.page_number,
                    "is_shall_statement": req.is_shall_statement,
                    "compliance_type": req.compliance_type,
                    "verification_method": req.verification_method,
                    "associated_risks": req.associated_risks
                }
                for req in analysis.requirements
            ],
            "deadlines": analysis.deadlines,
            "compliance_matrix": analysis.compliance_matrix,
            "navigation_structure": analysis.navigation_structure,
            "risk_assessment": analysis.risk_assessment,
            "actionable_insights": analysis.actionable_insights,
            "overall_confidence": analysis.overall_confidence
        }

    # RAG-Enhanced Proposal Generation Methods
    async def search_knowledge_base(self, query: str, search_type: str = "hybrid", top_k: int = 5) -> Dict[str, Any]:
        """Search the RAG knowledge base for relevant information"""
        if not self.has_rag:
            return {
                "error": "RAG system not available",
                "results": [],
                "search_performed": False
            }
        
        try:
            search_results = self.rag_system.search(query, top_k=top_k, search_type=search_type)
            
            return {
                "query": query,
                "search_type": search_type,
                "results_found": len(search_results),
                "search_performed": True,
                "results": [
                    {
                        "content": result.chunk.content,
                        "source_file": result.chunk.source_file,
                        "relevance_score": result.relevance_score,
                        "context_snippet": result.context_snippet,
                        "section": result.chunk.section,
                        "keywords": result.chunk.keywords
                    }
                    for result in search_results
                ]
            }
        except Exception as e:
            return {
                "error": f"Search failed: {str(e)}",
                "results": [],
                "search_performed": False
            }
    
    async def generate_proposal_section_with_rag(self, section_title: str, requirements: List[str], 
                                                query: str = None) -> Dict[str, Any]:
        """Generate proposal section using RAG context"""
        if not self.has_rag:
            return {
                "error": "RAG system not available",
                "section_title": section_title,
                "generation_ready": False
            }
        
        try:
            # Use section title as query if no specific query provided
            search_query = query or f"{section_title} {' '.join(requirements[:3])}"
            
            # Generate section with RAG context
            rag_result = self.rag_generator.generate_section_with_context(
                section_title=section_title,
                requirements=requirements,
                query=search_query
            )
            
            # Add search results for transparency
            search_results = await self.search_knowledge_base(search_query, top_k=5)
            rag_result["search_results"] = search_results
            
            return rag_result
            
        except Exception as e:
            return {
                "error": f"RAG generation failed: {str(e)}",
                "section_title": section_title,
                "generation_ready": False
            }
    
    async def add_document_to_knowledge_base(self, file_path: str, content: str, 
                                           metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Add a document to the RAG knowledge base"""
        if not self.has_rag:
            return {
                "error": "RAG system not available",
                "chunks_added": 0,
                "success": False
            }
        
        try:
            chunk_ids = self.rag_system.add_document(file_path, content, metadata)
            
            return {
                "file_path": file_path,
                "chunks_added": len(chunk_ids),
                "chunk_ids": chunk_ids,
                "success": True,
                "message": f"Successfully added {len(chunk_ids)} chunks to knowledge base"
            }
            
        except Exception as e:
            return {
                "error": f"Failed to add document: {str(e)}",
                "chunks_added": 0,
                "success": False
            }
    
    def get_rag_knowledge_base_stats(self) -> Dict[str, Any]:
        """Get statistics about the RAG knowledge base"""
        if not self.has_rag:
            return {
                "error": "RAG system not available",
                "stats": {}
            }
        
        try:
            chunks = self.rag_system.chunks
            
            # Calculate statistics
            total_chunks = len(chunks)
            total_content_length = sum(len(chunk.content) for chunk in chunks)
            
            # Group by source file
            sources = {}
            for chunk in chunks:
                if chunk.source_file not in sources:
                    sources[chunk.source_file] = 0
                sources[chunk.source_file] += 1
            
            # Group by section
            sections = {}
            for chunk in chunks:
                section = chunk.section or "Unknown"
                if section not in sections:
                    sections[section] = 0
                sections[section] += 1
            
            return {
                "total_chunks": total_chunks,
                "total_content_length": total_content_length,
                "average_chunk_length": total_content_length / max(1, total_chunks),
                "total_sources": len(sources),
                "sources": sources,
                "sections": sections,
                "has_embeddings": any(chunk.embedding is not None for chunk in chunks),
                "index_built": self.rag_system.index_built
            }
            
        except Exception as e:
            return {
                "error": f"Failed to get stats: {str(e)}",
                "stats": {}
            }
    
    async def initialize_knowledge_base_from_examples(self) -> Dict[str, Any]:
        """Initialize RAG knowledge base with example documents"""
        if not self.has_rag:
            return {
                "error": "RAG system not available",
                "initialized": False
            }
        
        try:
            from .rag_system import initialize_rag_knowledge_base
            initialize_rag_knowledge_base()
            
            stats = self.get_rag_knowledge_base_stats()
            
            return {
                "initialized": True,
                "message": "Knowledge base initialized with example documents",
                "stats": stats
            }
            
        except Exception as e:
            return {
                "error": f"Initialization failed: {str(e)}",
                "initialized": False
            }

# Create enhanced instance
enhanced_govcon_agent = EnhancedGovConAgent()