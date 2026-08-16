# S30 — Student Verification & Opportunities Platform

A modern, high-performance web platform for student identity verification, project validation, and automated internship matching.

---

## 🚀 Key Features

- **Futuristic Glassmorphism UI**: Ambient glowing orbs, frosted glass panels, and high-contrast dark aesthetic.
- **5-Digit Alphanumeric ID System**: Auto-generates unique 5-character alphanumeric candidate IDs (e.g. `A7X9K`, `9B3KZ`, `R4T2P`).
- **Student Onboarding (Steps 1–4)**:
  - Step 1: Profile information, college email validation, gender, age, and password confirmation.
  - Step 2: Skills & Project proofs with direct GitHub/website links.
  - Step 3: College ID card (Front & Back) and certificate upload with deduplication.
  - Step 4: Live verification status tracking.
- **Secure Admin Portal (`TeamX` / `TeamX@Admin`)**:
  - 3-Horizontal-Lines (`☰`) Hamburger drawer navigation menu.
  - **Approvals Queue**: Inspect ID cards with built-in modal viewer, 1-by-1 project link approvals, and ID banning controls.
  - **Executive Dashboard**: System health metrics, OCR pass rates, and review statistics.
  - **Internships**: Corporate partner internship listings.
  - **AI Internship**: Dedicated AI/ML research opportunities and candidate matching.
  - Direct navigation button to the main website.

---

## 🛠️ Tech Stack

- **Backend**: Python 3, Flask, Werkzeug
- **Database**: SQLite3
- **Frontend**: HTML5, Vanilla CSS3 (Glassmorphic Design System), JavaScript (ES6)

---

## 💻 Local Setup & Running

1. **Clone the repository**:
   ```bash
   git clone https://github.com/underworld-demon1/S30-Verification-Platform.git
   cd S30-Verification-Platform
   ```

2. **Install dependencies**:
   ```bash
   pip install flask werkzeug
   ```

3. **Run the application**:
   ```bash
   python app.py
   ```

4. **Access the application**:
   - Main Website: `http://127.0.0.1:5000/`
   - Student Login: `http://127.0.0.1:5000/login`
   - Admin Portal: `http://127.0.0.1:5000/admin` *(Username: `TeamX` | Password: `TeamX@Admin`)*

---

## 🔒 Security & Admin Access

- The Admin Portal is separated from public routes and guarded by session-based authentication.
- Credentials:
  - **Admin Username**: `TeamX`
  - **Admin Password**: `TeamX@Admin`

---

## 📄 License
MIT License
