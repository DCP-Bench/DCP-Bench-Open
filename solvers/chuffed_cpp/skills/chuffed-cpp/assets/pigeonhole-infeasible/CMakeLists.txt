cmake_minimum_required(VERSION 3.18)
project(model LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release)
endif()
find_package(chuffed CONFIG REQUIRED)   # found through CMAKE_PREFIX_PATH
find_package(Threads REQUIRED)
add_executable(model model.cpp)
target_include_directories(model PRIVATE ${CHUFFED_INCLUDE_DIRS})
# chuffed twice on purpose: the static libraries depend on each other
target_link_libraries(model PRIVATE chuffed chuffed_fzn chuffed Threads::Threads)
