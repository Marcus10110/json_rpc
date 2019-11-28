#include <iostream>
#include "server.h"

namespace Api
{
    int GraphServer::AddNode( std::string note_type )
    {
        std::cout << __FUNCTION__ << " called!\n";
        return 4;
    }

    void GraphServer::RemoveNode( int node_id )
    {
        std::cout << __FUNCTION__ << " called!\n";
    }
    int GraphServer::ConnectPipe( int from_node_id, std::string from_port, int from_port_index, int to_node_id, std::string to_port,
                                  int to_port_index )
    {
        std::cout << __FUNCTION__ << " called!\n";
        return 0;
    }
    void GraphServer::DisconnectPipe( int pipe_id )
    {
        std::cout << __FUNCTION__ << " called!\n";
    }
    int GraphServer::ConnectApi( int producer_node_id, int consumer_node_id )
    {
        std::cout << __FUNCTION__ << " called!\n";
        return 0;
    }
    void GraphServer::DisconnectApi( int api_id )
    {
        std::cout << __FUNCTION__ << " called!\n";
    }
    void GraphServer::PushToPipe( int node_id, std::string port, int port_id, std::string data )

    {
        std::cout << __FUNCTION__ << " called!\n";
    }
    int GraphServer::SubscribeToPipe( int node_id, std::string port, int port_id )
    {
        std::cout << __FUNCTION__ << " called!\n";
        return 0;
    }
    void GraphServer::UnsubscribeToPipe( int pipe_subscription_id )
    {
        std::cout << __FUNCTION__ << " called!\n";
    }
    std::string GraphServer::DispatchAction( int node_id, std::string action )
    {
        std::cout << __FUNCTION__ << " called!\n";
        return "";
    }
    std::string GraphServer::GetNodeState( int node_id )
    {
        std::cout << __FUNCTION__ << " called!\n";
        return "";
    }
    int GraphServer::SubscribeToNodeState( int node_id )
    {
        std::cout << __FUNCTION__ << " called!\n";
        return 0;
    }
    void GraphServer::UnsubscribeToNodeState( int state_subscription_id )
    {
        std::cout << __FUNCTION__ << " called!\n";
    }
} // namespace Api