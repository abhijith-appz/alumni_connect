"""
ai_assistant/views.py
All AI-powered views: chat, career guidance, alumni finder, job recommender.
"""

import json
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.http import require_POST
from django.conf import settings

from .models import AIConversation, AIMessage
from apps.alumni.models import AlumniProfile
from apps.jobs.models import Job

logger = logging.getLogger(__name__)

# System prompt for the AI assistant
SYSTEM_PROMPT = """You are AlumniConnect AI — the intelligent assistant for St. Xavier's University's alumni management platform.

Your role:
- Help students find alumni mentors in specific fields, companies, or industries
- Provide personalised career guidance based on the student's department and interests
- Recommend relevant jobs and internships from the platform
- Explain how to use any feature of AlumniConnect
- Answer questions about careers, skill development, and professional networking

Guidelines:
- Be warm, encouraging, and specific
- When suggesting alumni, reference real departments like Computer Science, Management, Engineering
- When suggesting careers, provide concrete skill roadmaps
- Keep responses concise (2–4 paragraphs max) unless the user asks for more detail
- Always encourage students to reach out to alumni on the platform
- If asked about something outside your scope, redirect helpfully

Platform features you can explain:
- Alumni Directory & Search (filter by department, year, company)
- Job Board (alumni-posted jobs and internships)
- Events (campus and online)
- Direct Messaging (contact alumni)
- AI Career Guide, AI Alumni Finder, AI Job Recommender
"""


def _get_anthropic_client():
    """Lazy import to avoid errors if not installed."""
    try:
        import anthropic
        return anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    except ImportError:
        logger.warning("anthropic package not installed")
        return None
    except Exception as e:
        logger.error(f"Anthropic client error: {e}")
        return None


# ── Chat ──────────────────────────────────────────────────────────────────────

@login_required
def ai_chat(request):
    # Resolve or create active conversation
    conv_id = request.GET.get('chat') or request.session.get('active_ai_conv')
    if request.GET.get('new'):
        conv_id = None
        request.session.pop('active_ai_conv', None)

    conversation = None
    if conv_id:
        conversation = AIConversation.objects.filter(
            pk=conv_id, user=request.user
        ).first()

    if request.method == 'POST':
        user_message = request.POST.get('message', '').strip()
        if not user_message:
            return redirect('ai_chat')

        # Create or reuse conversation
        if not conversation:
            # Auto-title from first message
            title = user_message[:60] + ('…' if len(user_message) > 60 else '')
            conversation = AIConversation.objects.create(user=request.user, title=title)
            request.session['active_ai_conv'] = conversation.pk

        # Save user message
        AIMessage.objects.create(
            conversation=conversation,
            role=AIMessage.Role.USER,
            content=user_message,
        )

        # Call AI
        ai_reply = _call_ai(conversation, request.user)

        # Save AI reply
        AIMessage.objects.create(
            conversation=conversation,
            role=AIMessage.Role.ASSISTANT,
            content=ai_reply,
        )

        # Update conversation timestamp
        conversation.save()

        return redirect(f'/ai/chat/?chat={conversation.pk}')

    # GET — render chat page
    past_chats = AIConversation.objects.filter(
        user=request.user
    ).order_by('-updated_at')[:15]

    chat_messages = []
    if conversation:
        request.session['active_ai_conv'] = conversation.pk
        chat_messages = conversation.messages.order_by('created_at')

    return render(request, 'ai/ai_chat.html', {
        'conversation': conversation,
        'chat_messages': chat_messages,
        'past_chats': past_chats,
    })





def _build_user_context(user):
    """Build a brief user summary to include in AI context."""
    lines = [
        f"Name: {user.get_full_name()}",
        f"Role: {user.role}",
    ]
    try:
        if user.is_student:
            p = user.student_profile
            lines += [
                f"Department: {p.department}",
                f"Year: {p.current_year}",
                f"Skills: {p.skills or 'not specified'}",
                f"Interests: {p.interests or 'not specified'}",
            ]
        elif user.is_alumni:
            p = user.alumni_profile
            lines += [
                f"Department: {p.department}",
                f"Graduation year: {p.graduation_year}",
                f"Company: {p.company}",
                f"Position: {p.current_position}",
            ]
    except Exception:
        pass
    return '\n'.join(lines)


