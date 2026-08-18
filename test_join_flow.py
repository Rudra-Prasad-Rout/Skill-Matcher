import requests
import database

# Priya Sharma (ID: 9B3KZ, user_id=3) logs in
s_priya = requests.Session()
r = s_priya.post('http://127.0.0.1:5000/login', data={'email': 'priya.s@iitd.ac.in', 'password': 'password123'})
print('Priya login status:', r.status_code)

# 1. Priya requests to join Jay's squad SQD-KO9N (CyberVikings, team_id=1, leader_id=8)
r_join = s_priya.post('http://127.0.0.1:5000/api/team/request-join', json={'team_code': 'SQD-KO9N', 'message': 'Hey Jay, let me join CyberVikings!'})
print('Priya Join Request Response:', r_join.json())

# 2. Jay (leader) logs in
s_jay = requests.Session()
r = s_jay.post('http://127.0.0.1:5000/login', data={'email': 'njay0885@gmail.com', 'password': 'password123'})
print('Jay login status:', r.status_code)

# Get the request id
conn = database.get_db_connection()
req = conn.execute("SELECT id FROM team_invites WHERE sender_id = 3 AND team_id = 1 AND invite_type = 'JOIN_REQUEST' ORDER BY id DESC LIMIT 1").fetchone()
req_id = req['id']
conn.close()
print('Found join request ID:', req_id)

# 3. Jay accepts the join request
r_accept = s_jay.post('http://127.0.0.1:5000/api/mailbox/respond', json={'item_id': req_id, 'action': 'accept'})
print('Jay Accept Response:', r_accept.json())

# 4. Check Priya's candidate dashboard: must show "MY SQUAD STATUS: CyberVikings" and "SQUAD MEMBER"
r_priya_dash = s_priya.get('http://127.0.0.1:5000/candidate/home')
print('\n--- Priya Dashboard Verification ---')
print('HTTP Status:', r_priya_dash.status_code)
print('Shows CyberVikings:', 'CyberVikings' in r_priya_dash.text)
print('Shows SQUAD MEMBER:', 'SQUAD MEMBER' in r_priya_dash.text)
print('Shows Leader Jay:', 'Jay' in r_priya_dash.text)
print('Shows Squad Code SQD-KO9N:', 'SQD-KO9N' in r_priya_dash.text)

# 5. Check Jay's Squad Management: Priya Sharma must show in the Confirmed Squad Roster
r_jay_manage = s_jay.get('http://127.0.0.1:5000/team/manage?team_id=1')
print('\n--- Jay Team Manage Verification ---')
print('HTTP Status:', r_jay_manage.status_code)
print('Shows Priya Sharma in members:', 'Priya Sharma' in r_jay_manage.text)
print('Shows 9B3KZ badge:', '9B3KZ' in r_jay_manage.text)
print('Shows Confirmed Members count:', 'CONFIRMED SQUAD MEMBERS' in r_jay_manage.text)

# 6. Check Find Teams page for Priya: should show "YOU ARE CURRENTLY IN A SQUAD"
r_find = s_priya.get('http://127.0.0.1:5000/find-teams')
print('\n--- Priya Find Teams Page Verification ---')
print('HTTP Status:', r_find.status_code)
print('Shows Current Squad banner:', 'YOU ARE CURRENTLY IN A SQUAD' in r_find.text)
print('Shows CyberVikings:', 'CyberVikings' in r_find.text)
