"""
Service for PDF generation from profile summaries
"""
import io
import logging
from typing import Optional
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER

from ..models.candidate_raw_data import ProfileSummary


class PDFGenerationService:
    """Service for generating PDF documents from profile summaries"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles for the PDF"""
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )
        
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            spaceBefore=20,
            textColor=colors.darkblue,
            leftIndent=0
        )
        
        self.body_style = ParagraphStyle(
            'CustomBody',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            leftIndent=10
        )
    
    def _parse_profile_sections(self, summary_text: str) -> dict:
        """Parse the profile summary text into sections"""
        sections = {}
        current_section = None
        current_content = []
        
        lines = summary_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if line is a section header
            if (line in ['Professional Summary', 'Education', 'Key Strengths', 
                        'Technical Skills', 'Professional Experience', 'Project Summary'] or
                line.endswith(':')):
                # Save previous section
                if current_section:
                    sections[current_section] = '\n'.join(current_content)
                
                # Start new section
                current_section = line.rstrip(':')
                current_content = []
            else:
                # Add to current section content
                current_content.append(line)
        
        # Save last section
        if current_section:
            sections[current_section] = '\n'.join(current_content)
        
        return sections
    
    def generate_profile_pdf(self, profile_summary: ProfileSummary, candidate_email: str) -> bytes:
        """Generate PDF from profile summary"""
        
        # Create PDF buffer
        buffer = io.BytesIO()
        
        # Create document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Container for the 'Flowable' objects
        elements = []
        
        # Title
        title = Paragraph("Professional Profile", self.title_style)
        elements.append(title)
        elements.append(Spacer(1, 12))
        
        # Candidate info
        info_data = [
            ['Email:', candidate_email],
            ['Generated:', datetime.utcnow().strftime('%B %d, %Y')],
            ['Model:', profile_summary.llm_model]
        ]
        
        info_table = Table(info_data, colWidths=[1.5*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        elements.append(info_table)
        elements.append(Spacer(1, 20))
        
        # Parse and add sections
        sections = self._parse_profile_sections(profile_summary.summary_text)
        
        section_order = [
            'Professional Summary',
            'Education', 
            'Key Strengths',
            'Technical Skills',
            'Professional Experience',
            'Project Summary'
        ]
        
        for section_name in section_order:
            if section_name in sections:
                # Section heading
                heading = Paragraph(section_name, self.heading_style)
                elements.append(heading)
                
                # Section content
                content = sections[section_name]
                if content:
                    # Handle technical skills table format
                    if section_name == 'Technical Skills':
                        elements.append(self._create_technical_skills_table(content))
                    else:
                        # Regular paragraph content
                        for line in content.split('\n'):
                            if line.strip():
                                para = Paragraph(line.strip(), self.body_style)
                                elements.append(para)
                
                elements.append(Spacer(1, 12))
        
        # Add any remaining sections not in the standard order
        for section_name, content in sections.items():
            if section_name not in section_order and content:
                heading = Paragraph(section_name, self.heading_style)
                elements.append(heading)
                
                for line in content.split('\n'):
                    if line.strip():
                        para = Paragraph(line.strip(), self.body_style)
                        elements.append(para)
                
                elements.append(Spacer(1, 12))
        
        # Build PDF
        try:
            doc.build(elements)
            pdf_data = buffer.getvalue()
            buffer.close()
            return pdf_data
        except Exception as e:
            logging.error(f"Error generating PDF: {str(e)}")
            raise Exception(f"PDF generation failed: {str(e)}")
    
    def _create_technical_skills_table(self, content: str) -> Table:
        """Create a formatted table for technical skills section"""
        skills_data = []
        
        for line in content.split('\n'):
            line = line.strip()
            if ':' in line:
                skill_type, skills = line.split(':', 1)
                skills_data.append([skill_type.strip() + ':', skills.strip()])
            elif line:
                skills_data.append([line, ''])
        
        if not skills_data:
            return Paragraph(content, self.body_style)
        
        table = Table(skills_data, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ]))
        
        return table


# Global service instance
pdf_generation_service = PDFGenerationService()