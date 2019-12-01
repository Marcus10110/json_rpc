#pragma once
#include <vector>
#include <cstdint>

// tag classes to auto-generate with GENERATE
#ifdef __CODE_GENERATOR__
#define GENERATE_RPC __attribute__( ( annotate( "generateRpc" ) ) )
#define GENERATE_CEREAL __attribute__( ( annotate( "generateCereal" ) ) )
#else
#define GENERATE_RPC
#define GENERATE_CEREAL
#endif

namespace Saleae::Graph
{
    struct GENERATE_CEREAL RenderRequestData
    {
        int mId;
        int mWidthPx;
        double mLeftEdgeTime;
        double mSecondsPerPx;
    };

    struct GENERATE_CEREAL Vec2
    {
        float mX{ 0.0f };
        float mY{ 0.0f };
    };

    struct GENERATE_CEREAL Line
    {
        Vec2 mFrom;
        Vec2 mTo;
    };

    struct GENERATE_CEREAL RenderResponseData
    {
        int mId;

        struct GENERATE_CEREAL ValueSet
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