#include "server.h"
#include <iostream>
#include <exception>
#include "server.gen.h"

int main()
{
    std::cout << "hello world!\n";
    Api::GraphServer server;

    try
    {
        ParseMessage( server, R"({ 
            "function": "DispatchAction",
            "node_id": 7 ,
            "action": "stuff"
        })" );
    }
    catch( std::exception& ex )
    {
        std::cout << "error: " << ex.what() << "\n";
    }
    return 0;
}