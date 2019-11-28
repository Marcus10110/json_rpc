#include <string>

namespace Api
{
    class GraphServer
    {
        public:
            int AddNode( std::string node_name );
    };

    
    enum Mark {A, B};
    enum class Mark2{C, D};

};

struct BStruct {
    int TestMe();
    int AnotherTest( std::string param1, std::string param2, int param3);
};