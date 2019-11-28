project(rpc_sample CXX)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

#This tells all compilers to use the C++ 17 standard.
set(CMAKE_CXX_STANDARD 17)

add_executable(main src/main.cpp src/server.cpp)