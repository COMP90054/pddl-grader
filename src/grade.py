
import glob, os, sys, tabulate, csv

USAGE = """
    Usage: python3 grade.py [<student_id>|all]
"""




# Change to reflect the list of problems for testing
PROBLEMS = ['problem1-1', 'problem1-2','problem1-3','problem1-4','problem1-5','problem1-6','problem2-1','problem2-2', 'problem3-1', 'problem3-2', 'problem3-3', 'problem3-4', 'problem3-5', 'problem3-6']
REFERENCE_LOC = '../comp90054/reference'
SUBMISSIONS_LOC = '../../git-hw-submissions/2022_s2_a2'
SUBMISSION_PDDL_FOLDER = 'pddl_template'
MARKING_LOC = '../comp90054/marking'


# Make sure all three directories exist
for LOC in [REFERENCE_LOC, SUBMISSIONS_LOC, MARKING_LOC]:
    if not os.path.isdir(LOC):
        print(f'Error: {LOC} does not exist')
        sys.exit(1)



mark = {
    False: '\u274c',
    True: '\u2714'
}

# character for a small red x
# c = '\u274c'

def check_alignment(student_id, prob):

    student_prob = prob.split('-')[0]+'.pddl'

    os.system(f'python3 merge.py {REFERENCE_LOC}/domain.pddl {REFERENCE_LOC}/{prob} {SUBMISSIONS_LOC}/{student_id}/{SUBMISSION_PDDL_FOLDER}/domain.pddl {SUBMISSIONS_LOC}/{student_id}/{SUBMISSION_PDDL_FOLDER}/{student_prob} {MARKING_LOC}/{student_id}/domain.pddl {MARKING_LOC}/{student_id}/{prob} > {MARKING_LOC}/{student_id}/merge.log 2>&1')
    os.system(f'./plan.sh {MARKING_LOC}/{student_id}/plan.{prob}.merged {MARKING_LOC}/{student_id}/domain.pddl {MARKING_LOC}/{student_id}/{prob} > {MARKING_LOC}/{student_id}/planner.{prob}.merged.log 2>&1')
    # check file for failure message
    with open(f'{MARKING_LOC}/{student_id}/planner.{prob}.merged.log', 'r') as f:
        mtext = f.read()
        align = 'Search stopped without finding a solution.' in mtext
    if not (align or os.path.isfile(f'{MARKING_LOC}/{student_id}/plan.{prob}.merged')):
        print(f'Warning: Alignment failed for {student_id}/{prob}')

    plan = None
    if os.path.isfile(f'{MARKING_LOC}/{student_id}/plan.{prob}.merged'):
        with open(f'{MARKING_LOC}/{student_id}/plan.{prob}.merged', 'r') as f:
            plan = f.read()
    return (align, plan)

def check_solve(student_id, prob):
    student_prob = prob.split('-')[0]+'.pddl'

    os.system(f'./plan.sh {MARKING_LOC}/{student_id}/plan.{prob} {SUBMISSIONS_LOC}/{student_id}/{SUBMISSION_PDDL_FOLDER}/domain.pddl {SUBMISSIONS_LOC}/{student_id}/{SUBMISSION_PDDL_FOLDER}/{student_prob} > {MARKING_LOC}/{student_id}/planner.{prob}.log 2>&1')
    return os.path.isfile(f'{MARKING_LOC}/{student_id}/plan.{prob}')

def check_validate(student_id, prob):
    os.system(f'./validate.sh {REFERENCE_LOC}/domain.pddl {REFERENCE_LOC}/{prob} {MARKING_LOC}/{student_id}/plan.{prob} > {MARKING_LOC}/{student_id}/validate1.{prob}.log 2>&1')
    with open(f'{MARKING_LOC}/{student_id}/validate1.{prob}.log', 'r') as f:
        vtext = f.read()
        valid1 = ('Plan executed successfully' in vtext) and ('Plan valid' in vtext)
    
    student_prob = prob.split('-')[0]+'.pddl'
    os.system(f'./validate.sh {SUBMISSIONS_LOC}/{student_id}/{SUBMISSION_PDDL_FOLDER}/domain.pddl {SUBMISSIONS_LOC}/{student_id}/{SUBMISSION_PDDL_FOLDER}/{student_prob} {REFERENCE_LOC}/plan.{prob} > {MARKING_LOC}/{student_id}/validate2.{prob}.log 2>&1')
    with open(f'{MARKING_LOC}/{student_id}/validate2.{prob}.log', 'r') as f:
        vtext = f.read()
        valid2 = ('Plan executed successfully' in vtext) and ('Plan valid' in vtext)
    return (valid1, valid2)

def format_results(results):
    headers = ['Problem', 'Solve', 'St-Validates', 'Ref-Validates', 'Aligns']
    rows = []
    for prob in results:
        rows.append([prob, results[prob]['solve'], results[prob]['validates1'], results[prob]['validates2'], results[prob]['aligns']])
    return tabulate.tabulate(rows, headers=headers, tablefmt='pipe')

