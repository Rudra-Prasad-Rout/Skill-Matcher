"""
Create realistic sample certificate and transcript files in static/uploads
"""
import os

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Generate sample files
seed_files = [
    ("seed_alex_transcript_2026.pdf", "Alex Rivera", "Delhi University", "Bachelor of Technology in Computer Science & Engineering", "9.4 CGPA - First Class with Distinction", "PDF Verification: PASSED"),
    ("seed_stanford_degree_proof.pdf", "Jordan Lee", "Stanford University", "Bachelor of Science in Symbolic Systems (AI Track)", "Dean's Honor List - Summa Cum Laude", "PDF Verification: PASSED"),
    ("seed_iitd_marksheet_verified.pdf", "Priya Sharma", "Indian Institute of Technology Delhi", "B.Tech Computer Science & Engineering", "Rank 1 Departmental Honors", "PDF Verification: PASSED"),
    ("seed_nyu_enrollment_verification.pdf", "Marcus Vance", "NYU Stern School of Business", "BS Information Systems & Financial Technology", "Active Matriculated Status", "PDF Verification: IN PROGRESS"),
    ("seed_scanned_id_unclear.jpg", "Elena Rostova", "University of Oxford", "MSc Artificial Intelligence", "Document Scan Low Resolution / Unreadable", "PDF Verification: REJECTED")
]

for filename, name, institution, degree, honors, verif in seed_files:
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    
    # We can write an SVG/HTML certificate or valid mock file
    if filename.endswith(".pdf"):
        # Create a standard PDF or HTML-based document
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Verification Document — {name}</title>
    <style>
        body {{
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            background: #f8fafc;
            margin: 0;
            padding: 40px 20px;
            display: flex;
            justify-content: center;
        }}
        .certificate-container {{
            background: #ffffff;
            width: 800px;
            padding: 50px;
            border: 2px solid #0f172a;
            border-radius: 12px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.08);
            position: relative;
        }}
        .header {{
            text-align: center;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .institution {{
            font-size: 24px;
            font-weight: 800;
            color: #0f172a;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .sub-inst {{
            font-size: 14px;
            color: #64748b;
            margin-top: 4px;
        }}
        .title {{
            font-size: 20px;
            font-weight: 700;
            color: #1e293b;
            text-align: center;
            margin-bottom: 30px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .content {{
            font-size: 16px;
            line-height: 1.8;
            color: #334155;
            text-align: center;
        }}
        .student-name {{
            font-size: 26px;
            font-weight: 800;
            color: #0e1828;
            border-bottom: 2px solid #0e1828;
            display: inline-block;
            padding: 0 20px 4px 20px;
            margin: 10px 0;
        }}
        .details-grid {{
            margin-top: 30px;
            background: #f8fafc;
            border-radius: 8px;
            padding: 20px;
            text-align: left;
            font-size: 14px;
        }}
        .footer {{
            margin-top: 40px;
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
            padding-top: 20px;
            border-top: 1px solid #e2e8f0;
        }}
        .badge {{
            display: inline-block;
            padding: 6px 14px;
            background: #dcfce7;
            color: #15803d;
            font-weight: 700;
            border-radius: 6px;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="certificate-container">
        <div class="header">
            <div class="institution">{institution}</div>
            <div class="sub-inst">OFFICIAL ACADEMIC TRANSCRIPT & COURSEWORK VERIFICATION</div>
        </div>
        <div class="title">Certificate of Academic Records</div>
        <div class="content">
            This document certifies the official enrollment and coursework completion of:
            <br>
            <div class="student-name">{name}</div>
            <br>
            in the program of
            <br>
            <strong style="font-size: 18px; color: #0f172a;">{degree}</strong>
        </div>
        <div class="details-grid">
            <div><strong>Academic Standing:</strong> {honors}</div>
            <div style="margin-top: 8px;"><strong>Verification Status:</strong> {verif}</div>
            <div style="margin-top: 8px;"><strong>Digital Signature Hash:</strong> <code>0x7f8a91b2c3d4e5f6...VERIFIED</code></div>
        </div>
        <div class="footer">
            <div>
                <div class="badge">OFFICIALLY ATTESTED</div>
            </div>
            <div style="text-align: right; font-size: 13px; color: #64748b;">
                Office of the University Registrar<br>
                Issued for Matchpoint Verification
            </div>
        </div>
    </div>
</body>
</html>
"""
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html_content)
    else:
        # For jpg image placeholder
        svg_content = f"""<svg width="600" height="400" xmlns="http://www.w3.org/2000/svg">
            <rect width="600" height="400" fill="#fee2e2"/>
            <text x="300" y="160" font-family="sans-serif" font-size="20" font-weight="bold" fill="#b91c1c" text-anchor="middle">SCANNED DOCUMENT PREVIEW</text>
            <text x="300" y="200" font-family="sans-serif" font-size="16" fill="#7f1d1d" text-anchor="middle">Candidate: {name}</text>
            <text x="300" y="230" font-family="sans-serif" font-size="14" fill="#991b1b" text-anchor="middle">{institution}</text>
            <text x="300" y="270" font-family="sans-serif" font-size="13" fill="#b91c1c" text-anchor="middle">Notice: Image low contrast / requires re-upload</text>
        </svg>"""
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(svg_content)

print("Created realistic sample documents.")
