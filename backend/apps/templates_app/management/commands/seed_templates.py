"""
Management command: seed_templates

Generates a rich library of system email templates (is_system=True) — about
10 per category — owned by a shared "maven-system" organization. Because the
templates API surfaces is_system templates to every org, these appear as
ready-to-use starting points for all users (and can be duplicated).

Usage:
    python manage.py seed_templates
    python manage.py seed_templates --clear   # delete existing system templates first
"""
from django.core.management.base import BaseCommand
from django.db import transaction


# ---------------------------------------------------------------------------
# HTML email renderer
# ---------------------------------------------------------------------------

_LAYOUT = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>__TITLE__</title>
</head>
<body style="margin:0;padding:0;background:#eef1f6;font-family:'Segoe UI',Arial,Helvetica,sans-serif;">
  <div style="display:none;max-height:0;overflow:hidden;opacity:0;color:#eef1f6;">__PREHEADER__</div>
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#eef1f6;padding:32px 12px;">
    <tr><td align="center">
      <table role="presentation" width="600" cellpadding="0" cellspacing="0" style="width:600px;max-width:100%;background:#ffffff;border-radius:14px;overflow:hidden;box-shadow:0 6px 24px rgba(20,30,60,0.08);">
        <tr><td style="background:__ACCENT__;padding:22px 36px;">
          <span style="color:#ffffff;font-size:18px;font-weight:700;letter-spacing:0.5px;">Maven Technosoft</span>
        </td></tr>
        <tr><td style="padding:40px 36px 4px;">
          __EYEBROW__
          <h1 style="margin:0 0 14px;font-size:26px;line-height:1.25;color:#141b2d;">__HEADING__</h1>
        </td></tr>
        <tr><td style="padding:0 36px 4px;">__BODY__</td></tr>
        <tr><td style="padding:4px 36px 40px;">__CTA__</td></tr>
        <tr><td style="background:#f4f6fa;padding:22px 36px;border-top:1px solid #e6e9f0;">
          <p style="margin:0;color:#8a93a6;font-size:12px;line-height:1.6;">__FOOTER__<br>
            Maven Technosoft &middot; Transforming Enterprises with Cloud, Data &amp; AI<br>
            <a href="#" style="color:#8a93a6;">Unsubscribe</a> &middot;
            <a href="#" style="color:#8a93a6;">Update preferences</a>
          </p>
        </td></tr>
      </table>
    </td></tr>
  </table>
