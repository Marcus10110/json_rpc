#pragma once
#include <optional>
#include <cstdint>
#include <vector>
#include <stdexcept>
#include <string>

#include "rapidjson/document.h"
#include "rapidjson/pointer.h"

namespace Saleae
{
    struct Archive
    {
        rapidjson::Document::AllocatorType* mAllocator;
        std::optional<rapidjson::Value> mValue;
        bool IsSave( );
    };

    void ArchiveJson( int16_t& target, Archive& archive );

    template <class T>
    struct IsRapidJsonType : std::false_type { };

    // types that "just work" with get/set/is functions of rapidjson.
    template <> struct IsRapidJsonType<bool> : std::true_type {};
    template <> struct IsRapidJsonType<int> : std::true_type {};
    template <> struct IsRapidJsonType<unsigned> : std::true_type {};
    template <> struct IsRapidJsonType<int64_t> : std::true_type {};
    template <> struct IsRapidJsonType<uint64_t> : std::true_type {};
    template <> struct IsRapidJsonType<double> : std::true_type {};
    template <> struct IsRapidJsonType<float> : std::true_type {};
    template <> struct IsRapidJsonType<std::string> : std::true_type {};

    template <typename T>
    std::enable_if_t<IsRapidJsonType<T>::value> ArchiveJson( T& target, Archive& archive );

    template <typename T>
    void ArchiveJson( std::vector<T>& target, Archive& archive );

    template <typename T, typename CharType, size_t N>
    void ArchiveByPointer( T& target, const CharType( &pointer )[ N ], Archive& archive );


    // Template Implementations:
    template <typename T>
    std::enable_if_t<IsRapidJsonType<T>::value> ArchiveJson( T& target, Archive& archive )
    {
        if( archive.IsSave() )
        {
            archive.mValue.emplace();
            archive.mValue->Set<T>( target );
        }
        else
        {
            if( !archive.mValue || !archive.mValue->Is<T>() )
            {
                throw std::runtime_error( "json value is not an int" );
            }
            target = archive.mValue->Get<T>();
        }
    }

    template <typename T>
    void ArchiveJson( std::vector<T>& target, Archive& archive )
    {
        
        if( archive.IsSave() )
        {
            archive.mValue.emplace();
            archive.mValue->SetArray( );
            for( auto& element : target )
            {
                Archive target_archive{ archive.mAllocator };
                ArchiveJson( element, target_archive );
                archive.mValue->PushBack( *target_archive.mValue, *archive.mAllocator );
            }
        }
        else
        {
            if( !archive.mValue || !archive.mValue->IsArray() )
            {
                throw std::runtime_error( "json value is not an array" );
            }
            target.clear();

            for( auto& v : archive.mValue->GetArray() )
            {
                T new_value;
                Archive target_archive{ nullptr, std::move(v) };
                ArchiveJson( new_value, target_archive );
                target.push_back( new_value );
            }
        }
        
    }

    template <typename T, typename CharType, size_t N>
    void ArchiveByPointer( T& target, const CharType ( &pointer )[ N ], Archive& archive )
    {
        if( archive.IsSave() )
        {
            Archive target_archive{ archive.mAllocator };
            ArchiveJson( target, target_archive );
            if( target_archive.mValue ) // empty indicates it should not be added to the json.
            {
                // if the existing value isn't already created, create it.
                if( !archive.mValue )
                {
                    archive.mValue.emplace();
                }
                SetValueByPointer( *archive.mValue, pointer, *target_archive.mValue, *archive.mAllocator );
            }
        }
        else
        {
            auto* load_value = rapidjson::Pointer( pointer ).Get( *archive.mValue );
            if( load_value )
            {
                Archive load_ar{ nullptr, std::move( *load_value ) };
                ArchiveJson( target, load_ar );
            }
        }
    }
}