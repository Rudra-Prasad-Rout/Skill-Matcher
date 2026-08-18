import requests
import database

# Priya Sharma (ID: 9B3KZ, user_id=3) is currently an accepted member in CyberVikings (lead by Jay, team_id=1)
s_priya = requests.Session()
r = s_priya.post('http://127.0.0.1:5000/login', data={'email': 'priya.s@iitd.ac.in', 'password': 'password123'})
print('Priya login:', r.status_code)

# 1. Test Priya viewing squad and fellow teammates at /team/manage
r_squad = s_priya.get('http://127.0.0.1:5000/team/manage')
print('\n--- Priya Teammates View Test ---')
print('HTTP Status:', r_squad.status_code)
print('Shows CyberVikings:', 'CyberVikings' in r_squad.text)
print('Shows Confirmed Teammates:', 'Active Team Roster' in r_squad.text or 'CONFIRMED TEAMMATES' in r_squad.text)
print('Shows Leader Jay:', 'Jay' in r_squad.text)
print('Shows Priya Sharma (YOU):', 'Priya Sharma' in r_squad.text)
print('Shows LEAVE SQUAD button:', 'LEAVE' in r_squad.text)

# 2. Test Priya leaving the squad via /api/team/leave
r_leave = s_priya.post('http://127.0.0.1:5000/api/team/leave', json={'team_id': 1})
print('\n--- Priya Leave Squad API Test ---')
print('Leave API Response:', r_leave.json())

# 3. Verify Priya's candidate dashboard after leaving: should no longer show CyberVikings
r_priya_dash = s_priya.get('http://127.0.0.1:5000/candidate/home')
print('\n--- Priya Dashboard After Leaving ---')
print('Shows Not In a Squad Yet:', 'Not In a Squad Yet' in r_priya_dash.text)
print('Shows FIND A SQUAD CTA:', 'FIND A SQUAD' in r_priya_dash.text)
print('CyberVikings gone from squad status:', 'CyberVikings' not in r_priya_dash.text)

# 4. Check Jay's team manage: Priya should no longer be in the roster
s_jay = requests.Session()
s_jay.post('http://127.0.0.1:5000/login', data={'email': 'njay0885@gmail.com', 'password': 'password123'})
r_jay_manage = s_jay.get('http://127.0.0.1:5000/team/manage?team_id=1')
print('\n--- Jay Team Manage After Priya Left ---')
print('Priya Sharma removed from confirmed members:', 'Priya Sharma' not in r_jay_manage.text)
print('Slots remaining increased:', 'OPEN SQUAD SLOT' in r_jay_manage.text)
