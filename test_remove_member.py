import requests
import database

# Leader Arjun (team_id=6, SQD-K1Y7)
s_arjun = requests.Session()
s_arjun.post('http://127.0.0.1:5000/login', data={'email': 'arjun.sharma@iitb.ac.in', 'password': 'password123'})

# Candidate Alex (user_id=1)
s_alex = requests.Session()
s_alex.post('http://127.0.0.1:5000/login', data={'email': 'alex.rivera@college.edu', 'password': 'password123'})

# Candidate Marcus (user_id=4)
s_marcus = requests.Session()
s_marcus.post('http://127.0.0.1:5000/login', data={'email': 'marcus.vance@nyu.edu', 'password': 'password123'})

print('--- Test 1: Leader Arjun views Squad 6 with members ---')
r = s_arjun.get('http://127.0.0.1:5000/team/manage?team_id=6')
print('HTTP Status:', r.status_code)
print('Has REMOVE FROM SQUAD button:', 'REMOVE FROM SQUAD' in r.text)

print('\n--- Test 2: Non-leader Marcus attempts to remove Alex (Should Fail 403) ---')
r_unauth = s_marcus.post('http://127.0.0.1:5000/api/team/remove-member', json={'team_id': 6, 'user_id': 1})
print('HTTP Status (Expect 403):', r_unauth.status_code)

print('\n--- Test 3: Leader Arjun removes themselves (Should Fail 400) ---')
r_self = s_arjun.post('http://127.0.0.1:5000/api/team/remove-member', json={'team_id': 6, 'user_id': 10})
print('HTTP Status (Expect 400):', r_self.status_code)

# First add Alex back so we can remove him cleanly in this test
conn = database.get_db_connection()
conn.execute("INSERT OR REPLACE INTO team_invites (team_id, sender_id, receiver_id, invite_type, status) VALUES (6, 1, 10, 'JOIN_REQUEST', 'ACCEPTED')")
conn.commit()
conn.close()

print('\n--- Test 4: Leader Arjun removes Alex from Squad 6 (Should Succeed) ---')
r_remove = s_arjun.post('http://127.0.0.1:5000/api/team/remove-member', json={'team_id': 6, 'user_id': 1})
print('HTTP Status:', r_remove.status_code)
print('Response message:', r_remove.json().get('message'))

print('\n--- Test 5: Verify Squad 6 roster after removing Alex ---')
r_roster = s_arjun.get('http://127.0.0.1:5000/team/manage?team_id=6')
print('Alex Rivera in squad roster (Should be False):', 'member-card-1' in r_roster.text)

print('\n--- Test 6: Verify Alex dashboard reflects removal ---')
r_alex_dash = s_alex.get('http://127.0.0.1:5000/candidate/home')
print('Alex Dashboard shows Not In a Squad Yet:', 'Not In a Squad Yet' in r_alex_dash.text)
print('Alex Dashboard shows FIND A SQUAD:', 'FIND A SQUAD' in r_alex_dash.text)
