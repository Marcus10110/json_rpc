#include "json_archive.h"

#include <stdexcept>
#include <iostream>
namespace Saleae
{
    bool Archive::IsSave( )
    {
        return mAllocator != nullptr;
    }
    
    void ArchiveJson( int16_t& target, Archive& archive )
    {
        // handle as if it was a int.
        int target_proxy = target;
        ArchiveJson( target_proxy, archive );
        target = target_proxy;
    }
}
