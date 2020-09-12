import re
from re import search

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
    ['node_type', 'nodeType'],
    ['node_id', 'nodeId'],
    ['from_node_id', 'fromNodeId'],
    ['from_port', 'fromPort'],
    ['from_port_index', 'fromPortIndex'],
    ['to_node_id', 'toNodeId'],
    ['to_port', 'toPort'],
    ['to_port_index', 'toPortIndex'],
    ['pipe_id', 'pipeId'],
    ['producer_node_id', 'producerNodeId'],
    ['consumer_node_id', 'consumerNodeId'],
    ['pipe_subscription_id', 'pipeSubscriptionId'],
    ['action', 'action'],
    ['state_subscription_id', 'stateSubscriptionId'],
]


type_test_set = [
    ['int', 'number'],
    ['double', 'number'],
    ['float', 'number'],
    ['std::string', 'string'],
    ['Saleae::Graph::Vec2', 'Vec2'],
    ['Saleae::Graph::RenderResponseData::ValueSet', 'ValueSet'],
    ['std::vector<double>', 'number[]'],
    ['std::map<int, std::string>', 'Map<number, string>'],
    ['std::map<int, Saleae::Graph::Vec2>', 'Map<number, Vec2>'],
    ['std::map<int, std::vector<std::string>>', 'Map<number, string[]>'],
    ['std::map<int, std::vector<Saleae::Graph::Vec2>>', 'Map<number, Vec2[]>'],
]

number_types = ['int', 'double', 'float']


def replace_character(str, index, new_char):
    temp = list(str)
    temp[index] = new_char
    return ''.join(temp)


def convert_name_for_json(original):
    if len(original) >= 2 and original[0] == 'm' and original[1].isupper():
        # handle members.
        new_string = original[1].lower() + original[2:]
        return new_string
    if '_' in original:
        # handle snake case
        new_string = original
        while '_' in new_string:
            index = new_string.find('_')
            new_string = new_string[0: index:] + new_string[index + 1::]
            if index < len(new_string):
                new_string = replace_character(new_string, index, new_string[index].upper())
        return new_string
    return original


def convert_type_for_ts(original):
    ts_type = original
    scope_range = ts_type
    if "<" in scope_range:
        scope_range = scope_range[0: scope_range.find("<")]
    if "::" in scope_range:
        ts_type = ts_type[scope_range.rfind('::', 0, )+2:]
    if any([number_type == ts_type for number_type in number_types]):
        ts_type = 'number'
    vec = re.search("^vector<(.+)>$", ts_type)
    if vec:
        ts_type = convert_type_for_ts(vec.group(1)) + "[]"
    map = re.search("^map<(.+),(.+)>$", ts_type)
    if map:
        ts_type = "Map<{}, {}>".format(convert_type_for_ts(map.group(1)), convert_type_for_ts(map.group(2)))
    return ts_type


any_failed = False

for pair in name_test_set:
    input = pair[0]
    expected = pair[1]
    actual = convert_name_for_json(input)
    result = actual == expected
    print(('✔ ' if result else ' FAILED: ') + pair[0] + ' -> ' + actual + ' [' + pair[1] + ']')
    if not result:
        any_failed = True


print('\nTesting types:')
for pair in type_test_set:
    input = pair[0]
    expected = pair[1]
    actual = convert_type_for_ts(input)
    result = actual == expected
    print(('✔ ' if result else ' FAILED: ') + pair[0] + ' -> ' + actual + ' [' + pair[1] + ']')
    if not result:
        any_failed = True

if any_failed:
    quit()
