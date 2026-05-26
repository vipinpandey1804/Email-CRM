"""
Management command: seed_templates

Creates system-level email templates (is_system=True) that belong to a
special "system" organisation (created if it doesn't exist).

Usage:
    python manage.py seed_templates
    python manage.py seed_templates --clear   # delete existing system templates first
"""
from django.core.management.base import BaseCommand
from django.db import transaction


# ---------------------------------------------------------------------------
# Template data
# ---------------------------------------------------------------------------

SYSTEM_TEMPLATES = [
    {
        "name": "Cloud Migration Announcement",
        "category": "announcement",
        "thumbnail_url": "",
        "html_output": """<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8"/>
  <title>Cloud Migration Announcement</title>
</head>
<body style="font-family:Arial,sans-serif;background:#f4f4f4;margin:0;padding:0;">
  <table width="600" align="center" cellpadding="0" cellspacing="0"
         style="background:#ffffff;border-radius:8px;overflow:hidden;margin:32px auto;">
    <tr>
      <td style="background:#1a237e;padding:32px 40px;">
        <h1 style="color:#ffffff;margin:0;font-size:24px;">Maven Technosoft</h1>
      </td>
    </tr>
    <tr>
      <td style="padding:40px;">
        <h2 style="color:#1a237e;">Your Cloud Migration Journey Starts Here</h2>
        <p style="color:#444;line-height:1.6;">
          Dear {{first_name}},
        </p>
        <p style="color:#444;line-height:1.6;">
          We're excited to announce our enterprise cloud migration solutions
          designed specifically for {{industry}} organisations like {{company_name}}.
        </p>
        <p style="color:#444;line-height:1.6;">
          Our proven 3-phase migration framework ensures zero data loss, minimal
          downtime, and up to 40% reduction in infrastructure costs.
        </p>
        <table cellpadding="0" cellspacing="0" style="margin:32px 0;">
          <tr>
            <td style="background:#1a237e;border-radius:4px;padding:14px 32px;">
              <a href="#" style="color:#ffffff;text-decoration:none;font-weight:bold;font-size:16px;">
                Schedule a Free Assessment
              </a>
            </td>
          </tr>
        </table>
        <p style="color:#888;font-size:13px;">
          Maven Technosoft | Transforming Enterprises, One Cloud at a Time
        </p>
      </td>
    </tr>
  </table>
</body>
</html>""",
        "gjs_components": {},
        "gjs_styles": {},
    },
    {
        "name": "Digital Transformation Newsletter",
        "category": "newsletter",
        "thumbnail_url": "",
        "html_output": """<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8"/>
  <title>Digital Transformation Newsletter</title>
</head>
<body style="font-family:Arial,sans-serif;background:#f4f4f4;margin:0;padding:0;">
  <table width="600" align="center" cellpadding="0" cellspacing="0"
         style="background:#ffffff;border-radius:8px;overflow:hidden;margin:32px auto;">
    <tr>
      <td style="background:#0d47a1;padding:24px 40px;">
        <h1 style="color:#ffffff;margin:0;font-size:20px;">Maven Tech Insights</h1>
        <p style="color:#90caf9;margin:4px 0 0;font-size:13px;">Monthly Newsletter</p>
      </td>
    </tr>
    <tr>
      <td style="padding:40px;">
        <h2 style="color:#0d47a1;margin-top:0;">This Month in Digital Transformation</h2>
        <p style="color:#444;line-height:1.6;">Hi {{first_name}},</p>
        <p style="color:#444;line-height:1.6;">
          Welcome to the latest edition of Maven Tech Insights — your monthly
          roundup of enterprise technology trends, case studies, and best practices.
        </p>

        <h3 style="color:#1565c0;border-bottom:2px solid #e3f2fd;padding-bottom:8px;">
          Feature: Big Data for {{industry}}
        </h3>
        <p style="color:#444;line-height:1.6;">
          Organisations in {{industry}} are generating more data than ever before.
          Learn how our clients are turning raw data into actionable insights with
          our AI-powered analytics platform.
        </p>

        <h3 style="color:#1565c0;border-bottom:2px solid #e3f2fd;padding-bottom:8px;">
          Case Study Spotlight
        </h3>
        <p style="color:#444;line-height:1.6;">
          How {{company_name}} reduced operational costs by 35% after deploying
          Maven's enterprise automation suite — read the full story.
        </p>

        <table cellpadding="0" cellspacing="0" style="margin:28px 0;">
          <tr>
            <td style="background:#0d47a1;border-radius:4px;padding:12px 28px;">
              <a href="#" style="color:#ffffff;text-decoration:none;font-weight:bold;">
                Read Full Newsletter →
              </a>
            </td>
          </tr>
        </table>
      </td>
    </tr>
    <tr>
      <td style="background:#f8f9fa;padding:20px 40px;text-align:center;">
        <p style="color:#999;font-size:12px;margin:0;">
          © 2024 Maven Technosoft · Unsubscribe
        </p>
      </td>
    </tr>
  </table>
</body>
</html>""",
        "gjs_components": {},
        "gjs_styles": {},
    },
    {
        "name": "Enterprise Solution Promotion",
        "category": "promo",
        "thumbnail_url": "",
        "html_output": """<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8"/>
  <title>Enterprise Solution Promotion</title>
</head>
<body style="font-family:Arial,sans-serif;background:#f4f4f4;margin:0;padding:0;">
  <table width="600" align="center" cellpadding="0" cellspacing="0"
         style="background:#ffffff;border-radius:8px;overflow:hidden;margin:32px auto;">
    <tr>
      <td style="background:linear-gradient(135deg,#1a237e,#0288d1);padding:40px;text-align:center;">
        <h1 style="color:#ffffff;margin:0;font-size:28px;">Limited-Time Offer</h1>
        <p style="color:#b3e5fc;font-size:16px;margin:8px 0 0;">Exclusively for {{industry}} Leaders</p>
      </td>
    </tr>
    <tr>
      <td style="padding:40px;">
        <p style="color:#444;line-height:1.6;">Dear {{first_name}},</p>
        <p style="color:#444;line-height:1.6;">
          As a decision-maker at {{company_name}}, you understand the competitive
          pressure to modernise. For a limited time, Maven Technosoft is offering
          our full Enterprise Suite at exclusive pricing.
        </p>

        <table width="100%" cellpadding="0" cellspacing="0"
               style="background:#e8f5e9;border-radius:8px;margin:24px 0;">
          <tr>
            <td style="padding:24px;text-align:center;">
              <p style="margin:0;font-size:36px;font-weight:bold;color:#2e7d32;">30% OFF</p>
              <p style="margin:4px 0 0;color:#388e3c;font-size:14px;">First-year Enterprise licence</p>
            </td>
          </tr>
        </table>

        <ul style="color:#444;line-height:1.8;padding-left:20px;">
          <li>Full cloud infrastructure migration support</li>
          <li>AI-powered analytics dashboard</li>
          <li>24/7 dedicated enterprise support</li>
          <li>Onboarding in 30 days or your money back</li>
        </ul>

        <table cellpadding="0" cellspacing="0" style="margin:28px 0;">
          <tr>
            <td style="background:#e53935;border-radius:4px;padding:16px 40px;">
              <a href="#" style="color:#ffffff;text-decoration:none;font-weight:bold;font-size:16px;">
                Claim Your Discount Now
              </a>
            </td>
          </tr>
        </table>

        <p style="color:#888;font-size:12px;">
          Offer valid until December 31, 2024. Terms & conditions apply.
        </p>
      </td>
    </tr>
  </table>
</body>
</html>""",
        "gjs_components": {},
        "gjs_styles": {},
    },
    {
        "name": "Webinar Invitation: Future of Enterprise AI",
        "category": "webinar",
        "thumbnail_url": "",
        "html_output": """<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8"/>
  <title>Webinar Invitation</title>
</head>
<body style="font-family:Arial,sans-serif;background:#f4f4f4;margin:0;padding:0;">
  <table width="600" align="center" cellpadding="0" cellspacing="0"
         style="background:#ffffff;border-radius:8px;overflow:hidden;margin:32px auto;">
    <tr>
      <td style="background:#4a148c;padding:32px 40px;text-align:center;">
        <p style="color:#ce93d8;margin:0 0 8px;font-size:13px;text-transform:uppercase;letter-spacing:2px;">
          Free Webinar
        </p>
        <h1 style="color:#ffffff;margin:0;font-size:24px;line-height:1.3;">
          The Future of Enterprise AI<br/>in {{industry}}
        </h1>
        <p style="color:#ce93d8;margin:16px 0 0;font-size:15px;">
          Thursday, December 19, 2024 · 2:00 PM IST
        </p>
      </td>
    </tr>
    <tr>
      <td style="padding:40px;">
        <p style="color:#444;line-height:1.6;">Dear {{first_name}},</p>
        <p style="color:#444;line-height:1.6;">
          Join us for an exclusive 60-minute webinar where Maven Technosoft's
          AI experts will reveal how {{industry}} companies like {{company_name}}
          can leverage AI to automate processes, predict outcomes, and drive growth.
        </p>

        <h3 style="color:#4a148c;">What You'll Learn</h3>
        <ul style="color:#444;line-height:1.8;padding-left:20px;">
          <li>Real-world AI use cases in {{industry}}</li>
          <li>Building a 90-day AI adoption roadmap</li>
          <li>Live demo: Maven AI Analytics Platform</li>
          <li>Q&A with industry experts</li>
        </ul>

        <table cellpadding="0" cellspacing="0" style="margin:28px 0;">
          <tr>
            <td style="background:#4a148c;border-radius:4px;padding:14px 32px;">
              <a href="#" style="color:#ffffff;text-decoration:none;font-weight:bold;font-size:16px;">
                Reserve My Seat →
              </a>
            </td>
          </tr>
        </table>

        <p style="color:#888;font-size:13px;">
          Seats are limited. Register now to secure your spot.
        </p>
      </td>
    </tr>
  </table>
</body>
</html>""",
        "gjs_components": {},
        "gjs_styles": {},
    },
    {
        "name": "Customer Onboarding Welcome",
        "category": "onboarding",
        "thumbnail_url": "",
        "html_output": """<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8"/>
  <title>Welcome to Maven Technosoft</title>
</head>
<body style="font-family:Arial,sans-serif;background:#f4f4f4;margin:0;padding:0;">
  <table width="600" align="center" cellpadding="0" cellspacing="0"
         style="background:#ffffff;border-radius:8px;overflow:hidden;margin:32px auto;">
    <tr>
      <td style="background:#00695c;padding:32px 40px;text-align:center;">
        <h1 style="color:#ffffff;margin:0;font-size:26px;">Welcome Aboard, {{first_name}}! 🎉</h1>
        <p style="color:#b2dfdb;margin:8px 0 0;font-size:15px;">Your enterprise journey starts today</p>
      </td>
    </tr>
    <tr>
      <td style="padding:40px;">
        <p style="color:#444;line-height:1.6;">
          Thank you for choosing Maven Technosoft as your technology partner.
          We're thrilled to have {{company_name}} as part of our enterprise family.
        </p>

        <h3 style="color:#00695c;">Your Next Steps</h3>

        <table width="100%" cellpadding="0" cellspacing="0">
          <tr>
            <td width="40" valign="top" style="padding:8px 0;">
              <span style="background:#00695c;color:#fff;border-radius:50%;
                           width:28px;height:28px;display:inline-block;
                           text-align:center;line-height:28px;font-weight:bold;">1</span>
            </td>
            <td style="padding:8px 0 8px 12px;color:#444;line-height:1.6;">
              <strong>Complete your profile</strong> — Add your team members
              and configure your organisation settings.
            </td>
          </tr>
          <tr>
            <td width="40" valign="top" style="padding:8px 0;">
              <span style="background:#00695c;color:#fff;border-radius:50%;
                           width:28px;height:28px;display:inline-block;
                           text-align:center;line-height:28px;font-weight:bold;">2</span>
            </td>
            <td style="padding:8px 0 8px 12px;color:#444;line-height:1.6;">
              <strong>Schedule your kickoff call</strong> — Meet your dedicated
              customer success manager.
            </td>
          </tr>
          <tr>
            <td width="40" valign="top" style="padding:8px 0;">
              <span style="background:#00695c;color:#fff;border-radius:50%;
                           width:28px;height:28px;display:inline-block;
                           text-align:center;line-height:28px;font-weight:bold;">3</span>
            </td>
            <td style="padding:8px 0 8px 12px;color:#444;line-height:1.6;">
              <strong>Explore the platform</strong> — Browse our getting-started
              guides and video tutorials.
            </td>
          </tr>
        </table>

        <table cellpadding="0" cellspacing="0" style="margin:28px 0;">
          <tr>
            <td style="background:#00695c;border-radius:4px;padding:14px 32px;">
              <a href="#" style="color:#ffffff;text-decoration:none;font-weight:bold;font-size:16px;">
                Access Your Dashboard
              </a>
            </td>
          </tr>
        </table>

        <p style="color:#888;font-size:13px;">
          Questions? Reply to this email or contact support@maventechnosoft.com
        </p>
      </td>
    </tr>
  </table>
</body>
</html>""",
        "gjs_components": {},
        "gjs_styles": {},
    },
    {
        "name": "B2B Outreach — Enterprise Solutions",
        "category": "outreach",
        "thumbnail_url": "",
        "html_output": """<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8"/>
  <title>Maven Technosoft Outreach</title>
</head>
<body style="font-family:Arial,sans-serif;background:#f4f4f4;margin:0;padding:0;">
  <table width="600" align="center" cellpadding="0" cellspacing="0"
         style="background:#ffffff;border-radius:8px;overflow:hidden;margin:32px auto;">
    <tr>
      <td style="background:#37474f;padding:24px 40px;">
        <h1 style="color:#ffffff;margin:0;font-size:20px;">Maven Technosoft</h1>
      </td>
    </tr>
    <tr>
      <td style="padding:40px;">
        <p style="color:#444;line-height:1.6;">Hi {{first_name}},</p>
        <p style="color:#444;line-height:1.6;">
          I noticed that {{company_name}} is rapidly expanding its {{industry}}
          operations. Congratulations on the growth!
        </p>
        <p style="color:#444;line-height:1.6;">
          I'm reaching out because we recently helped three {{industry}} companies
          of similar scale cut their IT overhead by 28% and go live with new
          infrastructure 2× faster — using our TTHL technology stack.
        </p>
        <p style="color:#444;line-height:1.6;">
          Would you be open to a 20-minute call to explore whether there's a fit?
          I'll keep it focused on your specific challenges, not a product pitch.
        </p>

        <table cellpadding="0" cellspacing="0" style="margin:28px 0;">
          <tr>
            <td style="background:#37474f;border-radius:4px;padding:14px 32px;">
              <a href="#" style="color:#ffffff;text-decoration:none;font-weight:bold;font-size:16px;">
                Book a 20-Minute Call
              </a>
            </td>
          </tr>
        </table>

        <p style="color:#444;line-height:1.6;">
          Best regards,<br/>
          <strong>{{sender_name}}</strong><br/>
          Enterprise Sales · Maven Technosoft
        </p>
      </td>
    </tr>
  </table>
</body>
</html>""",
        "gjs_components": {},
        "gjs_styles": {},
    },
]


# ---------------------------------------------------------------------------
# Command
# ---------------------------------------------------------------------------

class Command(BaseCommand):
    help = 'Seed system email templates (is_system=True) into the database.'

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

        # Ensure a system organisation exists (slug = 'system')
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
        skipped_count = 0

        for tpl_data in SYSTEM_TEMPLATES:
            obj, was_created = EmailTemplate.objects.update_or_create(
                name=tpl_data['name'],
                organization=system_org,
                defaults={
                    'category': tpl_data['category'],
                    'thumbnail_url': tpl_data.get('thumbnail_url', ''),
                    'html_output': tpl_data['html_output'],
                    'gjs_components': tpl_data.get('gjs_components', {}),
                    'gjs_styles': tpl_data.get('gjs_styles', {}),
                    'is_system': True,
                },
            )
            if was_created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'  ✓ Created: {obj.name}'))
            else:
                skipped_count += 1
                self.stdout.write(f'  ~ Updated: {obj.name}')

        self.stdout.write(
            self.style.SUCCESS(
                f'\nDone. {created_count} created, {skipped_count} updated.'
            )
        )
