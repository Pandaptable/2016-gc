#include "stdafx.h"
#include "main.hpp"
#include "platform.hpp"

#include <dlfcn.h>
#define STEAM_API_EXPORTS
#include <steam/steam_gameserver.h>

int main() {
#ifdef _WIN32
    if (!platform::win32_enable_vt_mode()) {
        printf("Couldn't enable virtual terminal mode! Continuing with colors disabled!");
        logger::disable_colors();
    }
#endif

#ifdef _WIN32
    if (!GetEnvironmentVariableA("SteamAppId", nullptr, 0)) {
        SetEnvironmentVariableA("SteamAppId", "730");
    }
#else
    setenv("SteamAppId", "730", 0);
#endif

    if (!SteamGameServer_Init(0, 21818, STEAMGAMESERVER_QUERY_PORT_SHARED, eServerModeAuthentication, "1.0.0")) {
        logger::error("Failed to initialize Steam!");
        return 0;
    }
    SteamGameServer()->LogOnAnonymous();

    m_network.Init();
	while (true) {
        m_network.Update();
	}
	return 1;
}