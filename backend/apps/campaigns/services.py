import csv
import io
from typing import List, Dict


def parse_recipient_csv(csv_content: str) -> List[Dict]:
    """
    Parse CSV with columns: email, name, and any personalization columns.
    Returns list of dicts with 'email', 'name', and 'personalization' keys.
    """
    reader = csv.DictReader(io.StringIO(csv_content))
    recipients = []
    standard_fields = {'email', 'name'}
    for row in reader:
        row = {k.strip().lower(): v.strip() for k, v in row.items()}
        if not row.get('email'):
            continue
        personalization = {k: v for k, v in row.items() if k not in standard_fields}
        recipients.append({
            'email': row['email'],
            'name': row.get('name', ''),
            'personalization': personalization,
        })
    return recipients


def render_personalized_html(html: str, personalization: Dict) -> str:
    """Replace {{key}} placeholders with personalization values."""
    for key, value in personalization.items():
        html = html.replace(f'{{{{{key}}}}}', str(value))
    return html
