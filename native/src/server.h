#pragma once
#include <string>

// tag classes to auto-generate with GENERATE
#ifdef __CODE_GENERATOR__
#define GENERATE_RPC __attribute__( ( annotate( "generate" ) ) )
#define GENERATE_CEREAL __attribute__( ( annotate( "generate" ) ) )
#else
#define GENERATE_RPC
#define GENERATE_CEREAL
#endif

namespace Api
{
    class GENERATE_RPC GraphServer
    {
      public:
        int AddNode( std::string node_type );
        void RemoveNode( int node_id );
        int ConnectPipe( int from_node_id, std::string from_port, int from_port_index, int to_node_id, std::string to_port,
                         int to_port_index );
        void DisconnectPipe( int pipe_id );
        int ConnectApi( int producer_node_id, int consumer_node_id );
        void DisconnectApi( int api_id );
        void PushToPipe( int node_id, std::string port, int port_id, std::string data );
        int SubscribeToPipe( int node_id, std::string port, int port_id );
        void UnsubscribeToPipe( int pipe_subscription_id );
        std::string DispatchAction( int node_id, std::string action );
        std::string GetNodeState( int node_id );
        int SubscribeToNodeState( int node_id );
        void UnsubscribeToNodeState( int state_subscription_id );
    };
}; // namespace Api
