
import os
from supabase import create_client, Client
from dotenv import load_dotenv
import time

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def run_sql(sql_query):
    # Note: The Python client doesn't expose a direct raw SQL method for DDL easily 
    # unless using rpc() with a stored procedure. 
    # For initial setup, we will use the user's dashboard or try to use PostgREST if enabled?
    # Actually, Supabase Python client is for DML (Data Manipulation).
    # DDL (Data Definition) generally needs to be done via SQL Editor in Dashboard or strictly via RPC.
    
    # HOWEVER, since I cannot access the user's dashboard, I will create a function 
    # or just assume the user can run this SQL.
    
    # Wait, 'rpc' can execute SQL if there is a helper function.
    # But we don't have one.
    
    # WORKAROUND: We will print the SQL needed and ask the user to run it?
    # OR: We can use `requests` to call the SQL API if we had the management token (which we don't, only Key).
    
    # Let's try to query. If it fails, tables don't exist.
    pass

print("="*50)
print("SUPABASE MIGRATOR")
print("="*50)

print("Connecting to Supabase...")
try:
    res = supabase.table('schools').select("*").limit(1).execute()
    print("✅ Connection successful!")
    print("ℹ️  'schools' table already exists.")
except Exception as e:
    print("⚠️  'schools' table likely missing.")
    print(e)

print("\nIMPORTANT: Python Client cannot create tables directly without an RPC function.")
print("Please run the following SQL in the Supabase SQL Editor:")

sql_commands = """
-- Enable UUID extension
create extension if not exists "uuid-ossp";

-- 1. SCHOOLS
create table if not exists schools (
  id uuid primary key default uuid_generate_v4(),
  name text not null,
  admin_phone text not null,
  admin_email text,
  sheet_id text, -- Keeping for backward compat if needed, or migration
  created_at timestamp with time zone default timezone('utc'::text, now())
);

-- 2. STUDENTS
create table if not exists students (
  id text primary key, -- e.g. ST-001
  school_id uuid references schools(id) on delete cascade,
  parent_name text,
  parent_phone text,
  student_class text,
  total_fees numeric default 0,
  amount_paid numeric default 0,
  balance numeric generated always as (total_fees - amount_paid) stored,
  created_at timestamp with time zone default timezone('utc'::text, now())
);

-- 3. PAYMENTS
create table if not exists payments (
  id uuid primary key default uuid_generate_v4(),
  student_id text references students(id),
  amount numeric not null,
  reference text,
  date timestamp with time zone default timezone('utc'::text, now())
);

-- 4. EVENTS
create table if not exists events (
  id uuid primary key default uuid_generate_v4(),
  school_id uuid references schools(id) on delete cascade,
  title text not null,
  date date,
  time text,
  type text,
  created_at timestamp with time zone default timezone('utc'::text, now())
);

-- 5. MESSAGES
create table if not exists messages (
  id uuid primary key default uuid_generate_v4(),
  school_id uuid references schools(id) on delete cascade,
  parent_phone text,
  content text,
  status text default 'Pending',
  created_at timestamp with time zone default timezone('utc'::text, now())
);
"""

print(sql_commands)
print("\n" + "="*50)
