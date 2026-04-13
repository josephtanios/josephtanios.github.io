#!/usr/bin/env python3
"""
CSV to Interactive HTML CV Generator
Converts Joseph_Tanios_CV_Complete_Extract.csv to HTML with professional layout
"""

import csv
from html import escape
from pathlib import Path
from collections import defaultdict

class CSVToHTMLConverter:
    def __init__(self, csv_file):
        self.csv_file = Path(csv_file)
        self.data = self.parse_csv()
        
    def parse_csv(self):
        """Parse CSV into structured data"""
        data = defaultdict(lambda: defaultdict(list))
        
        with open(self.csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                section = row['SECTION'].strip()
                subsection = row['SUBSECTION'].strip()
                key = row['KEY'].strip()
                value = row['VALUE'].strip()
                
                # Skip empty rows
                if not section or not subsection or not key or not value:
                    continue
                
                data[section][subsection].append({
                    'key': key,
                    'value': value
                })
        
        return data
    
    def get_contact_info(self):
        """Extract contact information"""
        contact = {}
        if 'CONTACT' in self.data:
            for subsection, items in self.data['CONTACT'].items():
                for item in items:
                    contact[item['key']] = item['value']
        return contact
    
    def get_professional_summary(self):
        """Extract professional summary"""
        if 'PROFESSIONAL SUMMARY' in self.data:
            summary = {}
            for subsection, items in self.data['PROFESSIONAL SUMMARY'].items():
                summary[subsection] = [item['value'] for item in items]
            return summary
        return {}
    
    def get_experience(self):
        """Extract and structure experience data"""
        experiences = []
        if 'EXPERIENCE' in self.data:
            positions = defaultdict(dict)
            
            for subsection, items in self.data['EXPERIENCE'].items():
                position_num = subsection.split()[-1]  # Extract number from "POSITION 1", "POSITION 2", etc.
                if position_num not in positions:
                    positions[position_num] = {}
                
                for item in items:
                    if item['key'] not in positions[position_num]:
                        positions[position_num][item['key']] = item['value']
                    else:
                        # Handle multiple values for same key
                        if not isinstance(positions[position_num][item['key']], list):
                            positions[position_num][item['key']] = [positions[position_num][item['key']]]
                        positions[position_num][item['key']].append(item['value'])
            
            # Convert to list sorted by position number
            for pos_num in sorted(positions.keys(), key=lambda x: int(x)):
                experiences.append(positions[pos_num])
        
        return experiences
    
    def get_skills(self):
        """Extract and structure skills data"""
        skills = []
        if 'SKILLS' in self.data:
            categories = defaultdict(lambda: {'skills': [], 'level': ''})

            # Collect skills and levels (case-insensitive key handling)
            for subsection, items in self.data['SKILLS'].items():
                cat_name = subsection.strip()
                for item in items:
                    key = item['key'].strip()
                    val = item['value']
                    key_lower = key.lower()
                    if key_lower == 'level':
                        categories[cat_name]['level'] = val
                    elif key_lower.startswith('skill') or key_lower == 'skill':
                        categories[cat_name]['skills'].append(val)

            # Build an ordered list of categories. Prefer known groups but include any present.
            preferred_order = [
                'ORDER MANAGEMENT', 'BANKING', 'DATA', 'ASSET', 'DERIVATIVES',
                'MIGRATION', 'LEADERSHIP', 'TECHNICAL'
            ]

            remaining = list(categories.keys())
            ordered = []

            # Add categories matching preferred keywords (case-insensitive)
            for pref in preferred_order:
                for cat in list(remaining):
                    if pref.upper() in cat.upper():
                        ordered.append(cat)
                        remaining.remove(cat)

            # Append any leftover categories (preserve CSV order as much as possible)
            for cat in remaining:
                ordered.append(cat)

            # Build final skills structure, removing duplicates
            for cat in ordered:
                lvl = categories[cat].get('level', '')
                seen = set()
                uniq_skills = []
                for s in categories[cat]['skills']:
                    if s and s not in seen:
                        uniq_skills.append(s)
                        seen.add(s)

                skills.append({'category': cat, 'level': lvl, 'skills': uniq_skills})

        return skills
    
    def get_achievements(self):
        """Extract achievements"""
        achievements = []
        if 'ACHIEVEMENTS' in self.data:
            ach_dict = defaultdict(dict)
            
            for subsection, items in self.data['ACHIEVEMENTS'].items():
                ach_num = subsection.split()[-1]
                if ach_num not in ach_dict:
                    ach_dict[ach_num] = {}
                
                for item in items:
                    ach_dict[ach_num][item['key']] = item['value']
            
            for ach_num in sorted(ach_dict.keys(), key=lambda x: int(x)):
                achievements.append(ach_dict[ach_num])
        
        return achievements
    
    def get_education(self):
        """Extract education and certifications"""
        certs = []
        degrees = []
        research = []

        key_aliases = {
            'years': 'Year',
            'yr': 'Year',
            'date': 'Year'
        }
        
        if 'EDUCATION' in self.data:
            for subsection, items in self.data['EDUCATION'].items():
                edu_dict = {}
                for item in items:
                    raw_key = item['key'].strip()
                    normalized_key = key_aliases.get(raw_key.lower(), raw_key)
                    edu_dict[normalized_key] = item['value']
                
                if 'CERTIFICATION' in subsection.upper():
                    certs.append(edu_dict)
                elif 'DEGREE' in subsection.upper():
                    degrees.append(edu_dict)
                elif 'RESEARCH' in subsection.upper():
                    research.append(edu_dict)
        
        return {'certifications': certs, 'degrees': degrees, 'research': research}
    
    def get_languages(self):
        """Extract languages"""
        languages = []
        if 'LANGUAGES' in self.data:
            lang_dict = defaultdict(dict)
            
            for subsection, items in self.data['LANGUAGES'].items():
                lang_num = subsection.split()[-1]
                if lang_num not in lang_dict:
                    lang_dict[lang_num] = {}
                
                for item in items:
                    lang_dict[lang_num][item['key']] = item['value']
            
            for lang_num in sorted(lang_dict.keys(), key=lambda x: int(x)):
                languages.append(lang_dict[lang_num])
        
        return languages

    def get_core_competencies(self):
        """Extract core competencies boxes from CORE COMPETENCIES section"""
        boxes = []
        if 'CORE COMPETENCIES' not in self.data:
            return boxes

        for subsection, items in self.data['CORE COMPETENCIES'].items():
            box = {
                'subsection': subsection,
                'title': '',
                'enabled': True,
                'items': []
            }

            for item in items:
                key = item['key'].strip().lower()
                val = item['value'].strip()
                if key == 'title':
                    box['title'] = val
                elif key == 'enabled':
                    box['enabled'] = val.lower() not in ('no', 'false', '0')
                elif key.startswith('item'):
                    box['items'].append(val)

            boxes.append(box)

        def _box_sort_key(box):
            tail = box.get('subsection', '').split()[-1]
            try:
                return int(tail)
            except Exception:
                return 9999

        boxes.sort(key=_box_sort_key)
        return boxes
    
    def generate_html(self):
        """Generate complete HTML CV"""
        contact = self.get_contact_info()
        summary = self.get_professional_summary()
        experience = self.get_experience()
        skills = self.get_skills()
        achievements = self.get_achievements()
        education = self.get_education()
        languages = self.get_languages()
        core_competencies = self.get_core_competencies()

        # Build contact HTML dynamically from CSV data (no hardcoded defaults)
        contact_html_parts = []
        # Preferred order and corresponding SVG icons
        contact_order = [
            ('Email', '<svg fill="currentColor" viewBox="0 0 20 20"><path d="M2.003 5.884L10 9.882l7.997-3.998A2 2 0 0016 4H4a2 2 0 00-1.997 1.884z"></path><path d="M18 8.118l-8 4-8-4V14a2 2 0 002 2h12a2 2 0 002-2V8.118z"></path></svg>'),
            ('Location', '<svg fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clip-rule="evenodd"></path></svg>')
        ]

        for key, svg in contact_order:
            val = contact.get(key)
            if val and str(val).strip():
                # default: svg icon + visible value
                contact_html_parts.append(f'<div class="contact-item">{svg}\n                        {val}\n                    </div>')

        contact_html = '\n                    '.join(contact_html_parts) if contact_html_parts else ''
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Joseph Tanios, CFA - Interactive CV</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        :root {{
            --primary: #0F2D4A;
            --secondary: #1F4E79;
            --accent: #2E6FAE;
            --success: #1F7A5A;
            --warning: #B07A00;
            --danger: #B42318;
            --purple: #3A4A6B;
            --gradient-1: linear-gradient(135deg, #0F2D4A 0%, #1F4E79 100%);
            --gradient-2: linear-gradient(135deg, #1F4E79 0%, #2E6FAE 100%);
            --gradient-3: linear-gradient(135deg, #0F2D4A 0%, #0B1F33 100%);
            --text-dark: #0F172A;
            --text-light: #475569;
            --bg-light: #F6F8FB;
            --shadow: 0 10px 30px rgba(15,23,42,0.10);
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #EEF2F7;
            min-height: 100vh;
            padding: clamp(0px, 1.2vw, 12px);
            line-height: 1.6;
        }}

        .container {{
            width: min(1600px, 100%);
            margin: 0 auto;
            min-height: 100vh;
            background: white;
            border-radius: clamp(0px, 1.2vw, 20px);
            overflow: hidden;
            box-shadow: 0 20px 60px rgba(15,23,42,0.22);
        }}

        .header {{
            background: var(--gradient-1);
            color: white;
            padding: clamp(18px, 3.2vw, 34px) 30px;
            text-align: center;
            position: relative;
            overflow: hidden;
        }}

        .header::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg"><rect width="100" height="100" fill="rgba(255,255,255,0.05)"/><circle cx="50" cy="50" r="30" fill="rgba(255,255,255,0.08)"/></svg>');
            opacity: 0.12;
        }}

        .header-content {{
            position: relative;
            z-index: 1;
            max-width: 980px;
            margin: 0 auto;
        }}

        .name {{
            font-size: 3em;
            font-weight: bold;
            margin-bottom: 4px;
            line-height: 1.1;
            text-shadow: 2px 2px 4px rgba(15,23,42,0.25);
        }}

        .name-link {{
            color: inherit;
            text-decoration: none;
        }}

        .name-link:hover {{
            text-decoration: underline;
        }}

        .title {{
            font-size: 1.5em;
            opacity: 0.95;
            margin-bottom: 8px;
            line-height: 1.35;
        }}

        .contact-info {{
            display: flex;
            justify-content: center;
            gap: 20px;
            flex-wrap: wrap;
            margin-top: 6px;
        }}

        .contact-item {{
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 1em;
        }}

        .contact-item svg {{
            width: 20px;
            height: 20px;
        }}

        .nav-tabs {{
            display: flex;
            flex-wrap: wrap;
            background: var(--bg-light);
            padding: 0;
            border-bottom: 2px solid #E2E8F0;
            overflow-x: hidden;
            overflow-y: hidden;
            scrollbar-width: none;
        }}

        .nav-tabs::-webkit-scrollbar {{
            display: none;
        }}

        .nav-tab {{
            flex: 1 1 180px;
            min-width: 0;
            padding: 16px 10px;
            text-align: center;
            cursor: pointer;
            background: transparent;
            border: none;
            font-size: 1em;
            font-weight: 600;
            color: var(--text-light);
            transition: all 0.3s ease;
            position: relative;
            min-width: 150px;
        }}

        .nav-tab:hover {{
            background: white;
            color: var(--primary);
        }}

        .nav-tab.active {{
            background: white;
            color: var(--primary);
        }}

        .nav-tab.active::after {{
            content: '';
            position: absolute;
            bottom: -2px;
            left: 0;
            right: 0;
            height: 3px;
            background: var(--gradient-1);
        }}

        .content {{
            padding: 40px;
        }}

        .tab-content {{
            display: none;
            animation: fadeIn 0.5s ease;
        }}

        .tab-content.active {{
            display: block;
        }}

        @keyframes fadeIn {{
            from {{
                opacity: 0;
                transform: translateY(20px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}

        .section {{
            margin-bottom: 20px;
            border: 2px solid #E2E8F0;
            border-radius: 12px;
            overflow: hidden;
            transition: all 0.3s ease;
        }}

        .section:hover {{
            border-color: var(--accent);
            box-shadow: var(--shadow);
        }}

        .section-header {{
            background: var(--gradient-1);
            color: white;
            padding: 20px 25px;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: all 0.3s ease;
            user-select: none;
        }}

        .section-header:hover {{
            background: var(--gradient-2);
        }}

        .section-header h3 {{
            font-size: 1.3em;
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .section-icon {{
            font-size: 1.5em;
        }}

        .toggle-icon {{
            font-size: 1.5em;
            transition: transform 0.3s ease;
        }}

        .section.expanded .toggle-icon {{
            transform: rotate(180deg);
        }}

        .section-content {{
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.4s ease, padding 0.4s ease;
            background: white;
        }}

        .section.expanded .section-content {{
            max-height: 3000px;
            padding: 25px;
        }}

        .skills-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}

        .skill-card {{
            background: var(--bg-light);
            padding: 20px;
            border-radius: 12px;
            border-left: 4px solid var(--accent);
            transition: all 0.3s ease;
        }}

        .skill-card:hover {{
            transform: translateY(-5px);
            box-shadow: var(--shadow);
            border-left-color: var(--secondary);
        }}

        .skill-card h4 {{
            color: var(--primary);
            margin-bottom: 10px;
            font-size: 1.1em;
        }}

        .skill-tags {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 10px;
        }}

        .tag {{
            background: var(--gradient-1);
            color: white;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 500;
        }}

        .tag.proficiency-expert {{
            background: var(--success);
        }}

        .tag.proficiency-advanced {{
            background: var(--secondary);
        }}

        .timeline {{
            position: relative;
            padding-left: 40px;
        }}

        .timeline::before {{
            content: '';
            position: absolute;
            left: 0;
            top: 0;
            bottom: 0;
            width: 3px;
            background: var(--gradient-1);
        }}

        .timeline-date {{
            color: var(--text-light);
            font-size: 0.9em;
            margin-bottom: 5px;
        }}

        .timeline-role {{
            color: var(--secondary);
            font-size: 1em;
            font-weight: 600;
            margin-bottom: 10px;
        }}

        .timeline-content {{
            background: var(--bg-light);
            padding: 15px;
            border-radius: 8px;
            margin-top: 10px;
        }}

        .timeline-content ul {{
            margin-left: 20px;
        }}

        .timeline-content li {{
            margin-bottom: 8px;
        }}

        .timeline-content h4 {{
            color: var(--primary);
            margin-top: 10px;
            margin-bottom: 8px;
        }}

        .timeline-content h4:first-child {{
            margin-top: 0;
        }}

        .achievement-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }}

        .achievement-card {{
            background: var(--gradient-3);
            color: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: var(--shadow);
            transition: all 0.3s ease;
            position: relative;
        }}

        .achievement-card:hover {{
            transform: translateY(-10px);
            box-shadow: 0 15px 40px rgba(15,23,42,0.18);
        }}

        .achievement-card h4 {{
            font-size: 1.3em;
            margin-bottom: 10px;
        }}

        .achievement-card p {{
            font-size: 0.95em;
            line-height: 1.6;
        }}

        .achievement-number {{
            font-size: 3em;
            font-weight: bold;
            opacity: 0.25;
            position: absolute;
            top: 10px;
            right: 15px;
        }}

        .cert-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }}

        .cert-badge {{
            background: white;
            border: 3px solid var(--accent);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            transition: all 0.3s ease;
        }}

        .cert-badge:hover {{
            transform: scale(1.05);
            border-color: var(--secondary);
            box-shadow: var(--shadow);
        }}

        .cert-badge .cert-icon {{
            font-size: 3em;
            margin-bottom: 10px;
        }}

        .cert-badge h4 {{
            color: var(--primary);
            font-size: 1em;
            margin-bottom: 5px;
        }}

        .cert-badge .cert-year {{
            color: var(--text-light);
            font-size: 0.85em;
        }}

        .highlight-box {{
            background: linear-gradient(135deg, rgba(15,45,74,0.06) 0%, rgba(31,78,121,0.10) 100%);
            border-left: 4px solid var(--secondary);
            padding: 20px;
            border-radius: 8px;
            margin: 15px 0;
        }}

        .highlight-box strong {{
            color: var(--primary);
        }}

        @media (max-width: 768px) {{
            body {{
                padding: 0;
            }}

            .container {{
                border-radius: 0;
                min-height: 100vh;
            }}

            .header {{
                padding: 16px 16px;
            }}

            .name {{
                font-size: 2em;
            }}

            .title {{
                font-size: 1.2em;
            }}

            .content {{
                padding: 18px 16px;
            }}

            .contact-info {{
                flex-direction: column;
                gap: 10px;
            }}

            .nav-tabs {{
                flex-direction: row;
            }}

            .nav-tab {{
                flex: 1 1 50%;
                min-width: 50%;
                padding: 14px 8px;
                font-size: 0.95em;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- HEADER -->
        <div class="header">
            <div class="header-content">
                <h1 class="name">
                    <a href="https://www.linkedin.com/in/joseph-tanios-95561282/" target="_blank" rel="noopener noreferrer" class="name-link">
                        {contact.get('First Name', 'Joseph')} {contact.get('Last Name', 'Tanios')}
                    </a>
                </h1>
                <p class="title">{contact.get('Professional Title', 'CFA | Project Delivery Manager | Order Management Expert')}</p>
                <div class="contact-info">
                    {contact_html}
                </div>
            </div>
        </div>

        <!-- NAVIGATION -->
        <div class="nav-tabs">
            <button class="nav-tab active" onclick="switchTab('summary')">📋 Summary</button>
            <button class="nav-tab" onclick="switchTab('experience')">💼 Experience</button>
            <button class="nav-tab" onclick="switchTab('skills')">⚡ Skills</button>
            <button class="nav-tab" onclick="switchTab('achievements')">🏆 Achievements</button>
            <button class="nav-tab" onclick="switchTab('education')">🎓 Education</button>
        </div>

        <!-- CONTENT -->
        <div class="content">
            <!-- SUMMARY TAB -->
            <div id="summary" class="tab-content active">
                <div class="highlight-box">
                    <h2 style="color: var(--primary); margin-bottom: 15px;">Professional Summary</h2>
                    {self._render_overview_html(summary)}
                </div>

                {self._generate_core_competencies_html(core_competencies)}
            </div>

            <!-- EXPERIENCE TAB -->
            <div id="experience" class="tab-content">
                <div class="timeline">
                    {self._generate_experience_html(experience)}
                </div>
            </div>

            <!-- SKILLS TAB -->
            <div id="skills" class="tab-content">
                <h2 style="color: var(--primary); margin-bottom: 25px;">Technical &amp; Professional Skills</h2>

                <div class="skills-grid">
                    {self._generate_skills_html(skills)}
                </div>
            </div>

            <!-- ACHIEVEMENTS TAB -->
            <div id="achievements" class="tab-content">
                <h2 style="color: var(--primary); margin-bottom: 25px;">Key Achievements</h2>

                <div class="achievement-grid">
                    {self._generate_achievements_html(achievements)}
                </div>
            </div>

            <!-- EDUCATION TAB -->
            <div id="education" class="tab-content">
                <h2 style="color: var(--primary); margin-bottom: 25px;">Education &amp; Certifications</h2>

                <div class="cert-grid">
                    {self._generate_education_html(education)}
                </div>

                <div class="highlight-box" style="margin-top: 30px;">
                    <h3 style="color: var(--primary); margin-bottom: 15px;">Languages</h3>
                    {self._generate_languages_html(languages)}
                </div>
            </div>
        </div>
    </div>

    <script>
        function switchTab(tabName) {{
            document.querySelectorAll('.tab-content').forEach(tab => {{
                tab.classList.remove('active');
            }});

            document.querySelectorAll('.nav-tab').forEach(navTab => {{
                navTab.classList.remove('active');
            }});

            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
        }}

        function toggleSection(header) {{
            const section = header.parentElement;
            section.classList.toggle('expanded');
        }}

        document.addEventListener('DOMContentLoaded', function() {{
            const firstSection = document.querySelector('#experience .section');
            if (firstSection) {{
                firstSection.classList.add('expanded');
            }}
        }});
    </script>
</body>
</html>
"""
        return html
    
    def _get_icon_for_company(self, company):
        """Get emoji icon for company"""
        icons = {
            'swiss re': '🏢',
            'julius baer': '🏦',
            'credit suisse': '🏛️',
            'ubs': '🏛️',
            'societe generale': '🏢',
            'horizon': '💻',
            'alternative': '📊',
            'arolys': '🔧'
        }
        company_lower = company.lower()
        for key, icon in icons.items():
            if key in company_lower:
                return icon
        return '🏢'
    
    def _generate_experience_html(self, experience):
        """Generate experience sections HTML"""
        html_parts = []
        
        for idx, exp in enumerate(experience):
            company = exp.get('Company', 'Company')
            title = exp.get('Title', 'Position')
            period = exp.get('Period', 'Date')
            project = exp.get('Project', '')
            icon = self._get_icon_for_company(company)
            
            # Extract achievements and contributions
            achievements = [exp[k] for k in exp.keys() if k.startswith('Achievement')]
            contributions = [exp[k] for k in exp.keys() if k.startswith('Contribution')]
            skills = [exp[k] for k in exp.keys() if k.startswith('Skill')]
            
            expanded_class = 'expanded' if idx == 0 else ''
            
            html = f"""
                    <div class="section {expanded_class}">
                        <div class="section-header" onclick="toggleSection(this)">
                            <h3><span class="section-icon">{icon}</span> {company} - {title}</h3>
                            <span class="toggle-icon">▼</span>
                        </div>
                        <div class="section-content">
                            <div class="timeline-date">{period}</div>
                            <div class="timeline-role">{project}</div>

                            <div class="timeline-content">
"""
            
            if contributions:
                html += """
                                <h4>Key Contributions:</h4>
                                <ul>
"""
                for contrib in contributions:
                    html += f"                                    <li>{contrib}</li>\n"
                html += """
                                </ul>
"""
            
            if achievements:
                html += """
                                <h4>Key Achievements:</h4>
                                <ul>
"""
                for ach in achievements:
                    html += f"                                    <li>✅ <strong>{ach}</strong></li>\n"
                html += """
                                </ul>
"""
            
            if skills:
                html += """
                                <div class="skill-tags">
"""
                for skill in skills:
                    html += f'                                    <span class="tag">{skill}</span>\n'
                html += """
                                </div>
"""
            
            html += """
                            </div>
                        </div>
                    </div>
"""
            html_parts.append(html)
        
        return ''.join(html_parts)
    
    def _generate_skills_html(self, skills):
        """Generate skills grid HTML"""
        html_parts = []
        icons = {
            'ORDER MANAGEMENT': '💼',
            'BANKING & INTEGRATION': '🏦',
            'DATA & GOVERNANCE': '🔎',
            'ASSET CLASSES & TRADING': '📈',
            'DERIVATIVES': '🎯',
            'MIGRATION & PROGRAMS': '🚀',
            'LEADERSHIP': '🤝',
            'TECHNICAL TOOLS': '🔧'
        }
        
        for skill in skills:
            icon = icons.get(skill['category'], '⚙️')
            level = skill['level'].lower().replace(' ', '-')
            
            html = f"""
                    <div class="skill-card">
                        <h4>{icon} {skill['category']}</h4>
                        <div class="skill-tags">
"""
            
            for s in skill['skills']:
                if level == 'expert':
                    html += f'                            <span class="tag proficiency-expert">{s}</span>\n'
                elif level == 'advanced':
                    html += f'                            <span class="tag proficiency-advanced">{s}</span>\n'
                else:
                    html += f'                            <span class="tag">{s}</span>\n'
            
            html += """
                        </div>
                    </div>
"""
            html_parts.append(html)
        
        return ''.join(html_parts)
    
    def _generate_achievements_html(self, achievements):
        """Generate achievements grid HTML"""
        html_parts = []
        gradients = ['--gradient-1', '--gradient-2', '--gradient-3']
        
        for idx, ach in enumerate(achievements):
            gradient = f'var({gradients[idx % 3]})'
            number = f"{idx + 1:02d}"
            title = ach.get('Title', 'Achievement')
            description = ach.get('Description', '')
            impact = ach.get('Impact', '')
            
            html = f"""
                    <div class="achievement-card" style="background: {gradient}; position: relative;">
                        <span class="achievement-number">{number}</span>
                        <h4>{title}</h4>
                        <p>{description}</p>
"""
            
            if impact:
                html += f'                        <p style="margin-top: 10px;"><strong>{impact} Impact</strong></p>\n'
            
            html += """
                    </div>
"""
            html_parts.append(html)
        
        return ''.join(html_parts)
    
    def _generate_education_html(self, education):
        """Generate education/certs grid HTML"""
        html_parts = []
        
        icons = {
            'PMP': '🎯',
            'PSPO': '🏅',
            'CFA': '📊',
            'Master': '🎓',
            'Bachelor': '📚',
            'Research': '🔬'
        }
        
        # Certifications
        for cert in education['certifications']:
            raw_title = cert.get('Title', '').strip()
            title_upper = raw_title.upper()

            if 'PROJECT MANAGER PROFESSIONAL' in title_upper or 'PROJECT MANAGEMENT PROFESSIONAL' in title_upper or title_upper == 'PMP':
                display_title = 'PMP (Project Management Professional)'
            else:
                display_title = raw_title

            icon = next((v for k, v in icons.items() if k in display_title.upper()), '🏆')
            year = cert.get('Year', cert.get('Years', cert.get('Date', '')))
            status = cert.get('Status', '')
            
            html = f"""
                    <div class="cert-badge">
                        <div class="cert-icon">{icon}</div>
                        <h4>{display_title}</h4>
                        <p class="cert-year">{status} ({year})</p>
                    </div>
"""
            html_parts.append(html)
        
        # Degrees
        for degree in education['degrees']:
            field = degree.get('Field', '')
            icon = '🎓' if 'Master' in degree.get('Type', '') else '📚'
            school = degree.get('School', '')
            year = degree.get('Year', '')
            
            html = f"""
                    <div class="cert-badge">
                        <div class="cert-icon">{icon}</div>
                        <h4>{field}</h4>
                        <p class="cert-year">{school} ({year})</p>
                    </div>
"""
            html_parts.append(html)
        
        # Research
        for res in education['research']:
            title = res.get('Title', '')
            year = res.get('Year', '')
            
            html = f"""
                    <div class="cert-badge">
                        <div class="cert-icon">🔬</div>
                        <h4>Research</h4>
                        <p class="cert-year">{title} ({year})</p>
                    </div>
"""
            html_parts.append(html)
        
        return ''.join(html_parts)
    
    def _generate_core_competencies_html(self, core_competencies):
        """Build Core Competencies grid from CORE COMPETENCIES section"""
        if not core_competencies:
            return ''

        card_html_parts = []
        for box in core_competencies:
            title = box.get('title', '').strip()
            items = [i for i in box.get('items', []) if i]
            if not box.get('enabled', True) or not title or not items:
                continue
            items_html = ''.join(f'<li>{item}</li>' for item in items)
            card_html_parts.append(
                f"""
                                <div class=\"skill-card\">
                                    <h4>{title}</h4>
                                    <ul style=\"margin: 0; padding-left: 20px; line-height: 1.8;\">{items_html}</ul>
                                </div>
                """
            )

        if not card_html_parts:
            return ''

        cards_html = ''.join(card_html_parts)
        html = f"""
                        <div style=\"margin-top: 30px;\">
                            <h3 style=\"color: var(--primary); margin-bottom: 20px;\">Core Competencies</h3>
                            <div class=\"skills-grid\">
{cards_html}
                            </div>
                        </div>
        """
        return html
    
    def _generate_languages_html(self, languages):
        """Generate languages from LANGUAGES section"""
        if languages:
            lang_list = []
            for lang in languages:
                language = lang.get('Language', '')
                proficiency = lang.get('Proficiency', '')
                if language:
                    lang_list.append(f"{proficiency}: {language}" if proficiency else language)
            
            if lang_list:
                return '<p>' + '<br>'.join(lang_list) + '</p>'
        
        return '<p><strong>Fluent:</strong> English &amp; German</p>'
    
    def _get_overview_description(self, summary):
        """Extract overview description from professional summary"""
        # CSV subsections are uppercase (e.g., OVERVIEW). Support both cases.
        items = summary.get('OVERVIEW') or summary.get('Overview')
        if items:
            first = items[0]
            if isinstance(first, dict):
                return first.get('value', '')
            return str(first)

        return 'Data & Delivery Lead with 10+ years in Order Management, fund monitoring, and data governance. Specialist in large-scale migrations, system integration, and cross-functional team leadership. Fluent in English and German.'

    def _render_overview_html(self, summary):
        """Render professional summary as paragraph or bullet list"""
        description = self._get_overview_description(summary)
        lines = [line.strip() for line in str(description).splitlines() if line.strip()]

        if not lines:
            return '<p style="font-size: 1.1em; line-height: 1.8;"></p>'

        bullet_items = []
        for line in lines:
            normalized = line.lstrip()
            if normalized.startswith('•'):
                item = normalized[1:].strip()
            elif normalized.startswith('-'):
                item = normalized[1:].strip()
            else:
                bullet_items = []
                break

            if item:
                bullet_items.append(item)

        if bullet_items:
            html = '<ul style="font-size: 1.1em; line-height: 1.8; margin: 0; padding-left: 24px;">\n'
            for item in bullet_items:
                html += f'                        <li>{escape(item)}</li>\n'
            html += '                    </ul>'
            return html

        safe_text = '<br>'.join(escape(line) for line in lines)
        return f'<p style="font-size: 1.1em; line-height: 1.8;">{safe_text}</p>'
    
    def save_html(self, output_file):
        """Generate and save HTML file"""
        html = self.generate_html()
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"[OK] HTML file generated: {output_file}")


def main():
    """Main function"""
    script_dir = Path(__file__).parent
    csv_file = script_dir / 'Joseph_Tanios_CV_Complete_Extract.csv'
    html_output = script_dir / 'Joseph_Tanios_Interactive_CV_Auto.html'
    index_output = script_dir / 'index.html'
    
    if not csv_file.exists():
        print(f"[ERROR] CSV file not found: {csv_file}")
        return
    
    print(f"[READ] CSV file: {csv_file}")
    
    # Generate HTML
    converter = CSVToHTMLConverter(csv_file)
    converter.save_html(html_output)
    converter.save_html(index_output)
    
    # Generate PDF
    try:
        from pdf_generator import CSVToPDFConverter
        pdf_output = script_dir / 'Joseph_Tanios_Interactive_CV_Auto.pdf'
        pdf_converter = CSVToPDFConverter(csv_file)
        pdf_converter.save_pdf(pdf_output)
    except ImportError:
        print("[WARN] PDF generator module not available")
    except Exception as e:
        print(f"[WARN] PDF generation failed: {e}")
    
    print(f"[OK] Done!")


if __name__ == '__main__':
    main()
