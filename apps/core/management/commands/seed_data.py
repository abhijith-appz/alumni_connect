"""
Management command: seed_data
Usage: python manage.py seed_data

Creates realistic demo data for development/testing:
- 1 admin user
- 10 alumni (approved)
- 15 students
- 20 jobs
- 5 events
- Sample messages
"""

import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

DEPARTMENTS = [
    'Computer Science',
    'Management / MBA',
    'Electronics & Communication',
    'Mechanical Engineering',
    'Commerce & Finance',
    'Law',
]

COMPANIES = [
    'Google', 'Microsoft', 'Amazon', 'Flipkart', 'Infosys',
    'TCS', 'Wipro', 'Deloitte', 'Goldman Sachs', 'Razorpay',
]

POSITIONS = [
    'Software Engineer', 'Senior Engineer', 'Product Manager',
    'Data Scientist', 'Business Analyst', 'Consultant',
    'DevOps Engineer', 'ML Engineer', 'UX Designer', 'Director',
]

JOB_TITLES = [
    'Software Engineer', 'Senior Backend Developer', 'Data Analyst',
    'Product Manager', 'UX Designer', 'DevOps Engineer',
    'Machine Learning Engineer', 'Full Stack Developer',
    'Business Analyst', 'Cloud Architect', 'QA Engineer',
    'Frontend Developer', 'Mobile Developer (Android)',
    'System Administrator', 'Cybersecurity Analyst',
    'Data Engineer', 'Research Engineer', 'Site Reliability Engineer',
    'Marketing Analyst', 'Finance Associate',
]

EVENT_DATA = [
    {
        'title': 'Annual Alumni Meet 2024',
        'description': 'Join us for the flagship annual gathering of St. Xavier\'s alumni and students.',
        'event_type': 'on_campus',
        'location': 'Main Campus Auditorium, St. Xavier\'s University',
        'capacity': 300,
    },
    {
        'title': 'Career Fair & Networking Webinar',
        'description': 'Connect with 30+ companies recruiting St. Xavier\'s graduates.',
        'event_type': 'online',
        'location': 'Online — Zoom (link sent on registration)',
        'capacity': 500,
    },
    {
        'title': 'Tech Talk: AI in Industry',
        'description': 'Alumni working in AI share real-world insights and career advice.',
        'event_type': 'online',
        'location': 'Online — Google Meet',
        'capacity': 200,
    },
    {
        'title': 'Startup Founders Panel',
        'description': 'Entrepreneurs from St. Xavier\'s discuss their startup journeys.',
        'event_type': 'on_campus',
        'location': 'Innovation Hub, Xavier Campus',
        'capacity': 100,
    },
    {
        'title': 'Resume & Interview Workshop',
        'description': 'Alumni HR professionals review resumes and conduct mock interviews.',
        'event_type': 'hybrid',
        'location': 'MBA Seminar Hall + Online',
        'capacity': 80,
    },
]


