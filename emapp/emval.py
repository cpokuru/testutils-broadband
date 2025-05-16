from flask import Flask, render_template, request, jsonify, send_file
import sqlite3
import os
import json
from datetime import datetime
import tempfile

app = Flask(__name__)

# Load test structures
def load_test_structure():
    stages = [
        {"id": 1, "name": "Stage 1 - Gateway + Colocated Agent"},
        {"id": 2, "name": "Stage 2 - Onboard Remote Agent 1"},
        {"id": 3, "name": "Stage 3 - Onboard Remote Agent 2 to Remote Agent 1 (Daisy Chain)"},
        {"id": 4, "name": "Stage 4 - Onboard Remote Agent 3 to Gateway (Star)"},
        {"id": 5, "name": "Stage 5 - Code Tagging and Build"}
    ]
    
    test_cases = {
        1: [
            {
                "id": "1.0", 
                "description": "Boot device and configure",
                "details": "• Boot the device and wait until all radios are up and running\n• Configure DB and mesh configuration in nvram\n• Remove wifi db /opt/secure/wifi/*\n• Need to have updated one_wifi_prestart.sh\n• Need to have aishwarya Mac address changes\n• Restart onewifi\n• Wifi reset in DB using cli and update brlan0 mac address in colocated agent",
                "priority": "stage 2 blocker"
            },
            {
                "id": "1.1", 
                "description": "Bringup controller and colocated agent",
                "details": "• Start em controller\n• Start em agent\n• Restart em controller\n• Restart em agent",
                "priority": "stage 2 blocker"
            },
            {
                "id": "1.2", 
                "description": "Make sure onewifi is up and running",
                "details": "Verify onewifi service is running correctly",
                "priority": "stage 2 blocker"
            },
            {
                "id": "1.3", 
                "description": "Make sure em_ctrl is up and running",
                "details": "Verify em_ctrl service is running correctly",
                "priority": "stage 2 blocker"
            },
            {
                "id": "1.4", 
                "description": "Make sure em_agent is up and running",
                "details": "Verify em_agent service is running correctly",
                "priority": "stage 2 blocker"
            },
            {
                "id": "1.5", 
                "description": "All wifi interfaces/VAP's should have standard mac address",
                "details": "Verify all wifi interfaces/VAP's have standard mac address using aishwarya change",
                "priority": "stage 2 blocker"
            },
            {
                "id": "1.6", 
                "description": "Reboot device with persistent configuration",
                "details": "• Reboot the device and onewifi/ctrl/agent should be up and running with persistent configuration in EasyMeshconfig.json and InterfaceMap.json & standard serial number\n• No DB crash should observe\n• Cli should not crash\n• Play around with cli without changing any values (j,k,q)",
                "priority": "stage 2 blocker"
            },
            {
                "id": "1.7", 
                "description": "Change SSID from CLI and verify changes",
                "details": "• Changes SSID from cli and check iw dev after 2mins\n• New SSID should reflect in all 3 radios\n• No crash of controller/agent/Onewifi should happen\n• No kernel panic",
                "priority": "stage 2 blocker"
            },
            {
                "id": "1.8.1", 
                "description": "Wait 3 mins - SSID persistence check 1",
                "details": "• Wait for 3 mins\n• New SSID should persistent in all 3 radios\n• No crash of controller/agent/Onewifi should happen\n• No kernel panic",
                "priority": "stage 2 blocker"
            },
            {
                "id": "1.8.2", 
                "description": "Wait 3 mins - SSID persistence check 2",
                "details": "• Wait for 3 mins\n• New SSID should persistent in all 3 radios\n• No crash of controller/agent/Onewifi should happen\n• No kernel panic",
                "priority": "stage 2 blocker"
            },
            {
                "id": "1.8.3", 
                "description": "Wait 3 mins - SSID persistence check 3",
                "details": "• Wait for 3 mins\n• New SSID should persistent in all 3 radios\n• No crash of controller/agent/Onewifi should happen\n• No kernel panic",
                "priority": "stage 2 blocker"
            },
            {
                "id": "1.8.4", 
                "description": "Wait 3 mins - SSID persistence check 4",
                "details": "• Wait for 3 mins\n• New SSID should persistent in all 3 radios\n• No crash of controller/agent/Onewifi should happen\n• No kernel panic",
                "priority": "stage 2 blocker"
            },
            {
                "id": "1.8.5", 
                "description": "Wait 3 mins - SSID persistence check 5",
                "details": "• Wait for 3 mins\n• New SSID should persistent in all 3 radios\n• No crash of controller/agent/Onewifi should happen\n• No kernel panic",
                "priority": "stage 2 blocker"
            },
            {
                "id": "1.9", 
                "description": "Connect mobile phone to 2.4GHz private SSID",
                "details": "• Connect Mobile phone to private SSID (Try with 2.4GHz first)\n• Connection should be successful\n• Internet browsing should work\n• No crash of controller/agent/Onewifi should happen\n• No kernel panic",
                "priority": "stage 2 blocker"
            },
            {
                "id": "1.10", 
                "description": "Connect mobile phone to 5GHz private SSID",
                "details": "• Connect Mobile phone to private SSID (Try with 5GHz)\n• Connection should be successful\n• Internet browsing should work\n• No crash of controller/agent/Onewifi should happen\n• No kernel panic",
                "priority": "stage 2 blocker"
            },
            {
                "id": "1.11", 
                "description": "Connect mobile phone to 6GHz private SSID",
                "details": "• Connect Mobile phone to private SSID (Try with 6GHz)\n• Connection should be successful\n• Internet browsing should work\n• No crash of controller/agent/Onewifi should happen\n• No kernel panic",
                "priority": "stage 2 blocker"
            },
            {
                "id": "1.12", 
                "description": "Disconnect all client and keep device idle for 15 mins",
                "details": "• Disconnect all clients\n• Keep device idle for 15 mins",
                "priority": "stage 2 blocker"
            },
            {
                "id": "1.13", 
                "description": "Check iw dev after 15 mins",
                "details": "• Check iw dev after 15 mins\n• All radios should have the same SSID",
                "priority": "stage 2 blocker"
            },
            {
                "id": "1.14", 
                "description": "Try connecting to all bands individually and verify internet",
                "details": "• Try connecting to 2.4GHz/5GHz/6GHz individually and verify internet connection\n• Connection should be successful\n• Internet browsing should work\n• No crash of controller/agent/Onewifi should happen\n• No kernel panic",
                "priority": "stage 2 blocker"
            },
            {
                "id": "1.15", 
                "description": "Reboot device and retry test case 14",
                "details": "• Reboot the device\n• Try test case 14\n• No issues should be observed",
                "priority": "stage 2 blocker"
            },
            {
                "id": "1.16", 
                "description": "Repeat test case 15 multiple times",
                "details": "• Repeat test case 15 for 15 times with a time interval\n• Reboot command from terminal\n• Hard reset",
                "priority": "stage 2 blocker"
            },
            {
                "id": "1.17", 
                "description": "Factory reset the device",
                "details": "Perform a factory reset on the device",
                "priority": "Future"
            },
            {
                "id": "1.18", 
                "description": "Repeat with passcode and channel change",
                "details": "Repeat from test case 7 till test case 16 with passcode change and channel change",
                "priority": "Future"
            }
        ],
        2: [
        {
                "id": "2.0", 
                "description": "Boot device, configure for remote agent",
                "details": "• Boot the device and wait until all radios are up and running\n• Remove dnsmasq from /usr/bin\n• ifconfig erouter0 down\n• Do mesh configuration in nvram ----- make sure you make colocated mode 0\n• Remove wifi db /opt/secure/wifi/* (till Agent profile is up and running by Akhil P)\n• Need to have updated one_wifi_prestart.sh\n• Need to have aishwarya Mac address changes\n• Restart onewifi",
                "priority": "stage 3 blocker"
            },
            {
                "id": "2.1", 
                "description": "Make sure onewifi is up and running",
                "details": "Verify onewifi service is running correctly",
                "priority": "stage 3 blocker"
            },
            {
                "id": "2.2", 
                "description": "Validate agent communication with gateway",
                "details": "Validate:\n1. iw dev wifi1.1 info in Extender 1\n2. iw dev wifi1.1.sta1 info in ctrl\n3. iw dev wifi1.1.sta1 station dump in ctrl\n• Agent 1 device should communicate with gateway all the time",
                "priority": "stage 3 blocker"
            },
            {
                "id": "2.3", 
                "description": "Bringup EasyMesh agent and verify connectivity",
                "details": "• Bringup Easymesh agent\n• Check iw dev\n  • Agent 1 should show all ssid details for all radios\n• Set brlan0 with static ip\n• Perform ping test/wget http://10.0.0.1",
                "priority": "stage 3 blocker"
            },
            {
                "id": "2.4", 
                "description": "Test 2.4GHz connectivity with gateway private VAPs disabled",
                "details": "• Disable all private VAP's in gateway side & disable 5Ghz and 6Ghz radio in agent 1 device\n• Connect Mobile phone to private ssid's (Try with 2Ghz)\n  • Connection should be successful\n  • Internet browsing should work\n  • No crash of agent/Onewifi should happen\n  • No kernel panic",
                "priority": "stage 3 blocker"
            },
            {
                "id": "2.5", 
                "description": "Test 5GHz connectivity with gateway private VAPs disabled",
                "details": "• Disable all private VAP's in gateway side & disable 2.4Ghz and 6Ghz radio in agent 1 device\n• Connect Mobile phone to private ssid's (Try with 5Ghz)\n  • Connection should be successful\n  • Internet browsing should work\n  • No crash of agent/Onewifi should happen\n  • No kernel panic",
                "priority": "stage 3 blocker"
            },
            {
                "id": "2.6", 
                "description": "Test 6GHz connectivity with gateway private VAPs disabled",
                "details": "• Disable all private VAP's in gateway side & disable 2.4Ghz and 5Ghz radio in agent 1 device\n• Connect Mobile phone to private ssid's (Try with 6Ghz)\n  • Connection should be successful\n  • Internet browsing should work\n  • No crash of agent/Onewifi should happen\n  • No kernel panic",
                "priority": "stage 3 blocker"
            },
            {
                "id": "2.7", 
                "description": "Idle device connectivity check",
                "details": "Leave the device idle for 5 mins & check Agent 1 connectivity with gateway. There should not be any disconnection over BH",
                "priority": "stage 3 blocker"
            },
            {
                "id": "2.8", 
                "description": "Reboot agent 1 and check stability",
                "details": "• Reboot the agent 1 & check if agent 1 connect to controller and stable\n• Monitor for 5 mins and see if BH connection is stable",
                "priority": "stage 3 blocker"
            },
            {
                "id": "2.9", 
                "description": "Repeat test cases 4,5,6",
                "details": "Repeat test cases 2.4, 2.5, 2.6",
                "priority": "stage 3 blocker"
            },
            {
                "id": "2.10", 
                "description": "Verify reboot resilience and automatic connection",
                "details": "Reboot the device and Agent1 should automatically connect to gateway & client connectivity and internet browsing should happen & no kernel crash/EM agent/onewifi crash",
                "priority": "stage 3 blocker"
            },
            {
                "id": "2.11", 
                "description": "Power cycle gateway and verify agent reconnection",
                "details": "Power off the gateway and wait for gateway to up and running and check if Agent 1 onboards to controller via BH without any issues",
                "priority": "stage 3 blocker"
            },
            {
                "id": "2.12", 
                "description": "Repeat test cases 4,5,6 again",
                "details": "Repeat test cases 2.4, 2.5, 2.6 again",
                "priority": "stage 3 blocker"
            },
            {
                "id": "2.13", 
                "description": "Change SSID in gateway and verify propagation",
                "details": "Change ssid in gateway using cli and wait for 2 to 3 mins and check if same is reflected in agent 1. If it's reflected, repeat test cases 4,5,6",
                "priority": "stage 3 blocker"
            }
            ],
        3: [
            # Add test cases for Stage 3
            {
                "id": "3.0",
                "description": "Boot device, configure for remote agent 2",
                "details": "• Boot the device and wait until all radios are up and running\n• Remove dnsmasq from /usr/bin\n• ifconfig erouter0 down\n• Do mesh configuration in nvram ---------- make sure you make colocated mode 0\n• Remove wifi db /opt/secure/wifi/* (till Agent profile is up and running by Akhil P)\n• Need to have updated one_wifi_prestart.sh\n• Need to have aishwarya Mac address changes\n• Restart onewifi",
                "priority": "stage 4 blocker"
            },
            {
                "id": "3.1",
                "description": "Make sure onewifi is up and running",
                "details": "Verify onewifi service is running correctly",
                "priority": "stage 4 blocker"
            },
            {
                "id": "3.2",
                "description": "Validate agent 2 communication with agent 1",
                "details": "Validate: \n1. iw dev wifi0.1 info in Agent 2\n2. iw dev wifi0.1.sta1 info in Agent 1\n3. iw dev wifi0.1.sta1 station dump in Agent 1\n• Agent 2 device should communicate with Agent 1 all the time",
                "priority": "stage 4 blocker"
            },
            {
                "id": "3.3",
                "description": "Bringup EasyMesh agent and verify connectivity",
                "details": "• Bringup Easymesh agent\n• Check iw dev\n• Agent 2 should show all ssid details for all radios which is common across gateway/agent1 and agent2\n• Set brlan0 with static ip\n• Perform ping test/wget http://10.0.0.1",
                "priority": "stage 4 blocker"
            },
            {
                "id": "3.4",
                "description": "Test 2.4GHz connectivity in daisy chain configuration",
                "details": "• Disable all private VAP's in gateway side & Agent 1 & disable 5Ghz and 6Ghz radio in agent 2 device\n• Connect Mobile phone to private ssid's (Try with 2Ghz)\n• Connection should be successful\n• Internet browsing should work\n• No crash of agent/Onewifi should happen\n• No kernel panic",
                "priority": "stage 4 blocker"
            },
            {
                "id": "3.5",
                "description": "Test 5GHz connectivity in daisy chain configuration",
                "details": "• Disable all private VAP's in gateway side & Agent 1 & disable 2.4Ghz and 6Ghz radio in agent 2 device\n• Connect Mobile phone to private ssid's (Try with 5Ghz)\n• Connection should be successful\n• Internet browsing should work\n• No crash of agent/Onewifi should happen\n• No kernel panic",
                "priority": "stage 4 blocker"
            },
            {
                "id": "3.6",
                "description": "Test 6GHz connectivity in daisy chain configuration",
                "details": "• Disable all private VAP's in gateway side & Agent 1 & disable 2.4Ghz and 5Ghz radio in agent 2 device\n• Connect Mobile phone to private ssid's (Try with 6Ghz)\n• Connection should be successful\n• Internet browsing should work\n• No crash of agent/Onewifi should happen\n• No kernel panic",
                "priority": "stage 4 blocker"
            },
            {
                "id": "3.7",
                "description": "Idle device connectivity check",
                "details": "Leave the device idle for 5 mins & check Agent 2 connectivity with Agent 1. There should not be any disconnection over BH",
                "priority": "stage 4 blocker"
            },
            {
                "id": "3.8",
                "description": "Reboot agent 2 and check stability",
                "details": "• Reboot the agent 2 & check if agent 2 connect to Agent 1 and stable\n• Monitor for 5 mins and see if BH connection is stable",
                "priority": "stage 4 blocker"
            },
            {
                "id": "3.9",
                "description": "Repeat test cases 4,5,6",
                "details": "Repeat test cases 3.4, 3.5, 3.6",
                "priority": "stage 4 blocker"
            },
            {
                "id": "3.10",
                "description": "Verify reboot resilience and automatic connection",
                "details": "Reboot the device and Agent2 should automatically connect to Agent 1 & client connectivity and internet browsing should happen & no kernel crash/EM agent/onewifi crash",
                "priority": "stage 4 blocker"
            },
            {
                "id": "3.11",
                "description": "Power cycle agent 1 and verify agent 2 reconnection",
                "details": "Power off the agent 1 and wait for agent 1 to up & running and let it onboard to gateway and check if Agent 2 onboards to Agent 1 via BH without any issues",
                "priority": "stage 4 blocker"
            },
            {
                "id": "3.12",
                "description": "Repeat test cases 4,5,6 again",
                "details": "Repeat test cases 3.4, 3.5, 3.6 again",
                "priority": "stage 4 blocker"
            },
            {
                "id": "3.13",
                "description": "Change SSID in gateway and verify propagation to agent 2",
                "details": "Change ssid in gateway using cli and wait for 2 to 3 mins and check if same is reflected in agent 2. If it's reflected, repeat test cases 4,5,6",
                "priority": "stage 4 blocker"
            }
        ],
        4: [
            # Add test cases for Stage 4
             {
                "id": "4.0",
                "description": "Boot device, configure for remote agent",
                "details": "• Boot the device and wait until all radios are up and running\n• Remove dnsmasq from /usr/bin\n• ifconfig erouter0 down\n• Do mesh configuration in nvram ----- make sure you make colocated mode 0\n• Remove wifi db /opt/secure/wifi/* (till Agent profile is up and running by Akhil P)\n• Need to have updated one_wifi_prestart.sh\n• Need to have aishwarya Mac address changes\n• Restart onewifi",
                "priority": "stage 5 blocker"
            },
            {
                "id": "4.1",
                "description": "Make sure onewifi is up and running",
                "details": "Verify onewifi service is running correctly",
                "priority": "stage 5 blocker"
            },
            {
                "id": "4.2",
                "description": "Validate agent communication with gateway",
                "details": "Validate:\n1. iw dev wifi1.1 info in Extender 1\n2. iw dev wifi1.1.sta1 info in ctrl\n3. iw dev wifi1.1.sta1 station dump in ctrl\n• Agent 3 device should communicate with gateway all the time",
                "priority": "stage 5 blocker"
            },
            {
                "id": "4.3",
                "description": "Bringup EasyMesh agent and verify connectivity",
                "details": "• Bringup Easymesh agent\n• Check iw dev\n  • Agent 1 should show all ssid details for all radios\n• Set brlan0 with static ip\n• Perform ping test/wget http://10.0.0.1",
                "priority": "stage 5 blocker"
            },
            {
                "id": "4.4",
                "description": "Test 2.4GHz connectivity with gateway private VAPs disabled",
                "details": "• Disable all private VAP's in gateway side & disable 5Ghz and 6Ghz radio in agent 3 device\n• Connect Mobile phone to private ssid's (Try with 2Ghz)\n  • Connection should be successful\n  • Internet browsing should work\n  • No crash of agent/Onewifi should happen\n  • No kernel panic",
                "priority": "stage 5 blocker"
            },
            {
                "id": "4.5",
                "description": "Test 5GHz connectivity with gateway private VAPs disabled",
                "details": "• Disable all private VAP's in gateway side & disable 2.4Ghz and 6Ghz radio in agent 3 device\n• Connect Mobile phone to private ssid's (Try with 5Ghz)\n  • Connection should be successful\n  • Internet browsing should work\n  • No crash of agent/Onewifi should happen\n  • No kernel panic",
                "priority": "stage 5 blocker"
            },
            {
                "id": "4.6",
                "description": "Test 6GHz connectivity with gateway private VAPs disabled",
                "details": "• Disable all private VAP's in gateway side & disable 2.4Ghz and 5Ghz radio in agent 3 device\n• Connect Mobile phone to private ssid's (Try with 6Ghz)\n  • Connection should be successful\n  • Internet browsing should work\n  • No crash of agent/Onewifi should happen\n  • No kernel panic",
                "priority": "stage 5 blocker"
            },
            {
                "id": "4.7",
                "description": "Idle device connectivity check",
                "details": "Leave the device idle for 5 mins & check Agent 3 connectivity with gateway. There should not be any disconnection over BH",
                "priority": "stage 5 blocker"
            },
            {
                "id": "4.8",
                "description": "Reboot agent 1 and check stability",
                "details": "• Reboot the agent 1 & check if agent 3 connect to controller and stable\n• Monitor for 5 mins and see if BH connection is stable",
                "priority": "stage 5 blocker"
            },
            {
                "id": "4.9",
                "description": "Repeat test cases 4,5,6",
                "details": "Repeat test cases 2.4, 2.5, 2.6",
                "priority": "stage 5 blocker"
            },
            {
                "id": "4.10",
                "description": "Verify reboot resilience and automatic connection",
                "details": "Reboot the device and Agent3 should automatically connect to gateway & client connectivity and internet browsing should happen & no kernel crash/EM agent/onewifi crash",
                "priority": "stage 5 blocker"
            },
            {
                "id": "4.11",
                "description": "Power cycle gateway and verify agent reconnection",
                "details": "Power off the gateway and wait for gateway to up and running and check if Agent 3 onboards to controller via BH without any issues",
                "priority": "stage 5 blocker"
            },
            {
                "id": "4.12",
                "description": "Repeat test cases 4,5,6 again",
                "details": "Repeat test cases 2.4, 2.5, 2.6 again",
                "priority": "stage 5 blocker"
            },
            {
                "id": "4.13",
                "description": "Change SSID in gateway and verify propagation",
                "details": "Change ssid in gateway using cli and wait for 2 to 3 mins and check if same is reflected in agent 3. If it's reflected, repeat test cases 4,5,6",
                "priority": "stage 5 blocker"
            }
        ],
        5: [
            # Add test cases for Stage 5
            {
                "id": "5.1",
                "description": "Tag code base",
                "details": "Perform code tagging for the validated build",
                "priority": "Required"
            },
            {
                "id": "5.2",
                "description": "Banana pi Base build",
                "details": "Create Banana pi Base build",
                "priority": "Required"
            },
            {
                "id": "5.3",
                "description": "Unified-wifi-mesh",
                "details": "Verify unified-wifi-mesh components",
                "priority": "Required"
            },
            {
                "id": "5.4",
                "description": "Onewifi",
                "details": "Verify Onewifi component",
                "priority": "Required"
            },
            {
                "id": "5.5",
                "description": "rdk-wifi-hal",
                "details": "Verify rdk-wifi-hal component",
                "priority": "Required"
            },
            {
                "id": "5.6",
                "description": "rdk-wifi-libhostap",
                "details": "Verify rdk-wifi-libhostap component",
                "priority": "Required"
            },
            {
                "id": "5.7",
                "description": "halinterface",
                "details": "Verify halinterface component",
                "priority": "Required"
            }
        ]
    }
    
    return stages, test_cases

