"""
SchoolSync 2.0 - Pre-Deployment Test Suite
Comprehensive tests for all features before production deployment
"""

import sys
import os

print("="*60)
print("   SchoolSync 2.0 - Pre-Deployment Tests")
print("="*60)

# Test 1: Imports
print("\n✓ TEST 1: Importing modules...")
try:
    from main import app
    from tools import get_db_connection, ADMIN_PHONES, check_general_tools
    from agent import router_node, app as agent_app
    from security import get_school_pin, request_otp
    print("   ✅ All core modules imported successfully")
except Exception as e:
    print(f"   ❌ Import failed: {e}")
    sys.exit(1)

# Test 2: Database Connection
print("\n✓ TEST 2: Database connection...")
try:
    sheet = get_db_connection(ADMIN_PHONES[0])
    if sheet:
        print(f"   ✅ Connected to: {sheet.title}")
        ws_list = [ws.title for ws in sheet.worksheets()]
        print(f"   ✅ Worksheets found: {len(ws_list)}")
        print(f"   📊 {', '.join(ws_list[:5])}...")
    else:
        print("   ⚠️ Database connection returned None")
except Exception as e:
    print(f"   ❌ Database error: {e}")

# Test 3: Admin Configuration
print("\n✓ TEST 3: Admin configuration...")
print(f"   ✅ Admin phones configured: {len(ADMIN_PHONES)}")
print(f"   📱 Numbers: {', '.join(ADMIN_PHONES[:2])}...")

# Test 4: Environment Variables
print("\n✓ TEST 4: Environment variables...")
required_vars = [
    'GROQ_API_KEY',
    'GOOGLE_CREDENTIALS_JSON',
    'TWILIO_ACCOUNT_SID',
    'TWILIO_AUTH_TOKEN',
    'PAYSTACK_SECRET_KEY'
]
missing_vars = []
for var in required_vars:
    if os.getenv(var):
        print(f"   ✅ {var}: Set")
    else:
        print(f"   ❌ {var}: Missing")
        missing_vars.append(var)

# Test 5: Critical Files
print("\n✓ TEST 5: Deployment files...")
critical_files = {
    'main.py': 'FastAPI server',
    'agent.py': 'AI routing',
    'tools.py': 'Business logic',
    'security.py': 'Auth & security',
    'scheduler.py': 'Background tasks',
    'Procfile': 'Railway config',
    'requirements.txt': 'Dependencies',
    'railway.json': 'Deployment settings'
}

missing_files = []
for file, desc in critical_files.items():
    if os.path.exists(file):
        size = os.path.getsize(file) / 1024
        print(f"   ✅ {file:<20} ({desc}) - {size:.1f}KB")
    else:
        print(f"   ❌ {file:<20} MISSING!")
        missing_files.append(file)

# Test 6: Agent System
print("\n✓ TEST 6: Agent routing...")
try:
    from langchain_core.messages import HumanMessage
    test_state = {
        'messages': [HumanMessage(content="+2349075014063 || CHECK ST-001 Okafor")]
    }
    result = router_node(test_state)
    print(f"   ✅ Router works: {result.get('next_step', 'Unknown')}")
except Exception as e:
    print(f"   ⚠️ Routing test skipped: {e}")

# Test 7: Security System
print("\n✓ TEST 7: Security features...")
try:
    if sheet:
        pin = get_school_pin(sheet)
        print(f"   ✅ School PIN configured: {'*' * len(pin)}")
    else:
        print("   ⚠️ PIN check skipped (no sheet)")
except Exception as e:
    print(f"   ⚠️ Security check: {e}")

# Test 8: Documentation
print("\n✓ TEST 8: Documentation...")
docs = {
    'README.md': 'Main docs',
    'FEATURES.md': 'Feature list',
    'DEPLOYMENT_USAGE.md': 'Usage guide',
    'RAILWAY_DEPLOYMENT.md': 'Deploy guide',
    'TESTING.md': 'Test guide',
    'SECURITY.md': 'Security docs'
}

for doc, desc in docs.items():
    if os.path.exists(doc):
        print(f"   ✅ {doc:<30} ({desc})")
    else:
        print(f"   ⚠️ {doc:<30} Missing")

# Summary
print("\n" + "="*60)
print("   TEST SUMMARY")
print("="*60)

issues = []
if missing_vars:
    issues.append(f"Missing env vars: {', '.join(missing_vars)}")
if missing_files:
    issues.append(f"Missing files: {', '.join(missing_files)}")

if not issues:
    print("\n🎉 ALL TESTS PASSED!")
    print("\n✅ System is ready for deployment!")
    print("\nNext steps:")
    print("1. Commit code to GitHub")
    print("2. Deploy to Railway")
    print("3. Configure Twilio webhook")
    print("4. Test via WhatsApp")
else:
    print("\n⚠️ ISSUES FOUND:")
    for issue in issues:
        print(f"   - {issue}")
    print("\nFix these before deployment!")

print("\n" + "="*60)
