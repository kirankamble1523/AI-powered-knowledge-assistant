import os
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_sample_pdfs(target_dir: Path):
    target_dir.mkdir(exist_ok=True)
    
    # Check if files already exist to avoid rewriting them
    hr_path = target_dir / "HR_Policy.pdf"
    customer_path = target_dir / "Customer_Policy.pdf"
    product_path = target_dir / "Product_Docs.pdf"
    compliance_path = target_dir / "Compliance_Guidelines.pdf"
    
    if hr_path.exists() and customer_path.exists() and product_path.exists() and compliance_path.exists():
        print("[PDF Generator] Sample PDFs already exist. Skipping generation.")
        return

    print("[PDF Generator] Generating mock enterprise PDF documents...")
    styles = getSampleStyleSheet()
    
    # Custom Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=24,
        leading=28,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=20
    )
    
    heading_style = ParagraphStyle(
        'DocHeading',
        parent=styles['Heading2'],
        fontSize=16,
        leading=20,
        textColor=colors.HexColor('#333333'),
        spaceBefore=15,
        spaceAfter=10
    )
    
    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['BodyText'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#4c4c4c'),
        spaceAfter=8
    )

    # 1. Generate HR_Policy.pdf (15 Pages, leave policy on page 12)
    doc_hr = SimpleDocTemplate(str(hr_path), pagesize=letter)
    hr_story = []
    
    # Title Page (Page 1)
    hr_story.append(Paragraph("AnthraSync Inc.", title_style))
    hr_story.append(Paragraph("Official Employee Handbook & HR Policy Guidelines", heading_style))
    hr_story.append(Spacer(1, 40))
    hr_story.append(Paragraph("Document Version: 2026.1", body_style))
    hr_story.append(Paragraph("Classification: Internal Confidential", body_style))
    hr_story.append(PageBreak())  # Page 2
    
    # Intermediate Pages (Pages 2 to 11)
    for p in range(2, 12):
        hr_story.append(Paragraph(f"Chapter {p-1}: Company Policies & Standards", heading_style))
        hr_story.append(Spacer(1, 10))
        hr_story.append(Paragraph(f"This page (Page {p}) covers details regarding company standard operation procedure number 00{p}. Employees are expected to adhere to all terms described herein. Standards are subject to change by HR management.", body_style))
        hr_story.append(Paragraph("Please consult the HR Portal for real-time updates. Direct questions to hr@anthrasync.com.", body_style))
        hr_story.append(PageBreak())  # Go to next page
        
    # Page 12: Employee Leave Policy (CRITICAL ANSWER HERE)
    hr_story.append(Paragraph("Chapter 11: Employee Benefits & Paid Time Off", heading_style))
    hr_story.append(Spacer(1, 15))
    hr_story.append(Paragraph("Section 11.2: Annual Paid Leaves", heading_style))
    hr_story.append(Paragraph("<b>Section 8.4: Annual Leave Policy.</b> Employees are eligible for 24 paid leaves annually. Vacation requests must be submitted at least two weeks in advance. Unused leaves do not roll over to the next calendar year.", body_style))
    hr_story.append(Paragraph("Sick leaves and casual leaves are covered separately under Section 11.3. Parental leaves details are found on Page 13.", body_style))
    hr_story.append(PageBreak())  # Page 13
    
    # Remaining Pages (Pages 13 to 15)
    for p in range(13, 16):
        hr_story.append(Paragraph(f"Chapter {p-1}: Additional HR Provisions", heading_style))
        hr_story.append(Spacer(1, 10))
        hr_story.append(Paragraph(f"This section (Page {p}) covers minor provisions, travel reimbursement procedures, and remote work infrastructure allowances. All claims must be submitted with original receipts within 30 days of expense.", body_style))
        if p < 15:
            hr_story.append(PageBreak())
            
    doc_hr.build(hr_story)
    print(f"[PDF Generator] Generated HR_Policy.pdf at {hr_path} (15 pages)")

    # 2. Generate Customer_Policy.pdf (8 Pages, refund policy on page 5)
    doc_cust = SimpleDocTemplate(str(customer_path), pagesize=letter)
    cust_story = []
    
    # Title Page (Page 1)
    cust_story.append(Paragraph("AnthraSync Customer Terms & Conditions", title_style))
    cust_story.append(Paragraph("Standard Customer Agreement, Service Terms, and Return Policy", heading_style))
    cust_story.append(Spacer(1, 30))
    cust_story.append(PageBreak())  # Page 2
    
    # Intermediate Pages (Pages 2 to 4)
    for p in range(2, 5):
        cust_story.append(Paragraph(f"Section {p-1}: Service Delivery Terms", heading_style))
        cust_story.append(Paragraph(f"This page (Page {p}) outlines the customer delivery commitments and quality of service (QoS) guarantees. AnthraSync strives to resolve service tickets within 24 hours.", body_style))
        cust_story.append(PageBreak())
        
    # Page 5: Refund Policy (CRITICAL ANSWER HERE)
    cust_story.append(Paragraph("Section 4: Return and Refund Policy", heading_style))
    cust_story.append(Spacer(1, 15))
    cust_story.append(Paragraph("<b>Section 3.2: Refund Policy.</b> Refunds are allowed within 30 days of purchase. The product must be returned in its original packaging and with all accessories. Allow 5-7 business days for processing.", body_style))
    cust_story.append(Paragraph("Subscriptions can be canceled at any time, but refunds will not be prorated for partial months.", body_style))
    cust_story.append(PageBreak())  # Page 6
    
    # Remaining Pages (Pages 6 to 8)
    for p in range(6, 9):
        cust_story.append(Paragraph(f"Section {p-1}: Warranty and Legal Provisions", heading_style))
        cust_story.append(Paragraph(f"Legal notice (Page {p}): Limitation of liability and standard dispute resolution mechanisms. Governed by state laws.", body_style))
        if p < 8:
            cust_story.append(PageBreak())
            
    doc_cust.build(cust_story)
    print(f"[PDF Generator] Generated Customer_Policy.pdf at {customer_path} (8 pages)")

    # 3. Generate Product_Docs.pdf (4 Pages)
    doc_prod = SimpleDocTemplate(str(product_path), pagesize=letter)
    prod_story = []
    prod_story.append(Paragraph("AnthraSync Product Documentation", title_style))
    prod_story.append(Paragraph("Product Overview, Core Features & API specifications", heading_style))
    prod_story.append(PageBreak()) # Page 2
    prod_story.append(Paragraph("System Architecture", heading_style))
    prod_story.append(Paragraph("AnthraSync Core v4.2 is built on a distributed microservices framework using Python, Docker, and Kubernetes. The primary databases are PostgreSQL for relational storage and Redis for high-speed caching.", body_style))
    prod_story.append(PageBreak()) # Page 3
    prod_story.append(Paragraph("API Reference", heading_style))
    prod_story.append(Paragraph("Base URL: https://api.anthrasync.com/v1. Endpoints support JSON payloads. Standard rate limit is 10,000 requests per hour per API client.", body_style))
    prod_story.append(PageBreak()) # Page 4
    prod_story.append(Paragraph("Troubleshooting FAQ", heading_style))
    prod_story.append(Paragraph("For connection timeout errors, verify your client API token and check if the cluster status page at status.anthrasync.com is operational.", body_style))
    doc_prod.build(prod_story)
    print(f"[PDF Generator] Generated Product_Docs.pdf at {product_path} (4 pages)")

    # 4. Generate Compliance_Guidelines.pdf (3 Pages)
    doc_comp = SimpleDocTemplate(str(compliance_path), pagesize=letter)
    comp_story = []
    comp_story.append(Paragraph("AnthraSync Security & Compliance Guidelines", title_style))
    comp_story.append(Paragraph("Corporate Compliance, Data Security, and Employee Protocols", heading_style))
    comp_story.append(PageBreak()) # Page 2
    comp_story.append(Paragraph("Section 1: Data Protection & Password Policy", heading_style))
    comp_story.append(Paragraph("Section 1.1: Authentication. All corporate account passwords must be at least 12 characters long and contain a mix of uppercase letters, lowercase letters, numbers, and special characters. Passwords must be rotated every 90 days. Multi-Factor Authentication (MFA) is mandatory for all access points.", body_style))
    comp_story.append(PageBreak()) # Page 3
    comp_story.append(Paragraph("Section 2: Data Retention & Disposal", heading_style))
    comp_story.append(Paragraph("Section 2.1: Retention Period. Customer personal data is retained for a maximum of 3 years after account termination. Compliance logs are archived for 7 years to meet regulatory requirements.", body_style))
    doc_comp.build(comp_story)
    print(f"[PDF Generator] Generated Compliance_Guidelines.pdf at {compliance_path} (3 pages)")

if __name__ == "__main__":
    generate_sample_pdfs(Path("../data"))
