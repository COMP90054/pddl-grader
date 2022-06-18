
import glob, os, sys, tabulate

USAGE = """
    Usage: python3 grade.py [<student_id>|all]
"""




# Change to reflect the list of problems for testing
PROBLEMS = ['p01', 'p02', 'p03']



mark = {
    False: '\u274c',
    True: '\u2714'
}

# character for a small red x
# c = '\u274c'

def check_alignment(student_id, prob):
    os.system(f'python3 merge.py reference/domain.pddl reference/{prob} submissions/{student_id}/domain.pddl submissions/{student_id}/{prob} marking/{student_id}/domain.pddl marking/{student_id}/{prob} > marking/{student_id}/merge.log 2>&1')
    os.system(f'./plan.sh marking/{student_id}/plan.{prob}.merged marking/{student_id}/domain.pddl marking/{student_id}/{prob} > marking/{student_id}/planner.{prob}.merged.log 2>&1')
    # check file for failure message
    with open(f'marking/{student_id}/planner.{prob}.merged.log', 'r') as f:
        mtext = f.read()
        align = 'Search stopped without finding a solution.' in mtext
    if not (align or os.path.isfile(f'marking/{student_id}/plan.{prob}.merged')):
        print(f'Warning: Alignment failed for {student_id}/{prob}')

    plan = None
    if os.path.isfile(f'marking/{student_id}/plan.{prob}.merged'):
        with open(f'marking/{student_id}/plan.{prob}.merged', 'r') as f:
            plan = f.read()
    return (align, plan)

def check_solve(student_id, prob):
    os.system(f'./plan.sh marking/{student_id}/plan.{prob} submissions/{student_id}/domain.pddl submissions/{student_id}/{prob} > marking/{student_id}/planner.{prob}.log 2>&1')
    return os.path.isfile(f'marking/{student_id}/plan.{prob}')

def check_validate(student_id, prob):
    os.system(f'./validate.sh reference/domain.pddl reference/{prob} marking/{student_id}/plan.{prob} > marking/{student_id}/validate1.{prob}.log 2>&1')
    with open(f'marking/{student_id}/validate1.{prob}.log', 'r') as f:
        vtext = f.read()
        valid1 = ('Plan executed successfully' in vtext) and ('Plan valid' in vtext)
    os.system(f'./validate.sh submissions/{student_id}/domain.pddl submissions/{student_id}/{prob} reference/plan.{prob} > marking/{student_id}/validate2.{prob}.log 2>&1')
    with open(f'marking/{student_id}/validate2.{prob}.log', 'r') as f:
        vtext = f.read()
        valid2 = ('Plan executed successfully' in vtext) and ('Plan valid' in vtext)
    return (valid1, valid2)

def format_results(results):
    headers = ['Problem', 'Solve', 'St-Validates', 'Ref-Validates', 'Aligns']
    rows = []
    for prob in results:
        rows.append([prob, results[prob]['solve'], results[prob]['validates1'], results[prob]['validates2'], results[prob]['aligns']])
    return tabulate.tabulate(rows, headers=headers, tablefmt='pipe')


def gradeall():
    sdirs = glob.glob('submissions/*')
    for sdir in sdirs:
        student_id = sdir.split('/')[1]
        grade(student_id)

def grade(student_id):

    print(f"Grading {student_id}...")

    # delete the old marking folder if user wants to re-grade
    if os.path.exists(f'marking/{student_id}'):
        remove = input(f'{student_id} already exists. Do you want to remove it? (y/n) ')
        if remove == 'y':
            os.system(f'rm -rf marking/{student_id}')
        else:
            print('Abort.')
            return
    os.mkdir(f'marking/{student_id}')

    results = {p: {} for p in PROBLEMS}


    # confirm they find plans for all
    print('  finding plans...')
    for prob in results:
        results[prob]['solve'] = mark[check_solve(student_id, f'{prob}.pddl')]


    # confirm their plans work on our domain
    print('  validating plans...')
    for prob in results:
        if results[prob]['solve'] == mark[True]:
            validates1, validates2 = check_validate(student_id, f'{prob}.pddl')
            results[prob]['validates1'] = mark[validates1]
            results[prob]['validates2'] = mark[validates2]
        else:
            _, validates2 = check_validate(student_id, f'{prob}.pddl')
            results[prob]['validates1'] = '-'
            results[prob]['validates2'] = mark[validates2]


    # check the theory alignments
    print('  checking theory alignments...')
    plan_text = ''
    for prob in results:
        align, plan = check_alignment(student_id, f'{prob}.pddl')
        if plan:
            plan_text += f"\nMis-alignment plan for {prob}:\n{plan}"
        results[prob]['aligns'] = mark[align]


    # format results
    res = format_results(results)

    with open(f'marking/{student_id}/grade.txt', 'w', encoding='utf-8') as f:
        f.write(f'\n{res}\n\n{plan_text}\n\n')

    print('Done!\n')

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2:
        print(USAGE)
    elif sys.argv[1] == 'all':
        gradeall()
    else:
        grade(sys.argv[1])
