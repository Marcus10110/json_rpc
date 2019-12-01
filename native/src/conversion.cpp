#include "converstion.h"
#include <exception>
namespace Saleae
{
    std::shared_ptr<const Saleae::Graph::Data> LoadRegisteredType( cereal::JSONInputArchive& archive )
    {
        std::string loaded_type_name;
        archive( cereal::make_nvp( "TypeId", loaded_type_name ) );
        if( RegisteredDataTypeLoaders.count( loaded_type_name ) > 0 )
        {
            return RegisteredDataTypeLoaders.at( loaded_type_name )( archive );
        }
        throw std::runtime_error( "unable to find loader for " + loaded_type_name );
    }
}