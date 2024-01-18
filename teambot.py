import os
import yaml

scoresraw = open(f"{os.getcwd()}/scores.txt", "r")

alternativeteam_scoretreshhold = 15
config = yaml.load(open(f"{os.getcwd()}/config.yaml", "r"), Loader=yaml.FullLoader)

def print_team(team):
    teamtotalscore = get_team_score(team)

    output = ''
    for p in range(len(team)):
        output += f'{team[p][0]}'
        if p < len(team) - 1:
            output += ', '
    output += f'  (Score: {teamtotalscore})'
    return output

def print_not_participating(parts):
    np = f''

    for p in range(len(parts)):
        if p > 11:
            np += f'{parts[p][0]}, '
    
    return np

def get_team_score(team):
    score = 0
    for t in range(len(team)):
        score += team[t][1]
    return score

def swap(parts, p1, p2):
    parts[p1], parts[p2] = parts[p2], parts[p1]

def generate_teams(parts):
    teams = []
    
    teamsize = config['team_size']
    teamcount = int(len(parts) / teamsize)

    for t in range(teamcount):
        team = []
        for p in range(teamsize):
            team.append(parts[p + t * teamsize])
        teams.append(team)

    return teams

def get_score_diff(teams):
    scores = []
    for t in range(len(teams)):
        scores.append(get_team_score(teams[t]))
    
    return max(scores) - min(scores)

def check_for_duplicates(team, allparts, bestparts):
    allparts.append(bestparts)

    for a in allparts:
        diffinpart = 0
        for p in range(len(a)):
            if a[p][0] != team[p][0]:
                diffinpart += 1
        if diffinpart == 0:
            return True


    return False

s = scoresraw.readlines()

participants = []

for x in s:
    x = x.replace('\n','')
    x = x.split(',')
    name = x[0]
    score = int(x[1])
    
    participants.append([name,score])

participants_sorted = sorted(participants, key=lambda p : p[1],reverse=True)
participants = participants_sorted

teams = generate_teams(participants)
scorediff = get_score_diff(teams)

alternatives = 0
alternativeparts = []

while True:

    tempparts = participants.copy()

    thisbestscore = scorediff
    thisbestparts = tempparts

    improvements = 0

    for p in range(len(tempparts)):
        for s in range(len(tempparts)):
            swap(tempparts,p,s)

            tempteams = generate_teams(tempparts)
            thisscorediff = get_score_diff(tempteams)

            if (thisscorediff < thisbestscore):
                thisbestscore = thisscorediff
                thisbestparts = tempparts
                alternatives = 0
                alternativeparts.clear()
                improvements += 1
            elif (thisscorediff <= thisbestscore + alternativeteam_scoretreshhold and not check_for_duplicates(tempparts, alternativeparts, thisbestparts)):
                alternatives += 1
                alternativeparts.append(tempparts)

            tempparts = participants.copy()

    sd = get_score_diff(generate_teams(thisbestparts))

    if (sd < scorediff):
        scorediff = sd
        participants = thisbestparts.copy()
    else:
        break


    print(f'Teams generated. {improvements} optimization(s) found. Diff: ({scorediff})')

bestteams = generate_teams(participants)

for f in bestteams:
    f.sort()


output = f'\nBEST TEAMS:\n'
for t in range(len(bestteams)):
    output += f'Team {t + 1}: {print_team(bestteams[t])}\n'
print(output)
print(f'')

al = 0
if (alternatives > 0 and config['generate_alternatives']):
    for a in alternativeparts:
        altbestteams = generate_teams(a)
        altscorediff = get_score_diff(altbestteams)
        
        for t in altbestteams:
            t.sort()

        duplicates = 0
        for t2 in range(len(altbestteams)):
            for p in range(len(altbestteams[t2])):
                if (altbestteams[t2][p] == bestteams[t2][p]):
                    duplicates += 1

        if (duplicates == 12):
            continue
        
        al += 1

        output = f'\nALTERNATIVE {al}\n'
        for t in range(len(altbestteams)):
            output += f'Team {t + 1}: {print_team(altbestteams[t])}\n'
        print(output)