import os
import tempfile
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from datetime import datetime

def create_pdf_report(results, email):
    """Create PDF report from search results"""
    temp_dir = tempfile.gettempdir()
    pdf_path = os.path.join(temp_dir, f'holehe_report_{email.replace("@", "_")}_{int(time.time())}.pdf')

    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        textColor=colors.darkblue
    )
    story.append(Paragraph(f'Holehe Results for: {email}', title_style))
    story.append(Spacer(1, 20))

    # Summary
    summary_data = [
        ['Search Date', results.get('search_time', 'Unknown')],
        ['Email Address', email],
        ['Total Sites Checked', str(results.get('total_sites', 0))],
        ['Accounts Found', str(results.get('found_count', 0))],
        ['Not Found', str(results.get('not_found_count', 0))],
        ['Rate Limited', str(results.get('rate_limited_count', 0))],
        ['Errors', str(results.get('error_count', 0))],
    ]

    summary_table = Table(summary_data, colWidths=[2*inch, 3*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    story.append(summary_table)
    story.append(Spacer(1, 30))

    # Found Profiles Only
    found_profiles = results.get('found_profiles', [])
    if found_profiles:
        story.append(Paragraph('Found Accounts:', styles['Heading2']))
        story.append(Spacer(1, 12))

        profile_data = [['Site', 'Domain', 'Additional Info']]
        for profile in found_profiles:
            additional_info = []
            if profile.get('emailrecovery'):
                additional_info.append(f"Email Recovery: {profile['emailrecovery']}")
            if profile.get('phoneNumber'):
                additional_info.append(f"Phone: {profile['phoneNumber']}")
            if profile.get('others'):
                for key, value in profile['others'].items():
                    additional_info.append(f"{key}: {value}")

            profile_data.append([
                profile['site'],
                profile['domain'],
                '\n'.join(additional_info) if additional_info else 'No additional info'
            ])

        profile_table = Table(profile_data, colWidths=[1.5*inch, 2*inch, 2.5*inch])
        profile_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]))

        story.append(profile_table)
    else:
        story.append(Paragraph('No accounts found for this email address.', styles['Normal']))

    doc.build(story)
    return pdf_path
