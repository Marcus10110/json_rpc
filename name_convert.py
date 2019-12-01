name_test_set = [
    ['mId', 'id'],
    ['mWidthPx', 'widthPx'],
    ['mLeftEdgeTime', 'leftEdgeTime'],
    ['mSecondsPerPx', 'secondsPerPx'],
    ['mX', 'x'],
    ['mY', 'y'],
    ['mFrom', 'from'],
    ['mTo', 'to'],
    ['mId', 'id'],
    ['mValues', 'values'],
    ['mFirstSampleTime', 'firstSampleTime'],
    ['mSampleRate', 'sampleRate'],
    ['mValueSet', 'valueSet'],
    ['mLines', 'lines'],
    ['mLineStrip', 'lineStrip'],
]

type_test_set = [
    ['int', 'number'],
    ['double', 'number'],
    ['float', 'number'],
    ['std::string', 'string'],
    ['Saleae::Graph::Vec2', 'Vec2'],
    ['Saleae::Graph::RenderResponseData::ValueSet', 'ValueSet'],
]

number_types = ['int', 'double', 'float']


def convert_name(original):
    # handle members.
    if len(original) >= 2 and original[0] == 'm' and original[1].isupper():
        new_string = original[1].lower() + original[2:]
        return new_string
    return original


def convert_type(original):
    if "::" in original:
        return original[original.rfind('::')+2:]
    if any([number_type == original for number_type in number_types]):
        return 'number'
    return original


for pair in name_test_set:
    input = pair[0]
    expected = pair[1]
    actual = convert_name(input)
    result = actual == expected
    print(('✔ ' if result else ' FAILED: ') + pair[0] + ' -> ' + actual + ' [' + pair[1] + ']')

print('\nTesting types:')
for pair in type_test_set:
    input = pair[0]
    expected = pair[1]
    actual = convert_type(input)
    result = actual == expected
    print(('✔ ' if result else ' FAILED: ') + pair[0] + ' -> ' + actual + ' [' + pair[1] + ']')
