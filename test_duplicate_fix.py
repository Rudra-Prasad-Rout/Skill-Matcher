import requests
import database

# Leader Arjun (team_id=6, SQD-K1Y7)
s_arjun = requests.Session()
s_arjun.post('http://127.0.0.1:5000/login', data={'email': 'arjun.sharma@iitb.ac.in', 'password': 'password123'})

# Candidate Marcus (user_id=4, M8V1Y)
s_marcus = requests.Session()
s_marcus.post('http://127.0.0.1:5000/login', data={'email': 'marcus.vance@nyu.edu', 'password': 'password123'})

# 1. Leader Arjun invites Marcus (M8V1Y) to squad 6
r_inv = s_arjun.post('http://127.0.0.1:5000/api/team/invite', json={'team_id': 6, 'target_id': 'M8V1Y'})
print('Arjun Invites Marcus:', r_inv.json())

# 2. Marcus also sends a join request to SQD-K1Y7
r_join = s_marcus.post('http://127.0.0.1:5000/api/team/request-join', json={'team_code': 'SQD-K1Y7', 'message': 'Hey Arjun!'})
print('Marcus Join Request:', r_join.json())

# 3. Check Marcus Mailbox and Accept Arjun's invite
conn = database.get_db_connection()
inv = conn.execute("SELECT id FROM team_invites WHERE receiver_id = 4 AND team_id = 6 AND invite_type = 'INVITATION' ORDER BY id DESC LIMIT 1").fetchone()
inv_id = inv['id'] if inv else None
conn.close()

if inv_id:
    r_acc = s_marcus.post('http://127.0.0.1:5000/api/mailbox/respond', json={'item_id': inv_id, 'action': 'accept'})
    print('Marcus Accepts Invite:', r_acc.json())

# 4. Check Arjun's squad 6 roster: Marcus must appear EXACTLY ONCE
r_roster = s_arjun.get('http://127.0.0.1:5000/team/manage?team_id=6')
print('\n--- Duplicate Prevention Verification ---')
print('HTTP Status:', r_roster.status_code)
print('Marcus Vance count in squad roster:', r_roster.text.count('Marcus Vance'))
print('Confirmed count shows 3 / 4:', '3 / 4 Confirmed' in r_roster.text or '3 / 4' in r_roster.text)
print('Alex Rivera count:', r_roster.text.count('Alex Rivera'))
