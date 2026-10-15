cmake_minimum_required(VERSION 3.18)
project(model LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(ortools CONFIG REQUIRED)

add_executable(model model.cc)
target_link_libraries(model PRIVATE ortools::ortools)
