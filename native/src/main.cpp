#include "server.h"
#include <iostream>
#include <exception>
#include "render_data.h"
#include "server.gen.h"
#include "render_data.gen.h"

int main()
{
    // test handling a json RPC call.
    Api::GraphServer server;

    try
    {
        Api::ParseMessageForGraphServer( server, R"({ 
            "function": "DispatchAction",
            "node_id": 7,
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

    Saleae::Graph::RenderResponseData render_response{ 42, { { 1, 2, 3, 4 }, 0, 1E9 }, { { { { 1, 2 }, { 3, 4 } } } } };
    Saleae::Graph::serialize( archive, render_response );
    std::cout << "RenderResponseData serialization example:" << ss.str() << "\n";
    return 0;
}