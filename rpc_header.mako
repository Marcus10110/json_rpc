// This file is auto-generated by the jankiest code evr!
#pragma once
#include <string>
#include <cereal/archives/json.hpp>
#include "${params['include']}"

% for ns in params['namespaces']:
namespace ${ns['name']} 
{
% for Class in ns['classes']:
    std::string ParseMessageFor${Class['name']}( ${Class['name']}& target, std::string message );
% endfor
}
% endfor