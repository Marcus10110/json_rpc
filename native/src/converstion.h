#pragma once
#include <string>
#include <functional>
#include <map>
#include <memory>
#include <cassert>

#include <cereal/archives/json.hpp>

#include "render_data.h"

namespace Saleae
{
    extern std::map<std::string, std::function<std::shared_ptr<const Saleae::Graph::Data>( cereal::JSONInputArchive& archive )>>
        RegisteredDataTypeLoaders;
    // type registration system exclusively used for converting unknown strings to the correct class type.
    template <typename TData>
    int RegisterDataType( std::string type_name )
    {
        std::function<std::shared_ptr<const Saleae::Graph::Data>( cereal::JSONInputArchive & archive )> loader_function =
            [type_name]( cereal::JSONInputArchive& archive ) -> std::shared_ptr<Saleae::Graph::Data> {
            std::string loaded_type_name;
            archive( cereal::make_nvp( "TypeId", loaded_type_name ) );
            assert( loaded_type_name == type_name );

            std::shared_ptr<TData> temp = std::make_shared<TData>();
            archive( cereal::make_nvp( type_name, *temp ) );
            return temp;
        };

        RegisteredDataTypeLoaders[ type_name ] = loader_function;
        return 0;
    }

    std::shared_ptr<const Saleae::Graph::Data> LoadRegisteredType( cereal::JSONInputArchive& archive );
}