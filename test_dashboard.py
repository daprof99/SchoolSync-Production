# Quick Dashboard Test
# Run this to verify dashboard works

import sys
sys.path.insert(0, 'c:\\Users\\HP\\Documents\\RAIN\\SchoolSyncv2')

try:
    print("Testing dashboard...")
    print("1. Testing imports...")
    from dashboard_app import app, get_dashboard_stats
    
    print("2. Testing stats function...")
    stats = get_dashboard_stats()
    print(f"   Revenue: ₦{stats['total_revenue']:,}")
    print(f"   Outstanding: ₦{stats['total_outstanding']:,}")
    print(f"   Debtors: {stats['total_debtors']}")
    print(f"   Students: {stats['total_students']}")
    
    print("\n✅ Dashboard code works!")
    print("\n💡 To access dashboard:")
    print("   1. Make sure dashboard_app.py is running")
    print("   2. Open browser to: http://127.0.0.1:5000")
    print("   3. Or try: http://192.168.0.179:5000")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