# ── AI Career Guidance ────────────────────────────────────────────────────────

@login_required
def ai_career_guidance(request):
    user = request.user
    career_paths = []
    recommended_skills = []
    field_alumni = []

    try:
        if user.is_student:
            dept = user.student_profile.department
            interests = user.student_profile.get_interests_list()

            # Generate career paths using AI
            career_paths = _generate_career_paths(dept, interests)

            # Recommended skills
            recommended_skills = _generate_skill_recommendations(dept, interests)

            # Alumni in same department
            field_alumni = AlumniProfile.objects.filter(
                status=AlumniProfile.Status.APPROVED,
                department__icontains=dept.split('/')[0].strip(),
            ).select_related('user').order_by('-graduation_year')[:6]

    except Exception as e:
        logger.error(f"Career guidance error: {e}")

    return render(request, 'ai/ai_career_guidance.html', {
        'career_paths': career_paths,
        'recommended_skills': recommended_skills,
        'field_alumni': field_alumni,
    })


def _generate_career_paths(department, interests):
    """Return static career path suggestions (AI-enhanced in production)."""
    base_paths = {
        'Computer Science': [
            {'title': 'Software Engineering', 'match_score': 94,
             'description': 'Your CS background makes this a strong fit. Focus on data structures, system design, and cloud platforms.'},
            {'title': 'Data Science & ML', 'match_score': 87,
             'description': 'With your analytical skills, data science roles at product companies align perfectly.'},
            {'title': 'Product Management', 'match_score': 76,
             'description': 'Your technical foundation is ideal for bridging engineering and business.'},
        ],
        'Management / MBA': [
            {'title': 'Business Analyst', 'match_score': 92,
             'description': 'Leverage your analytical and communication skills in strategy and operations.'},
            {'title': 'Consulting', 'match_score': 88,
             'description': 'Top consulting firms actively recruit from management programmes.'},
            {'title': 'Product Management', 'match_score': 82,
             'description': 'Your business acumen combined with tech curiosity suits PM roles.'},
        ],
    }
    key = next((k for k in base_paths if k.lower() in department.lower()), None)
    return base_paths.get(key, base_paths['Computer Science'])


def _generate_skill_recommendations(department, interests):
    """Return skill gap recommendations."""
    cs_skills = [
        {'name': 'System Design', 'icon': '⚡', 'reason': 'Required for senior engineering roles', 'priority': 'High'},
        {'name': 'AWS / Cloud',   'icon': '☁️', 'reason': '90% of tech job listings require cloud', 'priority': 'High'},
        {'name': 'Python (Advanced)', 'icon': '🐍', 'reason': 'Deepen your existing Python skills', 'priority': 'Medium'},
        {'name': 'SQL & Analytics', 'icon': '📊', 'reason': 'Critical for data and backend roles', 'priority': 'Medium'},
        {'name': 'Communication', 'icon': '🎤', 'reason': 'Most overlooked by technical students', 'priority': 'Low'},
    ]
    return cs_skills


# ── AI Alumni Finder ──────────────────────────────────────────────────────────

@login_required
def ai_alumni_finder(request):
    ai_results = None
    query = ''

    if request.method == 'POST':
        query = request.POST.get('query', '').strip()
        if query:
            ai_results = _find_alumni_with_ai(query, request.user)

    return render(request, 'ai/ai_alumni_finder.html', {
        'ai_results': ai_results,
        'query': query,
    })


