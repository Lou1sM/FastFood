from random import shuffle


def randomly(seq):
    shuffled = seq
    shuffle(shuffled)
    return shuffled

def transitive_closure(set_):
    closure = set(set_)
    while True:
        new_elements = set((a,b) for (a,x) in closure for (z,b) in set_ if x == z)
        new_closure = closure | new_elements
        if new_closure == closure:
            break
        closure = new_closure
    return closure


def direct_requires(proc_1,proc_2):
    return not set(proc_1['in']).intersection(set(proc_2['out'])) == set([])

def direct_dependent(proc_1,proc_2):
    return direct_requires(proc_1,proc_2) or direct_requires(proc_2,proc_1)

def hours_minutes_seconds(time_secs):
    #Convert time give in seconds to hhmmss format."""
    secondcount = time_secs % 60
    minutecount = (time_secs % 3600 - secondcount)/60
    hourcount = (time_secs - secondcount - (minutecount *60))/3600

    if time_secs == 0:
        return 0

    if hourcount == 0:
        hours = ''
    elif hourcount == 1:
        hours = str(int(hourcount)) + 'hr'
    else:
        hours = str(int(hourcount)) + 'hrs'
    if minutecount == 1:
        minutes = str(int(minutecount)) + 'min'
    else:
        minutes = str(int(minutecount)) + 'mins'
    if secondcount == 0:
        seconds = ''
    elif secondcount == 1:
        seconds = str(int(secondcount)) + 'sec'
    else:
        seconds = str(int(secondcount)) + 'secs'
    return hours + minutes + seconds