class Command(BaseCommand):
    help = 'Seed the database with demo data for development'

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true',
                            help='Clear existing demo data before seeding')

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data…')
            User.objects.filter(username__startswith='demo_').delete()

        self.stdout.write(self.style.MIGRATE_HEADING('Seeding demo data…'))

        admin  = self._create_admin()
        alumni = self._create_alumni()
        students = self._create_students()
        jobs   = self._create_jobs(alumni)
        events = self._create_events(admin)
        self._create_messages(students, alumni)

        self.stdout.write(self.style.SUCCESS(
            f'\n✅  Seeding complete!\n'
            f'   Admin:    admin / admin123\n'
            f'   Alumni:   alumni1 … alumni{len(alumni)} / pass123\n'
            f'   Students: student1 … student{len(students)} / pass123\n'
            f'   Jobs:     {len(jobs)} created\n'
            f'   Events:   {len(events)} created\n'
        ))

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _create_admin(self):
        user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email':      'admin@stxaviers.edu',
                'first_name': 'Admin',
                'last_name':  'Xavier',
                'role':       User.Role.ADMIN,
                'is_staff':   True,
                'is_superuser': True,
                'is_active':  True,
            }
        )
        if created:
            user.set_password('admin123')
            user.save()
            self.stdout.write(f'  Created admin: admin / admin123')
        return user

    def _create_alumni(self):
        from apps.alumni.models import AlumniProfile

        alumni_data = [
            ('Anil', 'Kumar',   'Computer Science',    2018, 'Google',      'Senior Engineer'),
            ('Sunita', 'Rao',   'Management / MBA',    2015, 'Microsoft',   'Product Manager'),
            ('Mohan', 'Pillai', 'Computer Science',    2020, 'Amazon',      'Data Scientist'),
            ('Riya', 'Nair',    'Commerce & Finance',  2019, 'Goldman Sachs','Analyst'),
            ('Priya', 'Thomas', 'Management / MBA',    2012, 'Deloitte',    'Senior Consultant'),
            ('Dev', 'Varma',    'Computer Science',    2021, 'Razorpay',    'Backend Developer'),
            ('Kavitha', 'Menon','Electronics & Communication', 2017, 'Qualcomm', 'VLSI Engineer'),
            ('Rahul', 'Sharma', 'Computer Science',    2016, 'Flipkart',    'Engineering Manager'),
            ('Deepa', 'Nair',   'Law',                 2013, 'Cyril Amarchand', 'Associate Partner'),
            ('Sanjay', 'Patel', 'Mechanical Engineering', 2014, 'Tata Motors', 'Design Lead'),
        ]

        alumni_list = []
        for i, (fname, lname, dept, year, company, position) in enumerate(alumni_data, 1):
            username = f'alumni{i}'
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email':      f'{username}@example.com',
                    'first_name': fname,
                    'last_name':  lname,
                    'role':       User.Role.ALUMNI,
                    'is_active':  True,
                }
            )
            if created:
                user.set_password('pass123')
                user.save()

            profile, _ = AlumniProfile.objects.get_or_create(
                user=user,
                defaults={
                    'department':       dept,
                    'graduation_year':  year,
                    'company':          company,
                    'current_position': position,
                    'location':         random.choice(['Bangalore', 'Mumbai', 'Delhi', 'Hyderabad', 'Pune']),
                    'skills':           'Python, Leadership, Communication, Problem Solving',
                    'bio':              f'Alumnus of St. Xavier\'s University ({dept}, {year}). Currently working as {position} at {company}.',
                    'is_mentor_available': (i % 3 == 0),
                    'status':           AlumniProfile.Status.APPROVED,
                    'approved_at':      timezone.now(),
                }
            )
            alumni_list.append(profile)
            self.stdout.write(f'  Alumni {i}: {fname} {lname} ({company})')

        return alumni_list

    def _create_students(self):
        from apps.students.models import StudentProfile

        first_names = ['Arjun', 'Sneha', 'Vikram', 'Pooja', 'Kiran',
                       'Neha', 'Rohit', 'Ananya', 'Suresh', 'Divya',
                       'Amit', 'Lakshmi', 'Prasad', 'Meera', 'Rajesh']
        last_names  = ['Singh', 'Kumar', 'Patel', 'Sharma', 'Nair',
                       'Iyer', 'Reddy', 'Pillai', 'Varma', 'Menon',
                       'Joshi', 'Mehta', 'Das', 'Bose', 'Mishra']

        students = []
        for i in range(1, 16):
            username = f'student{i}'
            fname    = first_names[i - 1]
            lname    = last_names[i - 1]
            dept     = DEPARTMENTS[(i - 1) % len(DEPARTMENTS)]

            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email':      f'{username}@stxaviers.edu',
                    'first_name': fname,
                    'last_name':  lname,
                    'role':       User.Role.STUDENT,
                    'is_active':  True,
                }
            )
            if created:
                user.set_password('pass123')
                user.save()

            profile, _ = StudentProfile.objects.get_or_create(
                user=user,
                defaults={
                    'student_id':   f'SX2024{i:03d}',
                    'department':   dept,
                    'current_year': random.randint(1, 4),
                    'expected_graduation': 2025 + random.randint(0, 3),
                    'skills':       'Python, Communication, Teamwork',
                    'interests':    'Technology, Finance, Entrepreneurship',
                }
            )
            students.append(profile)

        self.stdout.write(f'  Created {len(students)} students')
        return students

    def _create_jobs(self, alumni_profiles):
        from apps.jobs.models import Job

        jobs = []
        for i, title in enumerate(JOB_TITLES):
            alumni  = alumni_profiles[i % len(alumni_profiles)]
            job_type = random.choice([
                Job.Type.FULL_TIME, Job.Type.FULL_TIME, Job.Type.FULL_TIME,
                Job.Type.INTERNSHIP, Job.Type.REMOTE,
            ])
            job, created = Job.objects.get_or_create(
                title=title,
                posted_by=alumni.user,
                defaults={
                    'company':      alumni.company,
                    'location':     random.choice(['Bangalore', 'Mumbai', 'Remote', 'Hyderabad', 'Pune']),
                    'job_type':     job_type,
                    'domain':       random.choice(['Technology', 'Finance', 'Marketing', 'Operations']),
                    'salary':       f'₹{random.randint(8, 40)}-{random.randint(41, 60)} LPA',
                    'experience':   f'{random.randint(0, 5)}+ years',
                    'description':  f'We are hiring a {title} to join our growing team at {alumni.company}. You will work on challenging problems and collaborate with talented engineers.',
                    'requirements': 'B.Tech/B.E. or equivalent degree\n2+ years of relevant experience\nStrong communication skills',
                    'skills':       'Python, Django, Problem Solving, Teamwork',
                    'status':       Job.Status.ACTIVE,
                    'deadline':     (timezone.now() + timedelta(days=random.randint(7, 60))).date(),
                }
            )
            if created:
                jobs.append(job)

        self.stdout.write(f'  Created {len(jobs)} jobs')
        return jobs

    def _create_events(self, admin_user):
        from apps.events.models import Event

        events = []
        for i, data in enumerate(EVENT_DATA):
            event_date = timezone.now() + timedelta(days=random.randint(7, 90))
            event, created = Event.objects.get_or_create(
                title=data['title'],
                defaults={
                    **data,
                    'event_date':   event_date,
                    'is_published': True,
                    'created_by':   admin_user,
                }
            )
            if created:
                events.append(event)

        self.stdout.write(f'  Created {len(events)} events')
        return events

    def _create_messages(self, students, alumni_profiles):
        from apps.messaging.models import Conversation, Message

        count = 0
        for i in range(min(5, len(students))):
            student = students[i].user
            alumni  = alumni_profiles[i % len(alumni_profiles)].user

            conv, _ = Conversation.get_or_create_between(student, alumni)

            messages_data = [
                (student, f'Hi {alumni.first_name}, I found your profile on AlumniConnect. I am a {students[i].department} student and would love to learn about your career at {alumni_profiles[i % len(alumni_profiles)].company}.'),
                (alumni,  f'Hi {student.first_name}! Great to hear from you. I would be happy to chat. What specific area are you interested in?'),
                (student, 'I am particularly interested in backend development and system design. Any advice for a student starting out?'),
                (alumni,  'Great choice! Focus on data structures and algorithms first, then pick one backend language deeply — Python or Go are popular here. Happy to review your resume when ready!'),
            ]

            for sender, content in messages_data:
                Message.objects.get_or_create(
                    conversation=conv,
                    sender=sender,
                    content=content,
                )
                count += 1

        self.stdout.write(f'  Created {count} sample messages')
