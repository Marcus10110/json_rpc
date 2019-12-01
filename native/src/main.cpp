#include "server.h"
#include <iostream>
#include <exception>
#include "render_data.h"
#include "server.gen.h"
#include "render_data.gen.h"
#include "converstion.h"


std::map<std::string, std::function<std::shared_ptr<const Saleae::Graph::Data>( cereal::JSONInputArchive& archive )>>
    Saleae::RegisteredDataTypeLoaders;

static int a = Saleae::RegisterDataType<Saleae::Graph::RenderRequestData>( "Saleae::Graph::RenderRequestData" );
static int b = Saleae::RegisterDataType<Saleae::Graph::RenderResponseData>( "Saleae::Graph::RenderResponseData" );

int main()
{
    // test handling a json RPC call.
    Api::GraphServer server;

    try
    {
        Api::ParseMessageForGraphServer( server, R"({ 
            "function": "DispatchAction",
            "nodeId": 7,
            "action": "stuff"
        })" );
    }
    catch( std::exception& ex )
    {
        std::cout << "error: " << ex.what() << "\n";
    }

    // Test serializing a Data object.
    std::stringstream ss;
    cereal::JSONOutputArchive archive( ss );

    Saleae::Graph::RenderResponseData render_response;
    render_response.mId = 42;
    render_response.mValueSet = { { 1, 2, 3, 4 }, 0, 1e9 };
    render_response.mLines = { { { 1, 2 }, { 3, 4 } } };
    Saleae::Graph::serialize( archive, render_response );
    std::cout << "RenderResponseData serialization example:\n" << ss.str() << "\n";


    // attempt dynamic load:
    std::string input_json = R"({
        "TypeId": "Saleae::Graph::RenderRequestData",
        "Saleae::Graph::RenderRequestData": {
            "id": 42,
            "widthPx": 1,
            "leftEdgeTime": 1,
            "secondsPerPx": 1
        }
    })";

    std::stringstream ss2( input_json );
    cereal::JSONInputArchive archive2( ss2 );

    auto loaded_render_request_data = Saleae::LoadRegisteredType( archive2 );
    auto casted_object = std::dynamic_pointer_cast<const Saleae::Graph::RenderRequestData>( loaded_render_request_data );
    std::cout << "dynamic load serialization example:\n";
    std::cout << "mId: " << casted_object->mId << "\n";
    std::cout << "mWidthPx: " << casted_object->mWidthPx << "\n";
    std::cout << "mLeftEdgeTime: " << casted_object->mLeftEdgeTime << "\n";
    std::cout << "mSecondsPerPx: " << casted_object->mSecondsPerPx << "\n";
    return 0;
}