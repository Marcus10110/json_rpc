// This file is auto-generated by the jankiest code evr!
#pragma once
%if needs_converter == True:
#include "converter.h"
%endif
#include "${params['include']}"

namespace Saleae
{
    struct Archive;
}

% for ns in params['namespaces']:
% if ns['name'] == '':
% for Class in ns['classes']:
void ArchiveJson(${Class['full_name']}& target, Saleae::Archive& archive );
% endfor
% else:
namespace ${ns['name']} 
{
% for Class in ns['classes']:
    void ArchiveJson(${Class['full_name']}& target, Archive& archive );
% endfor
%if any([class_['extends_data'] for class_ in ns['classes']]):

% for Class in ns['classes']:
%if Class['extends_data'] == True:
    using ${Class['name']}ArchiveJsonConverter = ArchiveJsonConverter<${Class['full_name']}>;
%endif
% endfor
%endif
}
%endif
% endfor