# Database helpers
def get_db_connection(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path):
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS project_info (
            name TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS test_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stage_id INTEGER,
            test_id TEXT,
            status TEXT,
            notes TEXT,
            tester TEXT,
            timestamp TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/test-structure', methods=['GET'])
def get_test_structure():
    stages, test_cases = load_test_structure()
    return jsonify({'stages': stages, 'test_cases': test_cases})

@app.route('/api/create-session', methods=['POST'])
def create_session():
    data = request.json
    project_name = data.get('project_name', '')
    tester_name = data.get('tester_name', '')
    
    # Create temporary DB file
    db_path = os.path.join(tempfile.gettempdir(), f"mesh_test_{datetime.now().strftime('%Y%m%d%H%M%S')}.db")
    init_db(db_path)
    
    # Initialize project info
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO project_info (name, value) VALUES (?, ?)", 
                  ("project_name", project_name))
    cursor.execute("INSERT INTO project_info (name, value) VALUES (?, ?)", 
                  ("tester_name", tester_name))
    cursor.execute("INSERT INTO project_info (name, value) VALUES (?, ?)", 
                  ("test_date", datetime.now().strftime("%Y-%m-%d")))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'db_path': db_path})

@app.route('/api/save-test', methods=['POST'])
def save_test():
    data = request.json
    db_path = data.get('db_path')
    stage_id = data.get('stage_id')
    test_id = data.get('test_id')
    status = data.get('status')
    notes = data.get('notes')
    tester = data.get('tester')
    
    if not all([db_path, stage_id, test_id, status]):
        return jsonify({'success': False, 'error': 'Missing required fields'})
    
    try:
        conn = get_db_connection(db_path)
        cursor = conn.cursor()
        
        # Check if record exists
        cursor.execute(
            "SELECT id FROM test_results WHERE stage_id = ? AND test_id = ?",
            (stage_id, test_id)
        )
        existing_id = cursor.fetchone()
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if existing_id:
            # Update existing record
            cursor.execute(
                "UPDATE test_results SET status = ?, notes = ?, tester = ?, timestamp = ? "
                "WHERE stage_id = ? AND test_id = ?",
                (status, notes, tester, timestamp, stage_id, test_id)
            )
        else:
            # Insert new record
            cursor.execute(
                "INSERT INTO test_results (stage_id, test_id, status, notes, tester, timestamp) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (stage_id, test_id, status, notes, tester, timestamp)
            )
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/upload-db', methods=['POST'])
def upload_db():
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file part'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No selected file'})
    
    if file:
        # Save uploaded file to temporary location
        filename = os.path.join(tempfile.gettempdir(), f"uploaded_db_{datetime.now().strftime('%Y%m%d%H%M%S')}.db")
        file.save(filename)
        
        # Verify it's a valid SQLite database
        try:
            conn = sqlite3.connect(filename)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            conn.close()
            
            if not tables or ('project_info',) not in tables or ('test_results',) not in tables:
                os.remove(filename)
                return jsonify({'success': False, 'error': 'Invalid database file format'})
            
            return jsonify({'success': True, 'db_path': filename})
        except Exception as e:
            # Clean up file if it's not a valid database
            if os.path.exists(filename):
                os.remove(filename)
            return jsonify({'success': False, 'error': str(e)})

