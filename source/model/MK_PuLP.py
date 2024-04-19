import os
import pulp as pl
import pandas as pd
from datetime import datetime, timedelta
from itertools import product
from source.utilities import app_functions


def sessions(sess_start_stop_times, interval):
    all_sessions = []
    for sess in sess_start_stop_times:
        x = [d.to_pydatetime().strftime('%m/%d/%Y %I:%M %p') for d in
             pd.date_range(sess[0], sess[1], freq=interval)]
        all_sessions.extend(x[:-1])
    return all_sessions

def model_one_data_prep(stored_data):
    data = stored_data
    data = data.dropna()
    data = data.drop_duplicates()
    data = data.set_index('Working Group')
    data = data.filter(like='WG', axis=0).reset_index()
    data['WG Label'] = [w.split()[0] for w in data['Working Group']]
    data['Start Time'] = [datetime.strptime(i, '%I:%M %p') if not pd.isna(i) else pd.NaT for i in data['Start Time']]
    data['End Time'] = [datetime.strptime(i, '%I:%M %p') if not pd.isna(i) else pd.NaT for i in data['End Time']]
    data['Duration'] = [e - s for e, s in zip(data['End Time'], data['Start Time'])]
    data['Date'] = [datetime.strptime(i, '%m/%d/%Y') if not pd.isna(i) else pd.NaT for i in data['Date']]
    data['Start Time'] = [datetime.combine(d, s.time()) if not pd.isna(d) and not pd.isna(s) else pd.NaT for d, s in
                          zip(data['Date'], data['Start Time'])]
    data['End Time'] = [datetime.combine(d, e.time()) if not pd.isna(d) and not pd.isna(e) else pd.NaT for d, e in
                        zip(data['Date'], data['End Time'])]

    data = data.set_index(['WG Label', 'Talk'])
    return data

def model_result(model_status):
    pulp_outputs = {1:"Optimal solution found", 0:"Not solved",
                    -1:"Infeasible", -2:"Unbounded", -3:"Undefined"}
    return(pulp_outputs[model_status])

