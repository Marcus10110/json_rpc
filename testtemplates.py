from mako.template import Template


rpcHeaderTemplate = Template(filename='rpc_header.mako')
rpcSourceTemplate = Template(filename='rpc_source.mako')

namespaces = [{'name': "Saleae::Graph",
               'classes': [{'name': 'GraphServer', 'methods': [
                   {'name': 'AddNode', 'returnType': 'int', 'args': [
                       {'name': 'node_type', 'type': 'std::string'}]}
               ]}]}]

template_parameters = {
    'include': 'graph_server.h',
    'namespaces': namespaces
}
print('template_parameters', template_parameters)
print('*template_parameters', *template_parameters)

generatedHeader = rpcHeaderTemplate.render(
    params=template_parameters
)

print(generatedHeader)
generatedSource = rpcSourceTemplate.render(params=template_parameters)

print(generatedSource)
