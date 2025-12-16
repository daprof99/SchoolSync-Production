-- Run this in your Supabase SQL Editor

create table if not exists attendance (
  id uuid primary key default uuid_generate_v4(),
  school_id uuid references schools(id) on delete cascade,
  student_id text not null, -- Links to students.id
  status text default 'Present', -- Present, Late, Absent
  timestamp timestamp with time zone default timezone('utc'::text, now()),
  date date default CURRENT_DATE -- Useful for querying "today's attendance"
);

-- Optional: Index for faster queries
create index if not exists idx_attendance_school_date on attendance(school_id, date);