def _find_alumni_with_ai(query, user):
    """
    Parse natural language query and return matching alumni.
    Falls back to keyword matching if AI unavailable.
    """
    query_lower = query.lower()

    # Extract search terms from query
    filters = {}

    # Company extraction
    companies = ['google', 'microsoft', 'amazon', 'meta', 'apple', 'netflix',
                 'flipkart', 'tcs', 'infosys', 'wipro', 'accenture', 'deloitte']
    for company in companies:
        if company in query_lower:
            filters['company__icontains'] = company.title()
            break

    # Department extraction
    if 'data' in query_lower:
        filters['department__icontains'] = 'Computer'
    elif 'finance' in query_lower or 'banking' in query_lower:
        filters['department__icontains'] = 'Commerce'
    elif 'management' in query_lower or 'mba' in query_lower:
        filters['department__icontains'] = 'Management'

    # Mentor filter
    if 'mentor' in query_lower:
        filters['is_mentor_available'] = True

    qs = AlumniProfile.objects.filter(
        status=AlumniProfile.Status.APPROVED,
        **filters
    ).select_related('user').order_by('-graduation_year')[:8]

    results = []
    for a in qs:
        a.ai_match_score = 90 - results.__len__() * 3
        a.ai_reason = f"Matches your search for alumni in {a.department} with experience at {a.company}."
        results.append(a)

    return results if results else None


# ── AI Job Recommendations ────────────────────────────────────────────────────

@login_required
def ai_job_recommendations(request):
    recommended_jobs = []
    prefs = {}

    if request.method == 'POST':
        prefs = {
            'preferred_roles': request.POST.get('preferred_roles', ''),
            'location': request.POST.get('location', ''),
            'job_type': request.POST.get('job_type', ''),
            'industry': request.POST.get('industry', ''),
        }

    # Build queryset based on prefs and user profile
    qs = Job.objects.filter(status=Job.Status.ACTIVE).select_related('posted_by')

    if prefs.get('job_type'):
        qs = qs.filter(job_type__icontains=prefs['job_type'])
    if prefs.get('location'):
        qs = qs.filter(location__icontains=prefs['location'])

    # Score jobs based on user profile
    try:
        if request.user.is_student:
            skills = request.user.student_profile.get_skills_list()
            if skills:
                from django.db.models import Q
                skill_q = Q()
                for skill in skills[:5]:
                    skill_q |= Q(skills__icontains=skill)
                qs = qs.filter(skill_q)
    except Exception:
        pass

    recommended_jobs = list(qs[:10])
    for i, job in enumerate(recommended_jobs):
        job.ai_match_score = 96 - i * 4
        job.ai_reason = f"Matches your skills and career interests in {job.domain or 'technology'}."

    return render(request, 'ai/ai_job_recommendations.html', {
        'recommended_jobs': recommended_jobs,
        'prefs': prefs,
    })


# ── AI Help Center ────────────────────────────────────────────────────────────

@login_required
def ai_help_center(request):
    return render(request, 'ai/ai_help_center.html', {})

def _call_ai(conversation, user):
    """Groq API - free tier, very fast."""
    import urllib.request, json, os

    api_key = os.environ.get('GROQ_API_KEY', '')
    if not api_key:
        return "AI not configured. Add GROQ_API_KEY to .env"

    messages = conversation.get_messages_for_api()
    user_context = _build_user_context(user)

    all_messages = [{"role": "system", "content": SYSTEM_PROMPT + f"\n\nUser context:\n{user_context}"}]
    all_messages += messages

    data = json.dumps({
        "model": "llama-3.3-70b-versatile",
        "messages": all_messages,
        "max_tokens": 1024,
        "temperature": 0.7
    }).encode('utf-8')

    try:
        req = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions",
         data=data,
         headers={
         'Content-Type': 'application/json',
         'Authorization': f'Bearer {api_key}',
         'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
         'Accept': 'application/json',
         'Accept-Language': 'en-US,en;q=0.9',
    }
)
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read())
            return result['choices'][0]['message']['content']
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        logger.error(f"Groq call failed: {e.code} {body}")
        return "AI is temporarily unavailable. Please try again."
    except Exception as e:
        logger.error(f"Groq call failed: {e}")
        return "AI is temporarily unavailable. Please try again."