def count_trues(values):
    return len([ v for v in values if mark[True] in v])

def explain_fails(values):
    explanation = ''
    
    for i,v in enumerate(values):
        if mark[False] in v:
            if i == 0:
                explanation += 'Failed to Solve. '
            elif i == 1:
                explanation += 'Failed to validate student solution. '
            elif i == 2:
                explanation += 'Failed to validate reference solution. '
    
    return explanation if len(explanation) > 0 else '-'

def gradesummary():
    sdirs = glob.glob(f'{MARKING_LOC}/*')
    summary = []
    summary_fields = ['student_id', 'problem1', 'problem2','problem3','problem4','problem1-explanation', 'problem2-explanation','problem3-explanation','problem4-explanation']
    for sdir in sdirs:
        student_id = sdir.split('/')[-1]
        result = {}
        with open(f'{sdir}/grade.txt','r') as file:
            lines = file.readlines()
            for line in lines:
                linesplit = line.strip().split('|')
                if len(linesplit) == 1: continue
                key = linesplit[1].split('-')[0].strip()
                values = linesplit[2:]
                if key not in result.keys(): 
                    result[key] = values
                    result[f'{key}-explanation'] = explain_fails(values)
                elif  count_trues(values) > count_trues(result[key]):
                    result[key] = values
                    result[f'{key}-explanation'] = explain_fails(values)
            summary.append( {'student_id': student_id, 'problem1': count_trues(result['problem1'])/3.0, 'problem2': count_trues(result['problem2'])/3.0, 'problem3': count_trues(result['problem3'])/3.0, 'problem4': count_trues(result['problem4']), 'problem1-explanation': result['problem1-explanation'], 'problem2-explanation': result['problem2-explanation'],'problem3-explanation': result['problem3-explanation'],'problem4-explanation': result['problem4-explanation']   })

    with open('summary.csv', 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames = summary_fields)
        writer.writeheader()
        writer.writerows(summary)

def gradeall():
    sdirs = glob.glob(f'{SUBMISSIONS_LOC}/*')
    for sdir in sdirs:
        student_id = sdir.split('/')[-1]
        grade(student_id)

def grade(student_id):

    print(f"Grading {student_id}...")

    # delete the old marking folder if user wants to re-grade
    if os.path.exists(f'{MARKING_LOC}/{student_id}'):
        remove = input(f'{student_id} already exists. Do you want to remove it? (y/n) ')
        if remove == 'y':
            os.system(f'rm -rf {MARKING_LOC}/{student_id}')
        else:
            print('Abort.')
            return
    os.mkdir(f'{MARKING_LOC}/{student_id}')

    #copy student submission into marking location
    os.mkdir(f'{MARKING_LOC}/{student_id}/{SUBMISSION_PDDL_FOLDER}')
    os.system(f'cp {SUBMISSIONS_LOC}/{student_id}/{SUBMISSION_PDDL_FOLDER}/*.pddl {MARKING_LOC}/{student_id}/{SUBMISSION_PDDL_FOLDER}/.')

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

    #Check if they solve problem4 and visits all locations
    results.update( problem4 = {'solve': mark[check_solve(student_id, f'problem4')], 'validates1':'-', 'validates2':'-', 'aligns':'-' })
    
    num_cells = 0
    if os.path.isfile(f'{SUBMISSIONS_LOC}/{student_id}/{SUBMISSION_PDDL_FOLDER}/problem4.pddl'):
        with open(f'{SUBMISSIONS_LOC}/{student_id}/{SUBMISSION_PDDL_FOLDER}/problem4.pddl', 'r') as file:
            data = file.readlines()
            for line in data:
                if 'cells' in line:
                    num_cells = len([ l for l in line.split(' - ')[0].split(' ') if l != ''])
                    break
        
    num_moves = 0
    if os.path.isfile(f'{MARKING_LOC}/{student_id}/plan.problem4'):
        with open(f'{MARKING_LOC}/{student_id}/plan.problem4', 'r') as file:
            data = file.readlines()
            num_moves = 0
            for line in data:
                if 'move' in line: num_moves+=1

    if num_cells == num_moves + 1: 
        results['problem4']['solve']=mark[True]
    else:
        plan_text+= f'\n\nNumber of moves for problem4 is {num_moves} for {num_cells} cells\n\n'
        results['problem4']['solve']=mark[False]
    # format results
    res = format_results(results)

    with open(f'{MARKING_LOC}/{student_id}/grade.txt', 'w', encoding='utf-8') as f:
        f.write(f'\n{res}\n\n{plan_text}\n\n')

    print('Done!\n')

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2:
        print(USAGE)
    elif sys.argv[1] == 'all':
        gradeall()
    elif sys.argv[1] == 'summary':
        gradesummary()
    else:
        grade(sys.argv[1])
