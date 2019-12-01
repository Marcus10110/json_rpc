#include "render_data.h"
#include "converstion.h"

namespace Saleae::Graph
{
    int64_t RenderRequestData::GetMemoryBytes() const noexcept
    {
        return 1;
    }

    int64_t RenderResponseData::GetMemoryBytes() const noexcept
    {
        return 1;
    }
}