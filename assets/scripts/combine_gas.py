#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to combine gas_redesign.html (design) with complete content from gas.html
"""

from bs4 import BeautifulSoup
import re
from datetime import datetime

def read_file(filepath):
    """Read HTML file with UTF-8 encoding"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(filepath, content):
    """Write HTML file with UTF-8 encoding"""
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

def extract_informativos_from_original(html_content):
    """Extract all informativos from original gas.html"""
    soup = BeautifulSoup(html_content, 'html.parser')

    informativos = []

    # Find the INFORMATIVOS dropdown button and its content
    buttons = soup.find_all('button', class_='dropbtn')
    for button in buttons:
        if 'INFORMATIVOS' in button.get_text():
            # Find the associated dropdown-content div
            dropdown = button.find_next('div', class_='dropdown-content')
            if dropdown:
                # Extract all dropdown items and their content
                items = dropdown.find_all('a', class_='dropdown-item')
                for item in items:
                    # Get informativo title
                    title = item.get_text().strip()

                    # Get the content div ID from onclick attribute
                    onclick = item.get('onclick', '')
                    match = re.search(r"toggleContent\('([^']+)'\)", onclick)
                    if match:
                        content_id = match.group(1)
                        # Find the corresponding content div
                        content_div = dropdown.find('div', id=content_id)
                        if content_div:
                            informativos.append({
                                'title': title,
                                'content_div': content_div,
                                'html': str(content_div)
                            })
            break

    return informativos

def extract_other_sections(html_content):
    """Extract Editais, Relação de Credores, Avisos, Ação Civil Pública"""
    soup = BeautifulSoup(html_content, 'html.parser')

    sections = {}
    buttons = soup.find_all('button', class_='dropbtn')

    for button in buttons:
        button_text = button.get_text().strip()
        if button_text in ['EDITAIS', 'RELAÇÃO DE CREDORES', 'AVISOS', 'AÇÃO CIVIL PÚBLICA',
                           'TUTELA CAUTELAR ANTECEDENTE À RECUPERAÇÃO JUDICIAL', 'DECISÕES JUDICIAIS']:
            dropdown = button.find_next('div', class_='dropdown-content')
            if dropdown:
                items = dropdown.find_all('a', class_='dropdown-item')
                section_items = []
                for item in items:
                    title = item.get_text().strip()
                    onclick = item.get('onclick', '')
                    match = re.search(r"toggleContent\('([^']+)'\)", onclick)
                    if match:
                        content_id = match.group(1)
                        content_div = dropdown.find('div', id=content_id)
                        if content_div:
                            section_items.append({
                                'title': title,
                                'html': str(content_div)
                            })
                sections[button_text] = section_items

    return sections

def create_informativos_html(informativos):
    """Create informativos section in redesign format"""
    html_parts = []

    for i, info in enumerate(informativos):
        title = info['title']
        # Extract just the content paragraphs and other elements from the content div
        soup = BeautifulSoup(info['html'], 'html.parser')
        body_content = soup.find('div', class_='content')

        # Get inner HTML without the wrapper div
        if body_content:
            body_html = ''.join(str(child) for child in body_content.children)
        else:
            body_html = info['html']

        # Extract date if available from title or content
        date_match = re.search(r'(\d{1,2}/\d{1,2}/\d{4})', body_html)
        date = date_match.group(1) if date_match else ''

        # Clean up the informativo title
        title_clean = title.replace('INFORMATIVO ', 'Informativo ')

        doc_item = f'''                    <div class="doc-item">
                        <div class="doc-item-header" onclick="toggleDoc(this)">
                            <span class="doc-date">{date}</span>
                            <span class="doc-name">{title_clean}</span>
                            <span class="doc-toggle">+</span>
                        </div>
                        <div class="doc-item-body">
                            {body_html}
                            <strong>ADMINISTRAÇÃO JUDICIAL CONJUNTA DA GAS CONSULTORIA E TECNOLOGIA LTDA.</strong>
                        </div>
                    </div>
'''
        html_parts.append(doc_item)

    return '\n'.join(html_parts)

def create_section_html(section_items, section_name):
    """Create HTML for PDF sections (Editais, Decisões, etc.)"""
    html_parts = []

    for item in section_items:
        title = item['title']
        soup = BeautifulSoup(item['html'], 'html.parser')
        body = soup.find('div', class_='content')

        if body:
            body_html = ''.join(str(child) for child in body.children)
        else:
            body_html = item['html']

        # Extract date if available
        date_match = re.search(r'(\d{1,2}/\d{1,2}/\d{4})', body_html)
        date = date_match.group(1) if date_match else ''

        doc_item = f'''                    <div class="doc-item">
                        <div class="doc-item-header" onclick="toggleDoc(this)">
                            <span class="doc-date">{date}</span>
                            <span class="doc-name">{title}</span>
                            <span class="doc-toggle">+</span>
                        </div>
                        <div class="doc-item-body">
                            {body_html}
                        </div>
                    </div>
'''
        html_parts.append(doc_item)

    return '\n'.join(html_parts)

