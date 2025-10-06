# Document Generation Enhancement Configuration

## Quality Enhancement Settings
ENABLE_CONTENT_QUALITY_CONTROLLER = True
ENABLE_BUSINESS_INTELLIGENCE = True  
ENABLE_ADVANCED_FORMATTING = True

## Content Quality Standards
MIN_PARAGRAPH_WORDS = 150
MAX_PARAGRAPH_WORDS = 225
REQUIRED_BUSINESS_ELEMENTS = [
    "ROI", "business_value", "competitive_advantage",
    "risk_mitigation", "success_metrics", "implementation"
]

## Document Structure Enhancements
INCLUDE_EXECUTIVE_SUMMARY = True
INCLUDE_COMPETITIVE_ANALYSIS = True
INCLUDE_RISK_MATRIX = True
INCLUDE_IMPLEMENTATION_TIMELINE = True

## Business Intelligence Features
QUANTIFIED_BENEFITS_REQUIRED = True
INDUSTRY_BENCHMARKS_INCLUDED = True
COMPETITIVE_POSITIONING_ENHANCED = True
FORTUNE_500_QUALITY_TARGET = True

## Model Preferences for Enhanced Generation
PREFERRED_MODEL_FOR_BUSINESS_CONTENT = "claude-3-5-sonnet-20241022"
FALLBACK_MODEL = "gpt-4o-mini"

## Enhancement Levels
# BASIC = Standard generation
# ENHANCED = Business-focused with metrics  
# ADVANCED = Strategic with competitive analysis
# EXECUTIVE = Decision-ready with ROI justification
DEFAULT_ENHANCEMENT_LEVEL = "EXECUTIVE"

## Quality Validation
VALIDATE_BUSINESS_CONTENT = True
MINIMUM_QUALITY_SCORE = 75
AUTO_ENHANCEMENT_ENABLED = True

## Document Formatting
PROFESSIONAL_FORMATTING = True
BUSINESS_STYLE_TEMPLATES = True
EVALUATION_READY_STRUCTURE = True