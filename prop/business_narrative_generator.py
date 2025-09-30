# Enhanced Business-Focused Narrative Generator

def generate_business_focused_narrative(outline_item, reqs, llm_client):
    """Generate narrative content with business analyst focus"""
    
    # Enhanced system prompt for business-focused content
    system_prompt = f"""
You are a senior proposal strategist writing for government business analysts and evaluators. 
Write compelling, evaluation-focused content that clearly demonstrates business value.

SECTION: {outline_item.title}
REQUIREMENTS: {outline_item.related_shalls}

BUSINESS ANALYST FOCUS:
- Start with quantified business benefits and ROI
- Include specific metrics and performance indicators  
- Address risk mitigation with probability/impact analysis
- Provide implementation roadmap with milestones
- Emphasize competitive differentiators and unique value

STRUCTURE EACH RESPONSE WITH:
1. Executive Summary (2-3 sentences of business value)
2. Technical Approach (how we'll execute)
3. Business Benefits (quantified value to customer)
4. Risk Assessment & Mitigation
5. Success Metrics & KPIs
6. Implementation Timeline

USE THESE ELEMENTS:
- Specific percentages, timelines, and cost savings
- Past performance with measurable results
- Industry best practices and proven methodologies
- Quality assurance and performance monitoring
- Stakeholder communication and change management

WRITING STYLE:
- Active voice with confident, professional tone
- Bullet points for complex information
- Tables/charts references where helpful
- Quantify everything possible (%, $, timeline)
- Address "so what?" for every technical feature
"""

    # Create messages for the LLM
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Write a comprehensive proposal section for: {outline_item.title}. Address these bullets: {outline_item.bullets}. Keep it professional, business-focused, and evaluation-ready. Target approximately {outline_item.page_budget} pages worth of content."}
    ]
    
    # Generate the content
    narrative = llm_client.complete(messages[1]["content"])
    
    return narrative