//#include "server.h"
#include <iostream>
#include <exception>
#include "render_data.h"
//#include "server.gen.h"
//#include "render_data.gen.h"
// note, we can't mix cereal and rapidjson in the same file since they use different copies of rapidjson.
// #include "converstion.h"

#include "json_archive.h"
#include "render_data.gen2.h"


#include "rapidjson/writer.h"

using namespace Saleae::Graph;

void PrintDoc( rapidjson::Document& doc )
{
    rapidjson::StringBuffer buffer;
    rapidjson::Writer<rapidjson::StringBuffer> writer( buffer );
    doc.Accept( writer ); // NOLINT
    std::cout << buffer.GetString( ) << "\n";
}

void Test( )
{
    RenderRequestData render_request;
    render_request.mId = 42;
    render_request.mWidthPx = 300;
    render_request.mLeftEdgeTime = 42.42;
    render_request.mSecondsPerPx = 0.001;

    rapidjson::Document doc;
    auto& a = doc.GetAllocator( );
    Saleae::Archive ar{ &a };

    ArchiveJson( render_request, ar );

    doc.CopyFrom( *ar.mValue, a );

    PrintDoc( doc );

    // test load:
    Saleae::Archive load_ar{ nullptr, std::move(ar.mValue) };
    RenderRequestData loaded_request;

    ArchiveJson( loaded_request, load_ar );

    std::cout << "original: " << render_request.mId << "; loaded: " << loaded_request.mId << "\n";

    RenderResponseData render_response;
    render_response.mId = 42;
    render_response.mValueSet = { {1,2,3,4}, 0.001, 0.002 };
    render_response.mLines = { { {0,0}, {1,1} } };
    render_response.mLineStrip = { { 10, 20 } };

    rapidjson::Document doc2;
    auto& a2 = doc.GetAllocator( );
    Saleae::Archive ar2{ &a2 };
    ArchiveJson( render_response, ar2 );
    doc2.CopyFrom( *ar2.mValue, a2 );

    PrintDoc( doc2 );

    // test load:
    Saleae::Archive load_repsonse_ar{ nullptr, std::move(ar2.mValue) };
    RenderResponseData loaded_response;

    ArchiveJson( loaded_response, load_repsonse_ar );

    std::cout << "original: " << render_response.mId << "; loaded: " << loaded_response.mId << "\n";
}

int main( )
{
    Test( );
    return 0;
}