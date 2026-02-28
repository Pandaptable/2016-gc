#ifndef NETWORKING_H
#define NETWORKING_H

#include "steam/steam_api.h"
#include <mariadb/mysql.h>

#include <ctime> // time_t
#include <map> // std::map

#include "networking_users.hpp"

constexpr int NetMessageSendFlags = 8; //k_nSteamNetworkingSend_Reliable
constexpr int NetMessageChannel = 7;

class ClientSessions {
	public:
		CSteamID steamID;
		SNetSocket_t socket;

		bool isAuthenticated;
		time_t lastActivity;
		uint64_t lastCheckedItemId;
		bool itemIdInitialized;
	
		ClientSessions(CSteamID id) : 
			steamID(id), 
			isAuthenticated(false), 
			lastCheckedItemId(0),
			itemIdInitialized(false),
			socket(k_HSteamNetConnection_Invalid) {
			time(&lastActivity);
		}
	   
		void updateActivity() {
			time(&lastActivity);
		}
	};

class GCNetwork {
private:
	//STEAM_CALLBACK(GCNetwork, SocketStatusCallback, SocketStatusCallback_t, m_SocketStatusCallback);
	CCallbackManual<GCNetwork, SocketStatusCallback_t> m_SocketStatusCallback;
	void SocketStatusCallback(SocketStatusCallback_t* pParam);

	// client sessions
	std::map<uint64, ClientSessions> m_activeSessions;
	uint64_t GetSessionSteamId(SNetSocket_t socket);

	// db connections
	MYSQL* m_mysql1; // classiccounter
	MYSQL* m_mysql2; // inventory
	MYSQL* m_mysql3; // ranked

	// whitelist
	bool m_maintenanceMode = true; // false disables whitelist (add steamids to list below)
    std::vector<uint64_t> m_maintenanceAllowlist = {
        76561199119646639, // ollum
        76561198385236467, // grizzle
        76561199134853281  // vallu
    };
    bool IsUserWhitelisted(uint64_t steamID64, MYSQL* classiccounter_db);
	
public:
	GCNetwork();
	~GCNetwork();
	void Init();
	void Update();

    void ReadAuthTicket(SNetSocket_t p2psocket, void* message, uint32 msgsize, 
		MYSQL* classiccounter_db, MYSQL* inventory_db, MYSQL* ranked_db);
	
	// db methods
	bool InitDatabases();
	bool ExecuteQuery(MYSQL* connection, const char* query);
	void CloseDatabases();

	// client sessions
	void CleanupSessions();
	void CheckNewItemsForActiveSessions();
};

#endif