@app.route('/api/load-results', methods=['POST'])
def load_results():
    data = request.json
    db_path = data.get('db_path')
    
    if not db_path or not os.path.exists(db_path):
        return jsonify({'success': False, 'error': 'Invalid database path'})
    
    try:
        conn = get_db_connection(db_path)
        
        # Load project info
        project_info = {}
        for row in conn.execute("SELECT name, value FROM project_info"):
            project_info[row['name']] = row['value']
        
        # Load test results
        results = {}
        for row in conn.execute("SELECT stage_id, test_id, status, notes, tester, timestamp FROM test_results"):
            stage_id = row['stage_id']
            test_id = row['test_id']
            
            if stage_id not in results:
                results[stage_id] = {}
            
            results[stage_id][test_id] = {
                'status': row['status'],
                'notes': row['notes'],
                'tester': row['tester'],
                'timestamp': row['timestamp']
            }
        
        conn.close()
        
        return jsonify({
            'success': True,
            'project_info': project_info,
            'test_results': results
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/export-report', methods=['POST'])
def export_report():
    data = request.json
    db_path = data.get('db_path')
    format_type = data.get('format', 'txt')  # txt or csv
    
    if not db_path or not os.path.exists(db_path):
        return jsonify({'success': False, 'error': 'Invalid database path'})
    
    try:
        conn = get_db_connection(db_path)
        stages, test_cases = load_test_structure()
        
        # Get project info
        project_info = {}
        for row in conn.execute("SELECT name, value FROM project_info"):
            project_info[row['name']] = row['value']
        
        # Get test results
        test_results = {}
        for row in conn.execute("SELECT stage_id, test_id, status, notes, tester, timestamp FROM test_results"):
            stage_id = row['stage_id']
            test_id = row['test_id']
            
            if stage_id not in test_results:
                test_results[stage_id] = {}
            
            test_results[stage_id][test_id] = {
                'status': row['status'],
                'notes': row['notes'],
                'tester': row['tester'],
                'timestamp': row['timestamp']
            }
        
        conn.close()
        
        # Create report file
        report_path = os.path.join(tempfile.gettempdir(), 
                                  f"mesh_report_{datetime.now().strftime('%Y%m%d%H%M%S')}.{format_type}")
        
        if format_type == 'csv':
            # Generate CSV report
            import csv
            with open(report_path, 'w', newline='') as f:
                writer = csv.writer(f)
                
                # Write header
                writer.writerow(["Stage ID", "Test ID", "Description", "Priority", "Status", "Notes", 
                                "Tester", "Timestamp"])
                
                # Write data
                for stage_id in sorted([int(s) for s in test_results.keys()]):
                    for test_id in sorted(test_results[str(stage_id)].keys(), key=lambda x: float(x)):
                        test_desc = ""
                        test_priority = ""
                        for tc in test_cases.get(stage_id, []):
                            if tc["id"] == test_id:
                                test_desc = tc["description"]
                                test_priority = tc.get("priority", "")
                                break
                        
                        result = test_results[str(stage_id)][test_id]
                        writer.writerow([
                            stage_id,
                            test_id,
                            test_desc,
                            test_priority,
                            result["status"],
                            result["notes"],
                            result["tester"],
                            result["timestamp"]
                        ])
        else:
            # Generate text report
            with open(report_path, 'w') as f:
                # Write header
                f.write("=" * 80 + "\n")
                f.write(f"MESH NETWORK VALIDATION TEST REPORT\n")
                f.write("=" * 80 + "\n\n")
                
                f.write(f"Project: {project_info.get('project_name', 'N/A')}\n")
                f.write(f"Test Date: {project_info.get('test_date', 'N/A')}\n")
                f.write(f"Tester: {project_info.get('tester_name', 'N/A')}\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                # Write summary for each stage
                for stage in stages:
                    stage_id = stage["id"]
                    f.write("-" * 80 + "\n")
                    f.write(f"STAGE {stage_id}: {stage['name']}\n")
                    f.write("-" * 80 + "\n\n")
                    
                    if str(stage_id) in test_results:
                        stage_results = test_results[str(stage_id)]
                        # Count status totals
                        total = len(stage_results)
                        passed = sum(1 for r in stage_results.values() if r["status"] == "Passed")
                        failed = sum(1 for r in stage_results.values() if r["status"] == "Failed")
                        blocked = sum(1 for r in stage_results.values() if r["status"] == "Blocked")
                        not_started = sum(1 for r in stage_results.values() if r["status"] == "Not Started")
                        
                        # Write stage summary
                        f.write(f"Summary:\n")
                        f.write(f"  Total Tests: {total}\n")
                        if total > 0:
                            f.write(f"  Passed: {passed} ({passed/total*100:.1f}%)\n")
                            f.write(f"  Failed: {failed} ({failed/total*100:.1f}%)\n")
                            f.write(f"  Blocked: {blocked} ({blocked/total*100:.1f}%)\n")
                            f.write(f"  Not Started: {not_started} ({not_started/total*100:.1f}%)\n\n")
                        
                        # Determine stage status
                        stage_status = "Not Started"
                        if total > 0:
                            if failed > 0:
                                stage_status = "Failed"
                            elif blocked > 0:
                                stage_status = "Blocked"
                            elif not_started > 0:
                                stage_status = "In Progress"
                            else:
                                stage_status = "Passed"
                        
                        f.write(f"Stage Status: {stage_status}\n\n")
                        
                        # Write detailed test results
                        f.write("Detailed Test Results:\n")
                        f.write("  {:<10} {:<50} {:<15} {:<20}\n".format(
                            "Test ID", "Description", "Status", "Tester"))
                        f.write("  " + "-" * 95 + "\n")
                        
                        for test_id in sorted(stage_results.keys(), key=lambda x: float(x)):
                            result = stage_results[test_id]
                            test_desc = ""
                            for tc in test_cases.get(stage_id, []):
                                if tc["id"] == test_id:
                                    test_desc = tc["description"]
                                    break
                            
                            # Truncate description if too long
                            if len(test_desc) > 45:
                                test_desc = test_desc[:42] + "..."
                            
                            f.write("  {:<10} {:<50} {:<15} {:<20}\n".format(
                                test_id, test_desc, result["status"], result["tester"]))
                        
                        # Add test case details with notes for each test
                        f.write("\n  Detailed Test Descriptions:\n")
                        f.write("  " + "-" * 95 + "\n")
                        
                        for test_id in sorted(stage_results.keys(), key=lambda x: float(x)):
                            result = stage_results[test_id]
                            test_details = ""
                            test_priority = ""
                            
                            for tc in test_cases.get(stage_id, []):
                                if tc["id"] == test_id:
                                    test_details = tc.get("details", "")
                                    test_priority = tc.get("priority", "")
                                    break
                            
                            f.write(f"  Test ID: {test_id}\n")
                            f.write(f"  Status: {result['status']}\n")
                            f.write(f"  Priority: {test_priority}\n")
                            if test_details:
                                f.write(f"  Details:\n")
                                for line in test_details.split("\n"):
                                    f.write(f"    {line}\n")
                            if result["notes"]:
                                f.write(f"  Notes: {result['notes']}\n")
                            f.write(f"  Tester: {result['tester']}\n")
                            f.write(f"  Timestamp: {result['timestamp']}\n")
                            f.write("  " + "-" * 95 + "\n\n")
                    
                    f.write("\n\n")
                
                # Write overall summary
                f.write("=" * 80 + "\n")
                f.write("OVERALL SUMMARY\n")
                f.write("=" * 80 + "\n\n")
                
                total_tests = sum(len(tests) for tests in test_results.values())
                total_passed = sum(sum(1 for r in tests.values() if r["status"] == "Passed") 
                                 for tests in test_results.values())
                total_failed = sum(sum(1 for r in tests.values() if r["status"] == "Failed") 
                                 for tests in test_results.values())
                total_blocked = sum(sum(1 for r in tests.values() if r["status"] == "Blocked") 
                                  for tests in test_results.values())
                total_not_started = sum(sum(1 for r in tests.values() if r["status"] == "Not Started") 
                                     for tests in test_results.values())
                
                f.write(f"Total Tests: {total_tests}\n")
                if total_tests > 0:
                    f.write(f"Passed: {total_passed} ({total_passed/total_tests*100:.1f}%)\n")
                    f.write(f"Failed: {total_failed} ({total_failed/total_tests*100:.1f}%)\n")
                    f.write(f"Blocked: {total_blocked} ({total_blocked/total_tests*100:.1f}%)\n")
                    f.write(f"Not Started: {total_not_started} ({total_not_started/total_tests*100:.1f}%)\n\n")
                
                overall_status = "Not Started"
                if total_tests > 0:
                    if total_failed > 0:
                        overall_status = "Failed"
                    elif total_blocked > 0:
                        overall_status = "Blocked"
                    elif total_not_started > 0:
                        overall_status = "In Progress"
                    else:
                        overall_status = "Passed"
                
                f.write(f"Overall Status: {overall_status}\n\n")
                
                # End of report
                f.write("=" * 80 + "\n")
                f.write("END OF REPORT\n")
                f.write("=" * 80 + "\n")
        
        return jsonify({
            'success': True,
            'report_path': os.path.basename(report_path)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/download-report/<path:filename>')
def download_report(filename):
    directory = tempfile.gettempdir()
    return send_file(os.path.join(directory, os.path.basename(filename)), as_attachment=True)

@app.route('/api/save-db', methods=['POST'])
def save_db():
    data = request.json
    db_path = data.get('db_path')
    
    if not db_path or not os.path.exists(db_path):
        return jsonify({'success': False, 'error': 'Invalid database path'})
    
    # Generate a download name
    download_name = f"mesh_validation_{datetime.now().strftime('%Y%m%d%H%M%S')}.db"
    
    # Copy the file to a new location
    download_path = os.path.join(tempfile.gettempdir(), download_name)
    
    try:
        import shutil
        shutil.copy2(db_path, download_path)
        
        return jsonify({
            'success': True,
            'download_path': download_name
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    # Run the app on the specified IP and port
    app.run(host='192.168.64.2', port=8755, debug=True)
