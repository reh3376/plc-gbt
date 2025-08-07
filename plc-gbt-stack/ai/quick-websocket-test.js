#!/usr/bin/env node

const WebSocket = require('ws');

async function quickWebSocketTest() {
  console.log('🚀 QUICK WEBSOCKET DATA VALIDATION');
  console.log('===================================');

  return new Promise(resolve => {
    const ws = new WebSocket('ws://localhost:8000/ws');
    let receivedControlUpdate = false;
    let validDataStructure = false;

    // Set timeout
    const timeout = setTimeout(() => {
      ws.close();
      if (receivedControlUpdate && validDataStructure) {
        console.log('\n✅ WEBSOCKET DATA STRUCTURE: VALIDATED');
        console.log('🎯 Score: 100% - Ready for user testing');
        resolve(true);
      } else {
        console.log('\n❌ WEBSOCKET DATA STRUCTURE: FAILED');
        resolve(false);
      }
    }, 32000); // Wait for one update cycle

    ws.on('open', () => {
      console.log('✅ WebSocket connected');
    });

    ws.on('message', data => {
      try {
        const message = JSON.parse(data.toString());

        if (message.type === 'control_loop_update') {
          console.log('📊 Control loop update received!');
          receivedControlUpdate = true;

          // Validate NEW data structure format
          if (
            message.data &&
            message.data.loop_id &&
            message.data.updates &&
            typeof message.data.updates.process_value === 'number' &&
            typeof message.data.updates.control_output === 'number' &&
            message.data.updates.status
          ) {
            console.log('✅ Data structure VALID:');
            console.log(`   Loop: ${message.data.loop_id}`);
            console.log(`   Process Value: ${message.data.updates.process_value}`);
            console.log(`   Control Output: ${message.data.updates.control_output}`);
            console.log(`   Status: ${message.data.updates.status}`);
            validDataStructure = true;

            // Success - close early
            clearTimeout(timeout);
            ws.close();
          } else {
            console.log('❌ Data structure INVALID');
            console.log(
              'Expected: { data: { loop_id, updates: { process_value, control_output, status } } }'
            );
            console.log('Received:', JSON.stringify(message.data, null, 2));
          }
        }
      } catch (error) {
        console.log(`❌ Message parsing error: ${error.message}`);
      }
    });

    ws.on('close', () => {
      clearTimeout(timeout);
      resolve(receivedControlUpdate && validDataStructure);
    });

    ws.on('error', error => {
      console.log(`❌ WebSocket error: ${error.message}`);
      clearTimeout(timeout);
      resolve(false);
    });
  });
}

// Run test
quickWebSocketTest()
  .then(success => {
    process.exit(success ? 0 : 1);
  })
  .catch(error => {
    console.error('Test failed:', error);
    process.exit(1);
  });
