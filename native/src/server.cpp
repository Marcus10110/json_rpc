#include "server.h"

namespace Api
{
    int GraphServer::AddNode( std::string note_type )
    {
        return 4;
    }

    void GraphServer::RemoveNode( int node_id )
    {
    }
    int GraphServer::ConnectPipe( int from_node_id, std::string from_port, int from_port_index, int to_node_id, std::string to_port,
                                  int to_port_index )
    {
        return 0;
    }
    void GraphServer::DisconnectPipe( int pipe_id )
    {
    }
    int GraphServer::ConnectApi( int producer_node_id, int consumer_node_id )
    {
        return 0;
    }
    void GraphServer::DisconnectApi( int api_id )
    {
    }
    void GraphServer::PushToPipe( int node_id, std::string port, int port_id, std::string data )

    {
    }
    int GraphServer::SubscribeToPipe( int node_id, std::string port, int port_id )
    {
        return 0;
    }
    void GraphServer::UnsubscribeToPipe( int pipe_subscription_id )
    {
    }
    std::string GraphServer::DispatchAction( int node_id, std::string action )
    {
        return "";
    }
    std::string GraphServer::GetNodeState( int node_id )
    {
        return "";
    }
    int GraphServer::SubscribeToNodeState( int node_id )
    {
        return 0;
    }
    void GraphServer::UnsubscribeToNodeState( int state_subscription_id )
    {
    }
} // namespace Api