#pragma once
#include <vector>
#include <cstdint>
#include "graph_time.h"

// tag classes to auto-generate with GENERATE
#ifdef __CODE_GENERATOR__
#define GENERATE_RPC __attribute__( ( annotate( "generate" ) ) )
#else
#define GENERATE_RPC
#endif

namespace Saleae::Graph
{
    class Data
    {
        virtual int64_t GetMemoryBytes() const noexcept = 0;
    };

    struct GENERATE_ARCHIVE RenderRequestData : public Data
    {
        int64_t GetMemoryBytes() const noexcept override;

        int mId;
        int mWidthPx;
        double mLeftEdgeTime;
        double mSecondsPerPx;
        GraphTime mStartGraphTime;
    };

    struct GENERATE_ARCHIVE Vec2
    {
        float mX{ 0.0f };
        float mY{ 0.0f };
    };

    struct GENERATE_ARCHIVE Line
    {
        Vec2 mFrom;
        Vec2 mTo;
    };

    struct GENERATE_ARCHIVE RenderResponseData : public Data
    {
        int64_t GetMemoryBytes() const noexcept override;

        int mId;

        struct GENERATE_ARCHIVE ValueSet
        {
            using AnalogValue = int16_t;
            std::vector<AnalogValue> mValues;
            double mFirstSampleTime;
            double mSampleRate{ 0.0 };
        };

        ValueSet mValueSet;

        std::vector<Line> mLines;

        std::vector<Vec2> mLineStrip;
    };
}