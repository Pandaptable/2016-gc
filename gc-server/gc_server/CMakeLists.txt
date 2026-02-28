project(gc-server)

add_executable(gc-server WIN32
    main.cpp
    networking.cpp
    networking_users.cpp
    networking_inventory.cpp
    gc_message.cpp
    steam_network_message.cpp
    logger.cpp
    
    inventory.cpp
    item_schema.cpp
    keyvalue.cpp
    keyvalue_english.cpp
    random.cpp)

target_precompile_headers(gc-server PRIVATE stdafx.h)
set_target_properties(gc-server PROPERTIES PREFIX "")
set_target_properties(gc-server PROPERTIES OUTPUT_NAME gc-server${GC_EXE_SUFFIX})
if(UNIX AND NOT APPLE)
    set_target_properties(gc-server PROPERTIES POSITION_INDEPENDENT_CODE ON)
endif()

# Only set subsystem and Windows-specific options for MSVC
if (MSVC)
    target_link_options(gc-server PRIVATE /SUBSYSTEM:CONSOLE)
    target_compile_options(gc-server PRIVATE /W4 /wd4244)
    target_compile_definitions(gc-server PRIVATE *CRT*SECURE_NO_WARNINGS)
endif()

file(GLOB PROTOBUFS ../protobufs/*.cc)

if(IS_32BIT)
    set(MARIADB_LIBRARY "/usr/lib/i386-linux-gnu/libmariadb.a")
endif()

target_include_directories(gc-server PRIVATE
    ${protobuf_SOURCE_DIR}/src
    ../protobufs
    ${MARIADB_INCLUDE_DIRS}
    ${MARIADB_INCLUDE_DIR} # for windows
)

target_sources(gc-server PRIVATE ${PROTOBUFS})
source_group("Protobufs" FILES ${PROTOBUFS})

target_link_libraries(gc-server PRIVATE
    cryptopp
    protobuf::libprotobuf
    steam_api
    -Wl,-whole-archive ${MARIADB_LIBRARY} -Wl,-no-whole-archive
    -lpthread 
    -lm 
    -ldl 
    -lz
    -lssl
    -lcrypto
)
   
# apple message box
if (APPLE)
    target_link_libraries(gc-server PRIVATE "-framework Foundation")
endif()

if (MSVC)
    # we need large address awareness and a larger stack to not crash
    target_link_options(gc-server PRIVATE /LARGEADDRESSAWARE /STACK:1572864)
endif()

if (OUTDIR)
    add_custom_command(TARGET gc-server POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy
        $<TARGET_FILE:gc-server>
        ${OUTDIR}/gc-server/${GC_LIB_DIR}/$<TARGET_FILE_NAME:gc-server>)
endif()