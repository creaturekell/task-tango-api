#!/usr/bin/env python3
"""Test script for Database connection and table creation.

This script tests:
1. Database connection
2. Table creation
3. Basic CRUD operations
"""

from sqlalchemy import inspect, text
from database import engine, Base, SessionLocal
from models import User, Todo
from datetime import datetime


def test_database_connection():
    """Test 1: Verify database connection."""
    print("=" * 60)
    print("Test 1: Database Connection")
    print("=" * 60)
    
    try:
        # Try to connect to the database
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        print("✓ Database connection successful!")
        return True
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False


def test_table_creation():
    """Test 2: Create tables and verify they exist."""
    print("\n" + "=" * 60)
    print("Test 2: Table Creation")
    print("=" * 60)
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✓ Tables created successfully!")
        
        # Verify tables exist
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        print(f"\nTables in database: {tables}")
        
        expected_tables = ["users", "todos"]
        for table in expected_tables:
            if table in tables:
                print(f"  ✓ Table '{table}' exists")
            else:
                print(f"  ✗ Table '{table}' NOT found")
                return False
        
        # Check table columns
        print("\nTable structure:")
        for table_name in expected_tables:
            columns = inspector.get_columns(table_name)
            print(f"\n{table_name}:")
            for col in columns:
                print(f"  - {col['name']}: {col['type']}")
        
        return True
    except Exception as e:
        print(f"✗ Table creation failed: {e}")
        return False


def test_basic_operations():
    """Test 3: Basic CRUD operations."""
    print("\n" + "=" * 60)
    print("Test 3: Basic CRUD Operations")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        # Create a test user
        print("\n1. Creating test user...")
        test_user = User(
            name="Test User",
            email="test@example.com",
            hashed_password="hashed_password_here"
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        print(f"   ✓ User created with ID: {test_user.id}")
        
        # Read the user
        print("\n2. Reading test user...")
        found_user = db.query(User).filter(User.email == "test@example.com").first()
        if found_user:
            print(f"   ✓ User found: {found_user.name} ({found_user.email})")
        else:
            print("   ✗ User not found")
            return False
        
        # Create a test todo
        print("\n3. Creating test todo...")
        test_todo = Todo(
            title="Test Todo",
            description="This is a test todo item",
            user_id=test_user.id
        )
        db.add(test_todo)
        db.commit()
        db.refresh(test_todo)
        print(f"   ✓ Todo created with ID: {test_todo.id}")
        
        # Read the todo
        print("\n4. Reading test todo...")
        found_todo = db.query(Todo).filter(Todo.id == test_todo.id).first()
        if found_todo:
            print(f"   ✓ Todo found: {found_todo.title}")
            print(f"   ✓ Todo belongs to user: {found_todo.owner.name}")
        else:
            print("   ✗ Todo not found")
            return False
        
        # Update the todo
        print("\n5. Updating test todo...")
        found_todo.title = "Updated Test Todo"
        db.commit()
        db.refresh(found_todo)
        print(f"   ✓ Todo updated: {found_todo.title}")
        
        # Delete the todo
        print("\n6. Deleting test todo...")
        db.delete(found_todo)
        db.commit()
        print("   ✓ Todo deleted")
        
        # Delete the user (cascade should delete todos)
        print("\n7. Deleting test user...")
        db.delete(found_user)
        db.commit()
        print("   ✓ User deleted")
        
        print("\n✓ All CRUD operations successful!")
        return True
        
    except Exception as e:
        print(f"\n✗ CRUD operations failed: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return False
    finally:
        db.close()


def test_relationships():
    """Test 4: Verify relationships work correctly."""
    print("\n" + "=" * 60)
    print("Test 4: Relationship Testing")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        # Create user with todos
        print("\n1. Creating user with multiple todos...")
        test_user = User(
            name="Relationship Test User",
            email="relationship@example.com",
            hashed_password="hashed_password"
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        
        # Create todos for the user
        todo1 = Todo(title="Todo 1", user_id=test_user.id)
        todo2 = Todo(title="Todo 2", user_id=test_user.id)
        db.add_all([todo1, todo2])
        db.commit()
        
        # Test relationship: user -> todos
        print(f"\n2. User has {len(test_user.todos)} todos:")
        for todo in test_user.todos:
            print(f"   - {todo.title}")
        
        # Test relationship: todo -> user
        print(f"\n3. Todo belongs to user: {todo1.owner.name}")
        
        # Test cascade delete
        print("\n4. Testing cascade delete...")
        db.delete(test_user)
        db.commit()
        
        # Verify todos were deleted (cascade)
        remaining_todos = db.query(Todo).filter(Todo.user_id == test_user.id).count()
        if remaining_todos == 0:
            print("   ✓ Cascade delete works - todos deleted with user")
        else:
            print(f"   ✗ Cascade delete failed - {remaining_todos} todos remain")
            return False
        
        print("\n✓ All relationship tests passed!")
        return True
        
    except Exception as e:
        print(f"\n✗ Relationship test failed: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return False
    finally:
        db.close()


def main():
    """Run all database tests."""
    print("\n" + "=" * 60)
    print("Milestone 2: Database Connection & Models Test")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("Connection", test_database_connection()))
    results.append(("Table Creation", test_table_creation()))
    results.append(("CRUD Operations", test_basic_operations()))
    results.append(("Relationships", test_relationships()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{test_name:.<40} {status}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n🎉 All tests passed! Database is ready")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues before proceeding.")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

