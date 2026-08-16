import os

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

id_cards = [
    ("seed_id_front_alex.jpg", "Alex Rivera", "A7X9K", "Delhi University", "FRONT", "Student Identity Card", "Valid Thru: 2027"),
    ("seed_id_back_alex.jpg", "Alex Rivera", "A7X9K", "Delhi University", "BACK", "Emergency Contact & Barcode", "DU/CS/2026/0491"),
    ("seed_id_front_jordan.jpg", "Jordan Lee", "R4T2P", "Stanford University", "FRONT", "Stanford Student ID", "Valid Thru: 2027"),
    ("seed_id_back_jordan.jpg", "Jordan Lee", "R4T2P", "Stanford University", "BACK", "Library & Building Access", "SU-CARD-89211"),
    ("seed_id_front_priya.jpg", "Priya Sharma", "9B3KZ", "IIT Delhi", "FRONT", "IITD Smart Campus Card", "Valid Thru: 2026"),
    ("seed_id_back_priya.jpg", "Priya Sharma", "9B3KZ", "IIT Delhi", "BACK", "Hostel & Access Protocol", "2022CS10842"),
    ("seed_id_front_marcus.jpg", "Marcus Vance", "M8V1Y", "NYU Stern", "FRONT", "NYU Campus Card", "Valid Thru: 2028"),
    ("seed_id_back_marcus.jpg", "Marcus Vance", "M8V1Y", "NYU Stern", "BACK", "Stern Building Clearance", "N18290412")
]

for filename, name, code, uni, side, title, barcode in id_cards:
    fpath = os.path.join(UPLOAD_FOLDER, filename)
    svg = f"""<svg width="500" height="300" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <linearGradient id="grad_{code}_{side}" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#0e1828;stop-opacity:1" />
                <stop offset="100%" style="stop-color:#1e293b;stop-opacity:1" />
            </linearGradient>
        </defs>
        <rect width="500" height="300" rx="16" fill="url(#grad_{code}_{side})" />
        <rect x="15" y="15" width="470" height="270" rx="12" fill="#ffffff" />
        
        <rect x="15" y="15" width="470" height="50" rx="12" fill="#0e1828" />
        <text x="35" y="46" font-family="'Helvetica Neue', Arial, sans-serif" font-size="16" font-weight="bold" fill="#ffffff">{uni}</text>
        <rect x="380" y="28" width="90" height="24" rx="6" fill="#38bdf8" />
        <text x="425" y="44" font-family="sans-serif" font-size="11" font-weight="bold" fill="#0e1828" text-anchor="middle">{side} SIDE</text>
        
        <rect x="35" y="85" width="100" height="120" rx="8" fill="#e2e8f0" stroke="#cbd5e1" />
        <circle cx="85" cy="130" r="30" fill="#94a3b8" />
        <path d="M50 195 a35 35 0 0 1 70 0" fill="#64748b" />
        
        <text x="155" y="110" font-family="sans-serif" font-size="18" font-weight="bold" fill="#0f172a">{name}</text>
        <text x="155" y="132" font-family="sans-serif" font-size="13" color="#64748b" fill="#64748b">Candidate ID: <tspan font-weight="bold" fill="#0284c7">{code}</tspan></text>
        <text x="155" y="152" font-family="sans-serif" font-size="12" fill="#64748b">{title}</text>
        <text x="155" y="172" font-family="sans-serif" font-size="12" fill="#15803d" font-weight="bold">VERIFIED STUDENT</text>
        
        <line x1="35" y1="230" x2="465" y2="230" stroke="#e2e8f0" stroke-width="1.5" />
        <text x="35" y="258" font-family="monospace" font-size="12" fill="#334155">||||| ||||||| |||| |||||| ||||| {barcode}</text>
        <text x="465" y="258" font-family="sans-serif" font-size="11" fill="#94a3b8" text-anchor="end">MATCHPOINT ID SYSTEM</text>
    </svg>"""
    with open(fpath, "w", encoding="utf-8") as f:
        f.write(svg)

print("ID Card mock files generated successfully.")
