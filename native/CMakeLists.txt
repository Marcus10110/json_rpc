cmake_minimum_required(VERSION 3.9)

project(rpc_sample CXX)

include(ExternalProject)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

#This tells all compilers to use the C++ 17 standard.
set(CMAKE_CXX_STANDARD 17)

add_executable(main src/main.cpp src/server.cpp src/render_data.cpp src/render_data.gen2.cpp src/json_archive.cpp)

list(APPEND CEREAL_CMAKE_ARGS "-DJUST_INSTALL_CEREAL=ON")

set(EXTERNAL_INSTALL_PREFIX "external_install")

get_filename_component(EXTERNAL_INSTALL_PREFIX ${EXTERNAL_INSTALL_PREFIX}
                        ABSOLUTE BASE_DIR ${PROJECT_BINARY_DIR})

list(APPEND CEREAL_CMAKE_ARGS
    "-DCMAKE_INSTALL_PREFIX=${EXTERNAL_INSTALL_PREFIX}"
    "-DCMAKE_CXX_COMPILER=${CMAKE_CXX_COMPILER}"
)
if (DEFINED CMAKE_C_COMPILER)
   list(APPEND CEREAL_CMAKE_ARGS "-DCMAKE_C_COMPILER=${CMAKE_C_COMPILER}")
endif()

if ("${CMAKE_CXX_COMPILER_ID}" STREQUAL "Clang")
    list(APPEND CEREAL_CMAKE_ARGS "-DCMAKE_CXX_FLAGS=-std=c++17 -stdlib=libc++" "-DCMAKE_EXE_LINKER_FLAGS=-stdlib=libc++ -lc++abi")
endif()

message("CEREAL_BUILD_BYPRODUCTS: ${CEREAL_BUILD_BYPRODUCTS}")

ExternalProject_Add(
    cereal
    GIT_REPOSITORY      git@github.com:USCiLab/cereal.git
    GIT_TAG             v1.3.0
    GIT_SHALLOW         1
    CMAKE_ARGS          ${CEREAL_CMAKE_ARGS}
    PREFIX              ${CMAKE_BINARY_DIR}/external/cereal/prefix
    TMP_DIR             ${CMAKE_BINARY_DIR}/external/cereal/tmp
    STAMP_DIR           ${CMAKE_BINARY_DIR}/external/cereal/stamp
    DOWNLOAD_DIR        ${CMAKE_BINARY_DIR}/external/cereal/download
    SOURCE_DIR          ${CMAKE_BINARY_DIR}/external/cereal/src
    BINARY_DIR          ${CMAKE_BINARY_DIR}/external/cereal/build
    BUILD_BYPRODUCTS    ${CEREAL_BUILD_BYPRODUCTS}
    UPDATE_DISCONNECTED 1
)


# RapidJSON is a header only library. This section downloads it and makes it.
list(APPEND RAPIDJSON_CMAKE_ARGS "-DRAPIDJSON_BUILD_EXAMPLES=OFF")
list(APPEND RAPIDJSON_CMAKE_ARGS "-DRAPIDJSON_BUILD_TESTS=OFF")
list(APPEND RAPIDJSON_CMAKE_ARGS "-DRAPIDJSON_BUILD_DOC=OFF")
list(APPEND RAPIDJSON_CMAKE_ARGS     
"-DCMAKE_INSTALL_PREFIX=${EXTERNAL_INSTALL_PREFIX}"
"-DCMAKE_CXX_COMPILER=${CMAKE_CXX_COMPILER}"
)
# v1.1.0 -> f54b0e47a08782a6131cc3d60f94d038fa6e0a51
ExternalProject_Add(
    rapidjson
    GIT_REPOSITORY      https://github.com/Tencent/rapidjson.git
    GIT_TAG             f54b0e47a08782a6131cc3d60f94d038fa6e0a51
    GIT_SHALLOW         1
    CMAKE_ARGS          ${RAPIDJSON_CMAKE_ARGS}
    PREFIX              ${CMAKE_BINARY_DIR}/external/rapidjson/prefix
    TMP_DIR             ${CMAKE_BINARY_DIR}/external/rapidjson/tmp
    STAMP_DIR           ${CMAKE_BINARY_DIR}/external/rapidjson/stamp
    DOWNLOAD_DIR        ${CMAKE_BINARY_DIR}/external/rapidjson/download
    SOURCE_DIR          ${CMAKE_BINARY_DIR}/external/rapidjson/src
    BINARY_DIR          ${CMAKE_BINARY_DIR}/external/rapidjson/build
    BUILD_BYPRODUCTS    ${RAPIDJSON_BUILD_BYPRODUCTS}
    UPDATE_DISCONNECTED 1
)


include_directories(include)
include_directories(SYSTEM ${EXTERNAL_INSTALL_PREFIX}/include)


add_dependencies(main cereal rapidjson)