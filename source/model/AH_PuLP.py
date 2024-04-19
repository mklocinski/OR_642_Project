import pandas as pd
import numpy as np
import pulp
from source.utilities import app_functions



def run_AH_PuLP(abstract_data, schedule_data, preference_data):
    maxTalksPerRoom = 21
    TalksPerSlot = 3
    talk_dat = abstract_data
    time_dat = schedule_data
    pref_dat = preference_data
    WorkingGroups = list(talk_dat['PresentationTrackDesc'].unique())
    Talks = list(talk_dat['PresentationID'].unique())
    TimeSlots = list(time_dat['Slot ID'].unique())
    Preferences = {'L': 1,
                   'M': 10,
                   'H': 100}
    TalkPreference = {}
    for talk in Talks:
        TalkPreference[talk] = {}
        slot = talk_dat[(talk_dat['PresentationID'] == talk)]['PreferredTimeSlot'].item()
        pref_level = talk_dat[(talk_dat['PresentationID'] == talk)]['PreferenceLevel'].item()
        TalkPreference[talk][slot] = Preferences[pref_level]
        for ts in TimeSlots:
            if ts == slot:
                pass
            else:
                if pref_level == 'L':

                    TalkPreference[talk][ts] = Preferences['L']

                elif pref_level == 'M':

                    TalkPreference[talk][ts] = Preferences['L']

                elif pref_level == 'H':

                    TalkPreference[talk][ts] = -100

    ## get # of talks per working group and
    WGRooms = {}
    TalkWGs = {}
    for wg in WorkingGroups:
        WGRooms[wg] = int(TalksPerSlot * np.ceil(
            len(talk_dat[talk_dat['PresentationTrackDesc'] == wg]['PresentationID'].unique()) / maxTalksPerRoom))
        TalkWGs[wg] = list(talk_dat[talk_dat['PresentationTrackDesc'] == wg]['PresentationID'].unique())

    ## for each talk get all other talks with the same author
    TalkConflict = {}
    for talk in Talks:
        talk_author = talk_dat[talk_dat['PresentationID'] == talk]['AuthorID'].item()

        TalkConflict[talk] = list(talk_dat[talk_dat['AuthorID'] == talk_author]['PresentationID'].unique())

    for ts in range(2, max(TimeSlots)):
        test_range = range(ts - 1, ts + 2)
        print([i for i in test_range])
    TimeSlots

    ## define model
    model = pulp.LpProblem('MORS_Scheduling', pulp.LpMaximize)

    ## create boolean decision variables
    TALK_ASSIGN = {}
    # TALK_SLACK = {}
    for talk in Talks:
        # TALK_SLACK[talk] = pulp.LpVariable(f'Slack_talk{talk}', lowBound=-1, cat='Integer')
        for timeslot in TimeSlots:
            TALK_ASSIGN[talk, timeslot] = pulp.LpVariable(f'{talk} {timeslot}', cat='Binary')
    '''WG_SLACK = {}
    for wg in WorkingGroups:
        WG_SLACK[wg] = pulp.LpVariable(f'WG_SLACK{wg}', cat='Integer')
    '''
    ## no conflicting talks can be scheduled in the same time block
    for talk in Talks:
        for timeslot in range(2, max(TimeSlots) - 1):
            no_conflict_range = range(timeslot - 1, timeslot + 2)
            model += pulp.lpSum(TALK_ASSIGN[t, ts] for t in TalkConflict[talk] for ts in no_conflict_range) <= 1

    ## each talk gets assigned exactly once
    for talk in Talks:
        model += pulp.lpSum(TALK_ASSIGN[talk, timeslot] for timeslot in TimeSlots) == 1

    ## cannot assign more than WGRooms[wg]*3 talks in same time slot
    for wg in WorkingGroups:
        for timeslot in TimeSlots:
            model += pulp.lpSum(TALK_ASSIGN[talk, timeslot] for talk in TalkWGs[wg]) <= WGRooms[wg]

    ## add objective function
    model += pulp.lpSum(
        pulp.lpSum(TalkPreference[talk][timeslot] * TALK_ASSIGN[talk, timeslot] for timeslot in TimeSlots) for talk in
        Talks)

    ## solve problem and print status/objective
    status = model.solve()
    print(f"status: {model.status}, {pulp.LpStatus[model.status]}")
    print(f"objective: {model.objective.value()}")

    # --------------------------------------------------------------------------- #
    # ------------------------ Create and save dataset -------------------------- #
    # --------------------------------------------------------------------------- #

    output = pd.DataFrame({'Presentation': [t[0] for t in TALK_ASSIGN],
                           'Working Group': [
                               talk_dat['PresentationTrackDesc'].loc[talk_dat['PresentationID'] == t[0]].item() for t in
                               TALK_ASSIGN],
                           'Date': [time_dat.loc[t[1] - 1]['Day'] for t in TALK_ASSIGN],
                           'Start Time': [time_dat.loc[t[1] - 1]['Slot Begin Time'] for t in TALK_ASSIGN],
                           'Duration': [0 for t in TALK_ASSIGN],
                           'Authors': [talk_dat['AuthorID'].loc[talk_dat['PresentationID'] == t[0]].item() for t in
                                       TALK_ASSIGN],
                           'var': [TALK_ASSIGN[t[0], t[1]].varValue for t in TALK_ASSIGN]})
    output['End Time'] = [0 for s, d in zip(output['Start Time'], output['Duration'])]
    output = output[output['var'] == 1]

    model_status = app_functions.model_result(status)
    return model_status, output