def fix_email_links(html_content):
    """Replace email links with gold color style"""
    # Replace mailto links with gold style
    html_content = re.sub(
        r'<a\s+href="mailto:([^"]+)"[^>]*>([^<]+)</a>',
        r'<a href="mailto:\1" style="color:var(--gold-light);">\2</a>',
        html_content
    )

    # Replace old color styles on email links
    html_content = re.sub(
        r'<a\s+href="mailto:([^"]+)"\s+style="color:#0066cc;"',
        r'<a href="mailto:\1" style="color:var(--gold-light);"',
        html_content
    )

    # Also fix the email addresses without links
    html_content = re.sub(
        r'<strong>sacgas@zveiter\.adv\.br</strong>',
        r'<a href="mailto:sacgas@zveiter.adv.br" style="color:var(--gold-light);"><strong>sacgas@zveiter.adv.br</strong></a>',
        html_content
    )

    return html_content

def combine_files(redesign_path, original_path, output_path):
    """Main function to combine files"""

    print("Reading files...")
    redesign_html = read_file(redesign_path)
    original_html = read_file(original_path)

    print("Extracting informativos from original...")
    informativos = extract_informativos_from_original(original_html)
    print(f"Found {len(informativos)} informativos")

    print("Extracting other sections from original...")
    sections = extract_other_sections(original_html)
    print(f"Found sections: {list(sections.keys())}")

    # Parse redesign file to get the structure
    soup = BeautifulSoup(redesign_html, 'html.parser')

    # Find the page-content div
    page_content = soup.find('div', class_='page-content')

    if page_content:
        # Build new sidebar navigation
        sidebar_nav = '''                <ul class="doc-nav">
                    <li class="nav-label">Processo</li>
                    <li>
                        <a href="#" onclick="showPanel('informativos', this); return false;">
                            Informativos
                            <span class="count">{}</span>
                        </a>
                    </li>
                    <li class="nav-label">Documentos</li>
                    <li>
                        <a href="#" onclick="showPanel('editais', this); return false;">
                            Editais
                            <span class="count">{}</span>
                        </a>
                    </li>
                    <li>
                        <a href="#" onclick="showPanel('relacao-credores', this); return false;">
                            Relação de Credores
                            <span class="count">{}</span>
                        </a>
                    </li>
                    <li>
                        <a href="#" onclick="showPanel('avisos', this); return false;">
                            Avisos
                            <span class="count">{}</span>
                        </a>
                    </li>
                    <li class="nav-label">Ações Judiciais</li>
                    <li>
                        <a href="#" onclick="showPanel('acao-civil-publica', this); return false;">
                            Ação Civil Pública
                            <span class="count">{}</span>
                        </a>
                    </li>
                    <li>
                        <a href="#" onclick="showPanel('tutela-cautelar', this); return false;">
                            Tutela Cautelar
                            <span class="count">{}</span>
                        </a>
                    </li>
                    <li class="nav-label">Decisões</li>
                    <li>
                        <a href="#" onclick="showPanel('decisoes', this); return false;">
                            Decisões Judiciais
                            <span class="count">{}</span>
                        </a>
                    </li>
                </ul>'''.format(
            len(informativos),
            len(sections.get('EDITAIS', [])),
            len(sections.get('RELAÇÃO DE CREDORES', [])),
            len(sections.get('AVISOS', [])),
            len(sections.get('AÇÃO CIVIL PÚBLICA', [])),
            len(sections.get('TUTELA CAUTELAR ANTECEDENTE À RECUPERAÇÃO JUDICIAL', [])),
            len(sections.get('DECISÕES JUDICIAIS', []))
        )

        # Build panels HTML
        panels_html = '''
                <!-- Informativos Panel -->
                <div id="informativos-panel" class="doc-panel active">
                    <div class="panel-header">
                        <h2>Informativos</h2>
                        <p class="panel-subtitle">Comunicados da Administração Judicial</p>
                    </div>
                    <div class="doc-list">
{}
                    </div>
                </div>

                <!-- Editais Panel -->
                <div id="editais-panel" class="doc-panel">
                    <div class="panel-header">
                        <h2>Editais</h2>
                        <p class="panel-subtitle">Editais do processo falimentar</p>
                    </div>
                    <div class="doc-list">
{}
                    </div>
                </div>

                <!-- Relação de Credores Panel -->
                <div id="relacao-credores-panel" class="doc-panel">
                    <div class="panel-header">
                        <h2>Relação de Credores</h2>
                        <p class="panel-subtitle">Documentos e listas de credores</p>
                    </div>
                    <div class="doc-list">
{}
                    </div>
                </div>

                <!-- Avisos Panel -->
                <div id="avisos-panel" class="doc-panel">
                    <div class="panel-header">
                        <h2>Avisos</h2>
                        <p class="panel-subtitle">Avisos e comunicações</p>
                    </div>
                    <div class="doc-list">
{}
                    </div>
                </div>

                <!-- Ação Civil Pública Panel -->
                <div id="acao-civil-publica-panel" class="doc-panel">
                    <div class="panel-header">
                        <h2>Ação Civil Pública</h2>
                        <p class="panel-subtitle">Documentos e decisões</p>
                    </div>
                    <div class="doc-list">
{}
                    </div>
                </div>

                <!-- Tutela Cautelar Panel -->
                <div id="tutela-cautelar-panel" class="doc-panel">
                    <div class="panel-header">
                        <h2>Tutela Cautelar Antecedente</h2>
                        <p class="panel-subtitle">Documentos e decisões</p>
                    </div>
                    <div class="doc-list">
{}
                    </div>
                </div>

                <!-- Decisões Judiciais Panel -->
                <div id="decisoes-panel" class="doc-panel">
                    <div class="panel-header">
                        <h2>Decisões Judiciais</h2>
                        <p class="panel-subtitle">Decisões e acórdãos</p>
                    </div>
                    <div class="doc-list">
{}
                    </div>
                </div>
'''.format(
            create_informativos_html(informativos),
            create_section_html(sections.get('EDITAIS', []), 'EDITAIS'),
            create_section_html(sections.get('RELAÇÃO DE CREDORES', []), 'RELAÇÃO DE CREDORES'),
            create_section_html(sections.get('AVISOS', []), 'AVISOS'),
            create_section_html(sections.get('AÇÃO CIVIL PÚBLICA', []), 'AÇÃO CIVIL PÚBLICA'),
            create_section_html(sections.get('TUTELA CAUTELAR ANTECEDENTE À RECUPERAÇÃO JUDICIAL', []), 'TUTELA CAUTELAR'),
            create_section_html(sections.get('DECISÕES JUDICIAIS', []), 'DECISÕES JUDICIAIS')
        )

        # Find the sidebar and panels containers
        sidebar = page_content.find('aside', class_='doc-sidebar')
        main_content = page_content.find('div', class_='doc-main')

        if sidebar:
            # Replace sidebar nav
            sidebar_ul = sidebar.find('ul', class_='doc-nav')
            if sidebar_ul:
                sidebar_ul.replace_with(BeautifulSoup(sidebar_nav, 'html.parser'))

        if main_content:
            # Clear and replace main content
            main_content.clear()
            main_content.append(BeautifulSoup(panels_html, 'html.parser'))

        # Convert soup back to string
        output_html = str(soup.prettify())

        # Fix email links colors
        output_html = fix_email_links(output_html)

        # Save output
        print(f"Writing output to {output_path}...")
        write_file(output_path, output_html)

        # Count doc-items for verification
        doc_items = output_html.count('class="doc-item"')
        print(f"\nSuccess! Generated {output_path}")
        print(f"Total doc-items: {doc_items}")
        print(f"  - Informativos: {len(informativos)}")
        print(f"  - Editais: {len(sections.get('EDITAIS', []))}")
        print(f"  - Relação de Credores: {len(sections.get('RELAÇÃO DE CREDORES', []))}")
        print(f"  - Avisos: {len(sections.get('AVISOS', []))}")
        print(f"  - Ação Civil Pública: {len(sections.get('AÇÃO CIVIL PÚBLICA', []))}")
        print(f"  - Tutela Cautelar: {len(sections.get('TUTELA CAUTELAR ANTECEDENTE À RECUPERAÇÃO JUDICIAL', []))}")
        print(f"  - Decisões Judiciais: {len(sections.get('DECISÕES JUDICIAIS', []))}")

        # File size info
        import os
        output_size = os.path.getsize(output_path)
        print(f"Output file size: {output_size / 1024:.1f} KB")

if __name__ == '__main__':
    redesign_path = '/sessions/blissful-friendly-maxwell/mnt/SiteZveiter/gas_redesign.html'
    original_path = '/sessions/blissful-friendly-maxwell/mnt/SiteZveiter/gas.html'
    output_path = '/sessions/blissful-friendly-maxwell/mnt/SiteZveiter/gas_redesign.html'

    combine_files(redesign_path, original_path, output_path)
