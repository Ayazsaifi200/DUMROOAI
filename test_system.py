"""
Test script to verify all components work correctly
"""
import sys
sys.path.append('.')

def test_imports():
    """Test all imports"""
    try:
        print("Testing imports...")
        from src.rbac import rbac
        print("✅ RBAC imported successfully")
        
        from src.data_manager import data_manager
        print("✅ Data manager imported successfully")
        
        from src.query_processor import query_processor
        print("✅ Query processor imported successfully")
        
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_rbac():
    """Test RBAC functionality"""
    try:
        print("\nTesting RBAC...")
        from src.rbac import rbac
        
        # Test authentication
        user = rbac.authenticate_user("super_admin", "admin123")
        if user:
            print("✅ Super admin authentication successful")
        else:
            print("❌ Super admin authentication failed")
            return False
        
        # Test permissions
        permissions = rbac.get_user_permissions("north_admin")
        if permissions and permissions.regions == ["North"]:
            print("✅ Permission filtering working")
        else:
            print("❌ Permission filtering failed")
            return False
        
        return True
    except Exception as e:
        print(f"❌ RBAC test error: {e}")
        return False

def test_query_processor():
    """Test query processing"""
    try:
        print("\nTesting Query Processor...")
        from src.query_processor import query_processor
        
        # Test English query
        result = query_processor.process_query("Which students haven't submitted homework?")
        if result['status'] == 'success':
            print("✅ English query processing successful")
        else:
            print("❌ English query processing failed")
            return False
        
        # Test Hindi query
        result = query_processor.process_query("Kaunse students ne homework submit nahi kiya?")
        if result['status'] == 'success':
            print("✅ Hindi query processing successful")
        else:
            print("❌ Hindi query processing failed")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Query processor test error: {e}")
        return False

def test_data_manager():
    """Test data management"""
    try:
        print("\nTesting Data Manager...")
        from src.data_manager import data_manager
        
        # Test dashboard data
        dashboard = data_manager.get_dashboard_data("super_admin")
        if dashboard['status'] == 'success':
            print("✅ Dashboard data retrieval successful")
        else:
            print("❌ Dashboard data retrieval failed")
            return False
        
        # Test query execution
        result = data_manager.execute_query("super_admin", "Show me all students")
        if result['status'] == 'success':
            print("✅ Query execution successful")
        else:
            print("❌ Query execution failed")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Data manager test error: {e}")
        return False

def test_role_based_filtering():
    """Test role-based data filtering"""
    try:
        print("\nTesting Role-Based Filtering...")
        from src.data_manager import data_manager
        
        # Test with different users
        super_result = data_manager.execute_query("super_admin", "Show all students")
        north_result = data_manager.execute_query("north_admin", "Show all students")
        
        if (super_result['status'] == 'success' and north_result['status'] == 'success'):
            super_count = super_result['total_records']
            north_count = north_result['total_records']
            
            if super_count > north_count:
                print(f"✅ Role-based filtering working (Super: {super_count}, North: {north_count})")
            else:
                print("❌ Role-based filtering not working properly")
                return False
        else:
            print("❌ Role-based filtering test failed")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Role-based filtering test error: {e}")
        return False

def main():
    """Run all tests"""
    print("=== DUMROO AI SYSTEM TESTS ===\n")
    
    tests = [
        test_imports,
        test_rbac,
        test_query_processor,
        test_data_manager,
        test_role_based_filtering
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=== TEST SUMMARY ===")
    print(f"Passed: {passed}/{total}")
    print(f"Success Rate: {passed/total*100:.1f}%")
    
    if passed == total:
        print("🎉 All tests passed! System is ready to use.")
        print("\nTo start the application, run:")
        print("streamlit run app.py")
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    main()