</body>
</html>"""


def _p(text: str) -> str:
    return f'<p style="margin:0 0 16px;color:#3d4451;font-size:15px;line-height:1.7;">{text}</p>'


def _eyebrow(text: str, accent: str) -> str:
    return (
        f'<p style="margin:0 0 10px;font-size:12px;font-weight:700;letter-spacing:1.5px;'
        f'text-transform:uppercase;color:{accent};">{text}</p>'
    )


def _bullets(items) -> str:
    lis = ''.join(f'<li style="margin:0 0 10px;">{i}</li>' for i in items)
    return (
        '<ul style="margin:6px 0 16px;padding-left:20px;color:#3d4451;'
        f'font-size:15px;line-height:1.7;">{lis}</ul>'
    )


def _stat(value: str, label: str, accent: str) -> str:
    return (
        '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:18px 0;">'
        '<tr><td style="background:#f4f6fa;border-radius:10px;padding:20px 24px;text-align:center;">'
        f'<span style="font-size:30px;font-weight:800;color:{accent};">{value}</span>'
        f'<span style="display:block;margin-top:4px;color:#3d4451;font-size:14px;">{label}</span>'
        '</td></tr></table>'
    )


def _button(label: str, accent: str) -> str:
    style = ('display:inline-block;padding:14px 34px;color:#ffffff;text-decoration:none;'
             'font-weight:600;font-size:15px;')
    return (
        '<table role="presentation" cellpadding="0" cellspacing="0" style="margin:24px 0 4px;"><tr>'
        f'<td style="background:{accent};border-radius:6px;">'
        f'<a href="#" style="{style}">{label}</a>'
        '</td></tr></table>'
    )


def render_email(cfg: dict) -> str:
    accent = cfg['accent']
    body = _p(cfg['intro'])
    for para in cfg.get('paragraphs', []):
        body += _p(para)
    if cfg.get('bullets'):
        body += _bullets(cfg['bullets'])
    if cfg.get('stat'):
        body += _stat(cfg['stat'][0], cfg['stat'][1], accent)

    eyebrow = _eyebrow(cfg['eyebrow'], accent) if cfg.get('eyebrow') else ''
    cta = _button(cfg.get('cta', 'Learn More'), accent)
    preheader = cfg.get('preheader', cfg['intro'][:120])

    return (
        _LAYOUT
        .replace('__TITLE__', cfg['name'])
        .replace('__PREHEADER__', preheader)
        .replace('__ACCENT__', accent)
        .replace('__EYEBROW__', eyebrow)
        .replace('__HEADING__', cfg['heading'])
        .replace('__BODY__', body)
        .replace('__CTA__', cta)
        .replace('__FOOTER__', cfg.get('footer', 'You are receiving this email from Maven Technosoft.'))
    )


# Accent palette rotated across each category for visual variety.
_ACCENTS = [
    '#d6294e', '#1a73e8', '#0d9488', '#7c3aed', '#ea580c',
    '#0369a1', '#16a34a', '#be123c', '#4f46e5', '#0891b2',
]


# ---------------------------------------------------------------------------
# Template content — ~10 per category
# ---------------------------------------------------------------------------

CATEGORY_TEMPLATES = {
    'promo': [
        {'name': 'Year-End Cloud Savings — 30% Off', 'eyebrow': 'Limited-time offer',
         'heading': 'Lock in 30% off Maven Cloud before year-end',
         'intro': 'Hi {{first_name}}, give {{company_name}} a head start on 2026 with our biggest cloud discount of the year.',
         'stat': ('30% OFF', 'first-year Enterprise Cloud licence'),
         'paragraphs': ['Migrate, scale, and modernize with zero upfront infrastructure cost — offer ends December 31.'],
         'cta': 'Claim Your Discount'},
        {'name': 'Enterprise AI Bundle — Limited Seats', 'eyebrow': 'Exclusive bundle',
         'heading': 'The Enterprise AI Bundle is back — limited seats',
         'intro': 'Combine our analytics, automation, and AI copilots in one discounted package built for {{industry}} teams.',
         'bullets': ['AI-powered analytics dashboard', 'Workflow automation suite', '24/7 dedicated support'],
         'cta': 'Reserve Your Seat'},
        {'name': 'Black Friday: Infrastructure Deal', 'eyebrow': 'Black Friday',
         'heading': 'Our best infrastructure pricing of the year',
         'intro': 'For 72 hours only, {{company_name}} can lock in premium cloud infrastructure at our lowest rate ever.',
         'stat': ('40%', 'lower total cost of ownership'),
         'cta': 'Shop the Deal'},
        {'name': 'Upgrade & Save — Premium Support', 'eyebrow': 'Upgrade offer',
         'heading': 'Upgrade to Premium Support and save 25%',
         'intro': 'Hi {{first_name}}, unlock guaranteed response times and a named success engineer for {{company_name}}.',
         'bullets': ['15-minute response SLA', 'Named success engineer', 'Quarterly architecture reviews'],
         'cta': 'Upgrade Now'},
        {'name': 'Flash Sale: Data Analytics Suite', 'eyebrow': '48-hour flash sale',
         'heading': 'Turn data into decisions — 48-hour flash sale',
         'intro': 'Our full Data Analytics Suite is 35% off for the next two days only.',
         'paragraphs': ['Connect every source, build dashboards in minutes, and give your teams answers — not spreadsheets.'],
         'cta': 'Grab the Offer'},
        {'name': 'New Customer Offer — 90 Days Free', 'eyebrow': 'New customers',
         'heading': 'Your first 90 days on us',
         'intro': 'Welcome offer for {{company_name}}: start any Maven platform free for 90 days, no commitment.',
         'stat': ('90 DAYS', 'free, then flexible monthly pricing'),
         'cta': 'Start Free'},
        {'name': 'Renewal Reward — Loyalty Discount', 'eyebrow': 'Thank you',
         'heading': "You've earned a loyalty discount",
         'intro': 'Hi {{first_name}}, thanks for growing with Maven. Renew {{company_name}} early and save 20%.',
         'cta': 'Renew & Save'},
        {'name': 'Bundle & Save: Cloud + Security', 'eyebrow': 'Better together',
         'heading': 'Cloud + Security, bundled and discounted',
         'intro': 'Protect what you build. Bundle Maven Cloud with our Security suite and save 28%.',
         'bullets': ['End-to-end encryption', 'Continuous threat monitoring', 'Compliance-ready reporting'],
         'cta': 'See Bundle Pricing'},
        {'name': 'Early-Bird Pricing: 2026 Platform', 'eyebrow': 'Early access',
         'heading': 'Early-bird pricing for the 2026 platform',
         'intro': 'Be first to the next generation of Maven — and lock in launch pricing for {{company_name}}.',
         'cta': 'Get Early-Bird Pricing'},
        {'name': 'Exclusive Partner Pricing', 'eyebrow': 'Partners only',
         'heading': 'Exclusive pricing for our partners',
         'intro': 'As a valued partner, {{company_name}} qualifies for preferred pricing across the Maven platform.',
         'cta': 'View Partner Rates'},
    ],
    'newsletter': [
        {'name': 'Maven Monthly: Tech Insights', 'eyebrow': 'Monthly newsletter',
         'heading': 'This month in enterprise technology',
         'intro': 'Hi {{first_name}}, here is your monthly roundup of trends, case studies, and product news.',
         'bullets': ['Feature: AI adoption in {{industry}}', 'Customer story: 35% cost reduction', 'New on the platform this month'],
         'cta': 'Read the Full Edition'},
        {'name': 'The Cloud Brief — Weekly Digest', 'eyebrow': 'Weekly digest',
         'heading': 'The Cloud Brief',
         'intro': 'Five minutes on the cloud news that matters to engineering and platform teams.',
         'paragraphs': ['This week: multi-cloud cost control, the new FinOps playbook, and a deep dive on autoscaling.'],
         'cta': 'Read This Week'},
        {'name': 'Data & AI Roundup', 'eyebrow': 'Data & AI',
         'heading': 'Your Data & AI roundup',
         'intro': 'The latest on analytics, machine learning, and putting big data to work in production.',
         'bullets': ['Building a 90-day AI roadmap', 'From dashboards to decisions', 'MLOps lessons from the field'],
         'cta': 'Explore the Roundup'},
        {'name': 'Product Update Newsletter', 'eyebrow': "What's new",
         'heading': "What's new at Maven this month",
         'intro': 'Hi {{first_name}}, we shipped a lot. Here are the updates most relevant to {{company_name}}.',
         'bullets': ['Faster onboarding flows', 'New analytics widgets', 'Improved role-based access'],
         'cta': 'See All Updates'},
        {'name': 'Industry Trends: Quarterly Report', 'eyebrow': 'Quarterly report',
         'heading': 'Where {{industry}} is heading next quarter',
         'intro': 'Our research team distilled the signals shaping {{industry}} into one concise report.',
         'cta': 'Download the Report'},
        {'name': 'Customer Spotlight Stories', 'eyebrow': 'Customer spotlight',
         'heading': 'How teams like yours are winning',
         'intro': 'Real stories from organizations using Maven to modernize, scale, and cut costs.',
         'paragraphs': ['This edition features a logistics leader that doubled deployment speed with Maven Cloud.'],
         'cta': 'Read the Stories'},
        {'name': 'Security Advisory Bulletin', 'eyebrow': 'Security bulletin',
         'heading': 'Your monthly security advisory',
         'intro': 'Stay ahead of threats with this month\'s advisories, patches, and best practices.',
         'bullets': ['Critical patch summary', 'Zero-trust checklist', 'Incident response tips'],
         'cta': 'Review Advisories'},
        {'name': 'Engineering Blog Highlights', 'eyebrow': 'From the blog',
         'heading': 'The best of the Maven engineering blog',
         'intro': 'Deep dives from our engineers on the systems behind the platform.',
         'cta': 'Read the Highlights'},
        {'name': 'Leadership Perspectives', 'eyebrow': 'Leadership',
         'heading': 'Perspectives from Maven leadership',
         'intro': 'Hi {{first_name}}, our leaders share how they see cloud, data, and AI reshaping {{industry}}.',
         'cta': 'Read the Interview'},
        {'name': 'Year in Review', 'eyebrow': 'Year in review',
         'heading': 'A year of building together',
         'intro': 'Thank you for an incredible year, {{first_name}}. Here is what we shipped and what is next.',
         'stat': ('120+', 'new features shipped this year'),
         'cta': 'See the Highlights'},
    ],
    'announcement': [
        {'name': 'Introducing Maven Cloud 2.0', 'eyebrow': 'Product launch',
         'heading': 'Introducing Maven Cloud 2.0',
         'intro': 'Hi {{first_name}}, the next generation of our cloud platform is here — faster, safer, and easier to scale.',
         'bullets': ['2x faster provisioning', 'Built-in cost controls', 'New zero-downtime migrations'],
         'cta': 'Explore Cloud 2.0'},
        {'name': 'New Data Center — Now Live', 'eyebrow': 'Infrastructure',
         'heading': 'Our new data center is now live',
         'intro': 'Lower latency and stronger data residency for customers in your region, including {{company_name}}.',
         'cta': 'Read the Details'},
        {'name': 'Big News: We\'ve Joined Forces', 'eyebrow': 'Announcement',
         'heading': 'Maven is joining forces to serve you better',
         'intro': 'We are excited to share news that expands what we can deliver for {{company_name}}.',
         'paragraphs': ['Nothing changes for your service today — only more capability ahead. Full details inside.'],
         'cta': 'Read the Announcement'},
        {'name': 'New AI Feature Launch', 'eyebrow': 'Now available',
         'heading': 'Meet your new AI copilot',
         'intro': 'Generate, optimize, and analyze faster with AI now built into your Maven workspace.',
         'bullets': ['Subject-line and copy generation', 'Spam-score checks', 'Smart send-time suggestions'],
         'cta': 'Try the AI Copilot'},
        {'name': 'Pricing Update Notice', 'eyebrow': 'Important notice',
         'heading': 'An update to our pricing',
         'intro': 'Hi {{first_name}}, we are writing to give {{company_name}} advance notice of upcoming pricing changes.',
         'paragraphs': ['Here is exactly what changes, when it takes effect, and how it affects your plan.'],
         'cta': 'Review the Changes'},
        {'name': 'Partnership Announcement', 'eyebrow': 'Partnership',
         'heading': 'A new partnership to power your stack',
         'intro': 'We have teamed up with a leading provider to bring more value to {{company_name}}.',
         'cta': 'Learn More'},
        {'name': 'SOC 2 Type II Achieved', 'eyebrow': 'Compliance',
         'heading': 'We achieved SOC 2 Type II',
         'intro': 'Your trust matters. Maven has completed its SOC 2 Type II audit with no exceptions.',
         'bullets': ['Independently audited controls', 'Continuous monitoring', 'Report available on request'],
         'cta': 'Request the Report'},
        {'name': 'Office Expansion News', 'eyebrow': 'Company news',
         'heading': 'We are growing to serve you better',
         'intro': 'Maven is expanding with a new regional office and support team closer to you.',
         'cta': 'Read the Story'},
        {'name': 'Scheduled Maintenance Notice', 'eyebrow': 'Service notice',
         'heading': 'Scheduled platform maintenance',
         'intro': 'Hi {{first_name}}, we will perform maintenance to improve performance and reliability.',
         'paragraphs': ['Expected window and impact are detailed inside. No action is required from {{company_name}}.'],
         'cta': 'View Maintenance Window'},
        {'name': 'Leadership Appointment', 'eyebrow': 'Leadership news',
         'heading': 'Welcoming new leadership to Maven',
         'intro': 'We are thrilled to announce a new leader joining the team to accelerate our roadmap.',
         'cta': 'Meet the Team'},
    ],
    'webinar': [
        {'name': 'The Future of Enterprise AI', 'eyebrow': 'Free webinar',
         'heading': 'The Future of Enterprise AI in {{industry}}',
         'intro': 'Hi {{first_name}}, join our experts for a 60-minute session on putting AI to work — without the hype.',
         'bullets': ['Real {{industry}} use cases', 'Building a 90-day adoption plan', 'Live Q&A with our AI team'],
         'cta': 'Reserve My Seat'},
        {'name': 'Cloud Migration Masterclass', 'eyebrow': 'Masterclass',
         'heading': 'Cloud Migration Masterclass',
         'intro': 'A practical, step-by-step walkthrough of migrating production workloads with zero downtime.',
         'cta': 'Save My Spot'},
        {'name': 'Big Data Strategy Workshop', 'eyebrow': 'Workshop',
         'heading': 'Build a big-data strategy that scales',
         'intro': 'Turn raw data into a competitive advantage in this hands-on workshop for {{industry}} leaders.',
         'bullets': ['Designing your data platform', 'Governance that scales', 'From pipelines to insight'],
         'cta': 'Register Free'},
        {'name': 'Cybersecurity Best Practices', 'eyebrow': 'Security webinar',
         'heading': 'Cybersecurity best practices for 2026',
         'intro': 'Learn the controls and habits that keep modern enterprises secure — and audit-ready.',
         'cta': 'Reserve Your Seat'},
        {'name': 'Live Product Demo', 'eyebrow': 'Live demo',
         'heading': 'See the Maven platform live',
         'intro': 'Hi {{first_name}}, join a guided demo and see exactly how Maven fits {{company_name}}.',
         'cta': 'Book the Demo'},
        {'name': 'Digital Transformation Roadmap', 'eyebrow': 'Strategy session',
         'heading': 'Your digital transformation roadmap',
         'intro': 'A clear framework for modernizing {{industry}} operations — and where to start.',
         'cta': 'Join the Session'},
        {'name': 'DevOps at Scale', 'eyebrow': 'Engineering webinar',
         'heading': 'DevOps at scale: shipping faster, safely',
         'intro': 'How high-performing teams automate, observe, and deploy with confidence.',
         'bullets': ['CI/CD that scales', 'Observability done right', 'Reducing change failure rate'],
         'cta': 'Register Now'},
        {'name': 'Customer Success Panel', 'eyebrow': 'Live panel',
         'heading': 'Lessons from teams that scaled with Maven',
         'intro': 'Hear directly from customers about what worked, what they would change, and results they saw.',
         'cta': 'Save My Seat'},
        {'name': 'AMA with Our CTO', 'eyebrow': 'Ask me anything',
         'heading': 'Ask our CTO anything',
         'intro': 'Bring your hardest questions on cloud, data, and AI — our CTO is answering live.',
         'cta': 'Submit a Question'},
        {'name': 'Annual Tech Summit', 'eyebrow': 'Flagship event',
         'heading': 'The Maven Annual Tech Summit',
         'intro': 'Hi {{first_name}}, join thousands of {{industry}} leaders for a day of keynotes and deep dives.',
         'stat': ('20+', 'sessions across cloud, data & AI'),
         'cta': 'Get Your Pass'},
    ],
    'onboarding': [
        {'name': 'Welcome to Maven Technosoft', 'eyebrow': 'Welcome aboard',
         'heading': 'Welcome aboard, {{first_name}}!',
         'intro': 'We are thrilled to have {{company_name}} on Maven. Let us get you set up for a fast start.',
         'bullets': ['Complete your profile', 'Invite your team', 'Launch your first project'],
         'cta': 'Go to Your Dashboard'},
        {'name': 'Your Account is Ready', 'eyebrow': 'Account ready',
         'heading': 'Your Maven account is ready',
         'intro': 'Everything is set up for {{company_name}}. Sign in and take the first step.',
         'cta': 'Sign In'},
        {'name': 'Getting Started in 3 Steps', 'eyebrow': 'Quick start',
         'heading': 'Get value from Maven in 3 steps',
         'intro': 'Hi {{first_name}}, follow these three steps to see results in your first session.',
         'bullets': ['1. Connect your data', '2. Pick a template', '3. Launch your first campaign'],
         'cta': 'Start Step 1'},
        {'name': 'Meet Your Success Manager', 'eyebrow': "You're not alone",
         'heading': 'Meet your customer success manager',
         'intro': 'A dedicated expert is here to help {{company_name}} get the most from Maven.',
         'cta': 'Schedule a Kickoff'},
        {'name': 'Complete Your Profile', 'eyebrow': 'One quick thing',
         'heading': 'Finish setting up your profile',
         'intro': 'A complete profile unlocks personalization and a smoother experience for your team.',
         'cta': 'Complete Profile'},
        {'name': 'Explore Key Features', 'eyebrow': 'Did you know?',
         'heading': 'Three features worth trying first',
         'intro': 'Hi {{first_name}}, here are the features customers love most in their first week.',
         'bullets': ['AI copywriting copilot', 'Drag-and-drop email editor', 'Real-time analytics'],
         'cta': 'Explore Features'},
        {'name': 'Your First Project Setup', 'eyebrow': 'Build something',
         'heading': 'Set up your first project',
         'intro': 'Turn the platform into results — let us walk you through creating your first project.',
         'cta': 'Create a Project'},
        {'name': 'Invite Your Team', 'eyebrow': 'Better together',
         'heading': 'Bring your team into Maven',
         'intro': 'Maven is better with your whole team. Invite colleagues from {{company_name}} in seconds.',
         'cta': 'Invite Teammates'},
        {'name': 'Training Resources', 'eyebrow': 'Learn faster',
         'heading': 'Everything you need to master Maven',
         'intro': 'Guides, videos, and live training to help your team ramp quickly.',
         'bullets': ['Getting-started guides', 'On-demand video library', 'Weekly live training'],
         'cta': 'Browse Resources'},
        {'name': '30-Day Check-In', 'eyebrow': 'How is it going?',
         'heading': 'You\'ve been with us 30 days',
         'intro': 'Hi {{first_name}}, let us make sure {{company_name}} is getting full value from Maven.',
         'cta': 'Book a Check-In'},
    ],
    'outreach': [
        {'name': 'Quick question about {{company_name}}', 'eyebrow': 'Reaching out',
         'heading': 'A quick question, {{first_name}}',
         'intro': 'I noticed {{company_name}} is scaling its {{industry}} operations — congratulations on the growth.',
         'paragraphs': ['We recently helped similar teams cut IT overhead while shipping faster. Open to a short chat?'],
         'cta': 'Book 20 Minutes'},
        {'name': 'Helping {{industry}} teams scale', 'eyebrow': 'Introduction',
         'heading': 'Helping {{industry}} teams scale faster',
         'intro': 'Hi {{first_name}}, we work with {{industry}} leaders to modernize infrastructure without the chaos.',
         'cta': 'See How'},
        {'name': 'Following up on your inquiry', 'eyebrow': 'Following up',
         'heading': 'Following up, {{first_name}}',
         'intro': 'Just circling back on your interest in Maven for {{company_name}}. Happy to answer any questions.',
         'cta': 'Continue the Conversation'},
        {'name': 'Idea for reducing IT costs', 'eyebrow': 'An idea for you',
         'heading': 'An idea to reduce {{company_name}}\'s IT costs',
         'intro': 'A quick thought on where {{industry}} teams typically overspend — and how to fix it.',
         'stat': ('28%', 'average infrastructure cost reduction'),
         'cta': 'Show Me How'},
        {'name': 'Congrats on your growth', 'eyebrow': 'Noticed your news',
         'heading': 'Congrats on the momentum, {{first_name}}',
         'intro': 'Saw the news about {{company_name}} — exciting times. Growth usually means new infrastructure pressure.',
         'cta': "Let's Talk Scale"},
        {'name': '20-minute intro call?', 'eyebrow': 'Quick ask',
         'heading': 'Worth a 20-minute call?',
         'intro': 'Hi {{first_name}}, I will keep it focused on {{company_name}}\'s challenges — not a product pitch.',
         'cta': 'Pick a Time'},
        {'name': 'Case study for {{industry}}', 'eyebrow': 'Relevant results',
         'heading': 'How a {{industry}} team doubled deploy speed',
         'intro': 'Thought this short case study might resonate with what {{company_name}} is working on.',
         'cta': 'Read the Case Study'},
        {'name': 'Re: modernizing your stack', 'eyebrow': 'Following up',
         'heading': 'Modernizing the {{company_name}} stack',
         'intro': 'Hi {{first_name}}, a few teams in {{industry}} recently modernized with us in under 30 days.',
         'cta': 'Explore the Approach'},
        {'name': 'Connecting from Maven', 'eyebrow': 'Hello',
         'heading': 'Hi {{first_name}}, connecting from Maven',
         'intro': 'I lead enterprise partnerships at Maven and would love to learn about {{company_name}}\'s roadmap.',
         'cta': 'Say Hello'},
        {'name': 'Last note — value for {{company_name}}', 'eyebrow': 'Last note',
         'heading': 'One last note, {{first_name}}',
         'intro': 'I will stop reaching out after this — but I genuinely think Maven could help {{company_name}}.',
         'paragraphs': ['If the timing is ever right, the door is open. Wishing you and the team continued success.'],
         'cta': 'Reopen the Conversation'},
    ],
}


# ---------------------------------------------------------------------------
# Command
# ---------------------------------------------------------------------------

class Command(BaseCommand):
    help = 'Seed a rich library of system email templates (~10 per category).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Delete all existing system templates before seeding.',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        from organizations.models import Organization
        from apps.templates_app.models import EmailTemplate

        system_org, created = Organization.objects.get_or_create(
            slug='maven-system',
            defaults={'name': 'Maven System'},
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created system organisation: {system_org.name}'))

        if options['clear']:
            deleted, _ = EmailTemplate.objects.filter(is_system=True).delete()
            self.stdout.write(self.style.WARNING(f'Deleted {deleted} existing system templates.'))

        created_count = 0
        updated_count = 0

        for category, templates in CATEGORY_TEMPLATES.items():
            for cfg in templates:
                cfg = {**cfg, 'accent': cfg.get('accent', _ACCENTS[len(cfg['name']) % len(_ACCENTS)])}
                html = render_email(cfg)
                _, was_created = EmailTemplate.objects.update_or_create(
                    name=cfg['name'],
                    organization=system_org,
                    defaults={
                        'category': category,
                        'thumbnail_url': '',
                        'html_output': html,
                        'gjs_components': {},
                        'gjs_styles': {},
                        'is_system': True,
                    },
                )
                if was_created:
                    created_count += 1
                else:
                    updated_count += 1

            self.stdout.write(self.style.SUCCESS(f'  - {category}: {len(templates)} templates'))

        total = created_count + updated_count
        self.stdout.write(
            self.style.SUCCESS(
                f'\nDone. {total} system templates ({created_count} created, {updated_count} updated).'
            )
        )
