#!/usr/bin/env python3
"""
Test script for the Enhanced AI GovCon Agent
"""

import asyncio
import aiohttp
import json
from io import BytesIO

async def test_govcon_agent():
    """Test the AI GovCon Agent endpoint"""
    url = "http://127.0.0.1:8000/api/platform/govcon-agent/process"
    
    # Create a sample PDF-like file for testing
    sample_content = b"""SECTION 1: INTRODUCTION
This is a sample government contracting document that contains requirements and specifications.

SECTION 2: TECHNICAL REQUIREMENTS
The contractor SHALL provide the following services:
- Network security monitoring
- Incident response capabilities  
- 24/7 support coverage

SECTION 3: EVALUATION CRITERIA
Proposals will be evaluated based on:
1. Technical approach (40%)
2. Past performance (30%)
3. Price (30%)

SECTION 4: SUBMISSION REQUIREMENTS
All proposals MUST include:
- Technical proposal
- Past performance references
- Cost proposal
"""
    
    # Create form data
    data = aiohttp.FormData()
    data.add_field('files', BytesIO(sample_content), filename='sample_rfp.txt', content_type='text/plain')
    data.add_field('analysis_type', 'full')
    data.add_field('output_format', 'interactive')
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data) as response:
                if response.status == 200:
                    result = await response.json()
                    print("✅ AI GovCon Agent Test PASSED!")
                    print("\n📄 Analysis Results:")
                    print(json.dumps(result, indent=2))
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ Test FAILED with status {response.status}")
                    print(f"Error: {error_text}")
                    return False
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return False

async def test_health_endpoint():
    """Test the health endpoint"""
    url = "http://127.0.0.1:8000/health"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    result = await response.json()
                    print("✅ Health Check PASSED!")
                    print(f"Status: {result}")
                    return True
                else:
                    print(f"❌ Health Check FAILED with status {response.status}")
                    return False
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return False

async def main():
    print("🚀 Testing Enhanced AI GovCon Agent Platform...\n")
    
    # Test health first
    print("1. Testing Health Endpoint...")
    health_ok = await test_health_endpoint()
    
    if health_ok:
        print("\n2. Testing AI GovCon Agent...")
        agent_ok = await test_govcon_agent()
        
        if agent_ok:
            print("\n🎉 All tests PASSED! Your AI GovCon Agent is working!")
            print("\n🌐 Web Interface Available at: http://127.0.0.1:8000")
            print("📱 Platform Capabilities at: http://127.0.0.1:8000/platform")
        else:
            print("\n⚠️  AI GovCon Agent needs attention")
    else:
        print("\n❌ Server is not responding")

if __name__ == "__main__":
    asyncio.run(main())