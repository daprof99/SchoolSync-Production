"""
Quick script to verify HELP command role differentiation
"""

from tools import ADMIN_PHONES, parse_message_metadata, check_general_tools

print("="*60)
print("   Testing Role-Based HELP Command")
print("="*60)

# Simulate admin request
admin_phone = ADMIN_PHONES[0]
admin_state = {
    'messages': [type('obj', (object,), {
        'content': f"{admin_phone} || HELP"
    })]
}

print("\n✓ TEST 1: Admin phone sends HELP")
print(f"   Phone: {admin_phone}")
admin_response = check_general_tools(admin_state)
admin_help = admin_response['messages'][0]

has_admin_section = "**For Admins:**" in admin_help
print(f"   Contains admin section: {'✅ YES' if has_admin_section else '❌ NO'}")
print(f"   Response length: {len(admin_help)} chars")

# Simulate parent request
parent_phone = "+2348189678261"
parent_state = {
    'messages': [type('obj', (object,), {
        'content': f"{parent_phone} || HELP"
    })]
}

print("\n✓ TEST 2: Parent phone sends HELP")
print(f"   Phone: {parent_phone}")
parent_response = check_general_tools(parent_state)
parent_help = parent_response['messages'][0]

has_admin_section_parent = "**For Admins:**" in parent_help
print(f"   Contains admin section: {'❌ NO (correct!)' if not has_admin_section_parent else '✅ YES (wrong!)'}")
print(f"   Response length: {len(parent_help)} chars")

# Summary
print("\n" + "="*60)
print("   SUMMARY")
print("="*60)

if has_admin_section and not has_admin_section_parent:
    print("\n✅ TEST PASSED!")
    print("   - Admins see admin commands")
    print("   - Parents see only parent commands")
elif not has_admin_section:
    print("\n❌ TEST FAILED!")
    print("   - Admin should see admin commands but doesn't")
elif has_admin_section_parent:
    print("\n❌ TEST FAILED!")
    print("   - Parent should NOT see admin commands but does")
else:
    print("\n⚠️ UNEXPECTED RESULT")

print("\n" + "="*60)
