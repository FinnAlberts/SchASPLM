import utils

testcases = [
    (['s(1..3).'], ['s(1..3).']),
    (['a :- b..c.'], ['a :- b..c.']),
    (['% a comment line'], ['% a comment line']),
    (['p(1,2).', 'q :- r.'], ['p(1,2).', 'q :- r.']),
    (['x..y. z.'], ['x..y.', 'z.']),
    (['x.\ny.'], ['x.', 'y.']),
    (['x.\n\ny.'], ['x.', '', 'y.']),
    (['% Instance Template\nevent(_).\n\nroom(Room, Capacity).\n'], ['% Instance Template', 'event(_).', '', 'room(Room, Capacity).']),
]

correct = total = 0

for input, expected_output in testcases:
    out = utils.split_ASP_code_into_statement_blocks(input)
    print('IN :', input)
    print('OUT:')
    for o in out:
        print('  ', o)
    print('EXPECTED:')
    for e in expected_output:
        print('  ', e)
    print('OK:', out == expected_output)
    correct += out == expected_output
    total += 1
    print('---')

print()
print(f'Test splitter: {correct}/{total} correct.')
print()