def run_MK_PuLP(stored_data):
    session_start_stops = [[datetime.strptime('6/14/2022 1:30 PM', '%m/%d/%Y %I:%M %p'),
                            datetime.strptime('6/14/2022 3:00 PM', '%m/%d/%Y %I:%M %p')],
                           [datetime.strptime('6/15/2022 8:30 AM', '%m/%d/%Y %I:%M %p'),
                            datetime.strptime('6/15/2022 10:00 AM', '%m/%d/%Y %I:%M %p')],
                           [datetime.strptime('6/15/2022 10:30 AM', '%m/%d/%Y %I:%M %p'),
                            datetime.strptime('6/15/2022 12:00 PM', '%m/%d/%Y %I:%M %p')],
                           [datetime.strptime('6/15/2022 1:30 PM', '%m/%d/%Y %I:%M %p'),
                            datetime.strptime('6/15/2022 3:00 PM', '%m/%d/%Y %I:%M %p')],
                           [datetime.strptime('6/16/2022 8:30 AM', '%m/%d/%Y %I:%M %p'),
                            datetime.strptime('6/16/2022 10:00 AM', '%m/%d/%Y %I:%M %p')],
                           [datetime.strptime('6/16/2022 10:30 AM', '%m/%d/%Y %I:%M %p'),
                            datetime.strptime('6/16/2022 12:00 PM', '%m/%d/%Y %I:%M %p')],
                           [datetime.strptime('6/16/2022 1:30 PM', '%m/%d/%Y %I:%M %p'),
                            datetime.strptime('6/16/2022 3:00 PM', '%m/%d/%Y %I:%M %p')]]

    data = model_one_data_prep(stored_data)

    # --------------------------------------------------------------------------- #
    # Create indices
    # - unique working group-presentation pairs
    wg_p = [i for i in set([(g, p) for a, g, p in data.index])]
    # - unique working groups
    wg = [i for i in set([g for a, g, p in data.index])]
    # - unique papers
    pr = [i for i in set([p for a, g, p in data.index])]
    # - unique time slots across sessions
    tm = sessions(session_start_stops, '30min')
    # - unique authors: some papers have groups of up to 4 people. These lines
    #  pull all of them out into a list so they can each be evaluated against the
    #  schedule
    t = data.reset_index()[['Authors', 'WG Label', 'Talk']]
    t['Authors'] = [a.replace(',', '') for a in t['Authors']]
    t['Authors'] = [a.replace(';', ',') for a in t['Authors']]
    t['Authors'] = [a.split(',') for a in t['Authors']]
    v = t.explode('Authors')
    au = [a for a in set(v['Authors'])]
    # - unique author-presentation-wg
    v = v.set_index(['Authors', 'WG Label', 'Talk'])
    a_gp = [(a, g, p) for a, g, p in v.index]
    # - unique author-presentation-wg-time
    agp_t = [(a_gp[0], a_gp[1], a_gp[2], t) for a_gp, t in set(list(product(*[a_gp, tm])))]
    # - unique author-time
    auth_time = [(a, t) for a, t in set(list(product(*[au, tm])))]

    # --------------------------------------------------------------------------- #
    # Create data
    # - list indicating length of presentation
    data = data.reset_index()
    length_p = [0 if (d[0].seconds % 3600) // 60 == 30 else 1 for d in
                [[i for i in data[data['Talk'] == p]['Duration']] for p in pr]]
    # - session slot index, for handling one-hour presentations
    s_t = [1, 2, 3] * len(session_start_stops)

    # --------------------------------------------------------------------------- #
    # Create variables
    # - Primary decision variable. Is a presentation scheduled for a working group
    #   at a certain time. Filtered to only real working group-presentation pairings
    x_pgt = [(p, g, t) for p, g, t in list(product(*[pr, wg, tm])) if (g, p) in wg_p]

    assign = pl.LpVariable.dicts("assign",
                                 x_pgt,
                                 cat='Binary')

    # - Indicator variable. Is an author -- an individual, not a group -- scheduled
    #  for presentation p in working group g at time t.
    auth_apt = pl.LpVariable.dicts("auth_ind", agp_t, cat='Binary')

    # --------------------------------------------------------------------------- #
    # Cost

    # --------------------------------------------------------------------------- #
    # Create model
    model = pl.LpProblem("Project", pl.LpMinimize)
    model += pl.lpSum([assign[p, g, t] for p, g, t in x_pgt])

    # --------------------------------------------------------------------------- #
    # Constraints
    # - Each presentation-working group pair must be scheduled for exactly one time
    for wp in wg_p:
        model += pl.lpSum([assign[p, g, t] for p, g, t in x_pgt if p == wp[1] and g == wp[0]]) == 1

    # - Each author cannot be booked for more than one presentation at a time
    # >> this constraint turns on the author indicator variable - if a presentation-working group pair
    #   is scheduled for t, the indicator auth_apt must be 1 for that combination
    for agpt in agp_t:
        model += pl.lpSum([assign[p, g, t] for p, g, t in x_pgt if p == agpt[2] and g == agpt[1] and t == agpt[3]]) <= \
                 auth_apt[agpt[0], agpt[1], agpt[2], agpt[3]]

    # >> indicator auth_apt cannot have a value of more than 1 for a given author-time combination
    for a_t in auth_time:
        model += pl.lpSum([auth_apt[a, g, p, t] for a, g, p, t in agp_t if a == a_t[0] and t == a_t[1]]) <= 1

    # - Each working group cannot have more than one presentation at a time
    for ws in wg:
        for ts in tm:
            # print(sum([assign[p,g,t].varValue for p,g,t in x_pgt if g == ws]))
            model += pl.lpSum([assign[p, g, t] for p, g, t in x_pgt if g == ws and t == ts]) <= 1

    # - All presentations of length 60 minutes must have a session index of two or less.
    #  If there is an assignment for a (p-g-t) tuple, check if the presentation is
    #  a one-hour presentation (length_p), then check the session index (s_t) for
    #  which time slot the assignment was made. The product of the three values will
    #  reflect the time slot for the assignment, which cannot be more than two.
    for ps in pr:
        model += pl.lpSum(
            [s_t[tm.index(t)] * length_p[pr.index(p)] * assign[p, g, t] for p, g, t in x_pgt if p == ps]) <= 2

    model.solve()
    # --------------------------------------------------------------------------- #
    # ------------------------ Create and save dataset -------------------------- #
    # --------------------------------------------------------------------------- #
    output = pd.DataFrame({'Presentation': [p for p, g, t in x_pgt],
                           'Working Group': [g for p, g, t in x_pgt],
                           'Date': [datetime.strptime(t, '%m/%d/%Y %I:%M %p').strftime('%m/%d/%Y') for p, g, t in
                                    x_pgt],
                           'Start Time': [datetime.strptime(t, '%m/%d/%Y %I:%M %p') for p, g, t in x_pgt],
                           'Duration': [length_p[pr.index(p)] for p, g, t in x_pgt],
                           'Authors': [data[data['Talk'] == p]['Authors'].values[0] for p, g, t in x_pgt],
                           'var': [assign[p,g,t].varValue for p,g,t in x_pgt]})
    output['End Time'] = [s + timedelta(minutes=60) if d == 1 else s + timedelta(minutes=30) for s, d in
                          zip(output['Start Time'], output['Duration'])]
    output['End Time'] = [s.time().strftime('%I:%M %p') for s in output['End Time']]
    output['Start Time'] = [s.time().strftime('%I:%M %p') for s in output['Start Time']]
    output = output[output['var'] == 1]

    model_status = app_functions.model_result(model.status)

    return model_status, output
