// This file is auto-generated by the jankiest code evr!

% for ns in params['namespaces']:
% for Class in ns['classes']:
export interface ${Class['ts_name']} {
% for m in Class['members']:
    ${m['json_name']}: ${m['ts_type']};
% endfor
}
% endfor
% endfor
