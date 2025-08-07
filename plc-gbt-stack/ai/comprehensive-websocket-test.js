#!/usr/bin/env node

const WebSocket = require('ws');

async function comprehensiveWebSocketTest() {
  console.log('🔌 COMPREHENSIVE WEBSOCKET DATA STRUCTURE TEST');
  console.log('===============================================');

  // Test 1: Basic Backend Health
  console.log('\n📍 Test 1: Backend Health Check');
  try {
    const result = await fetch('http://localhost:8000/api/v1/health');
    const data = await result.json();
    if (result.status === 200 && data.status === 'healthy') {
      console.log('✅ PASS: Backend health check');
    } else {
      console.log('❌ FAIL: Backend health issue');
      return false;
    }
  } catch (error) {
    console.log(`❌ FAIL: Backend health error - ${error.message}`);
    return false;
  }

  // Test 2: WebSocket Connection and Data Structure
  console.log('\n🔌 Test 2: WebSocket Connection & Data Structure');
  return new Promise(resolve => {
    const ws = new WebSocket('ws://localhost:8000/ws');
    let testsPassed = 0;
    let totalTests = 3;
    let timeout;

    ws.on('open', () => {
      console.log('✅ WebSocket connection established');
      testsPassed++;

      // Set timeout to close connection after receiving data
      timeout = setTimeout(() => {
        ws.close();
        if (testsPassed >= totalTests) {
          console.log('\n📊 WEBSOCKET TEST RESULTS');
          console.log('==========================');
          console.log(`✅ Connection: PASS`);
          console.log(`✅ Data Structure: PASS`);
          console.log(`✅ Message Format: PASS`);
          console.log(`🎯 Overall Score: 100%`);
          console.log('✅ WebSocket data structure validation PASSED');
          resolve(true);
        } else {
          console.log('\n❌ WEBSOCKET TEST FAILED');
          console.log(`❌ Only ${testsPassed}/${totalTests} tests passed`);
          resolve(false);
        }
      }, 35000); // Wait for at least one update cycle
    });

    ws.on('message', data => {
      try {
        const message = JSON.parse(data.toString());
        console.log('📡 Received WebSocket message:', JSON.stringify(message, null, 2));

        // Validate message structure
        if (message.type === 'connection_established') {
          console.log('✅ Connection confirmation received');
          testsPassed++;
        } else if (message.type === 'control_loop_update') {
          console.log('📊 Validating control loop update structure...');

          // Check required fields according to frontend expectations
          const hasCorrectStructure =
            message.data &&
            message.data.loop_id &&
            message.data.updates &&
            typeof message.data.updates.process_value === 'number' &&
            typeof message.data.updates.control_output === 'number' &&
            typeof message.data.updates.status === 'string';

          if (hasCorrectStructure) {
            console.log('✅ PASS: WebSocket data structure matches frontend expectations');
            console.log(`   Loop ID: ${message.data.loop_id}`);
            console.log(`   Process Value: ${message.data.updates.process_value}`);
            console.log(`   Control Output: ${message.data.updates.control_output}`);
            console.log(`   Status: ${message.data.updates.status}`);
            testsPassed++;
          } else {
            console.log('❌ FAIL: WebSocket data structure mismatch');
            console.log(
              '   Expected: { data: { loop_id, updates: { process_value, control_output, status } } }'
            );
            console.log('   Received:', JSON.stringify(message.data, null, 2));
          }
        }
      } catch (error) {
        console.log(`❌ FAIL: WebSocket message parsing error - ${error.message}`);
      }
    });

    ws.on('close', () => {
      console.log('🔌 WebSocket connection closed');
      if (timeout) clearTimeout(timeout);
      if (testsPassed >= totalTests) {
        resolve(true);
      } else {
        console.log(`❌ WebSocket test incomplete: ${testsPassed}/${totalTests} tests passed`);
        resolve(false);
      }
    });

    ws.on('error', error => {
      console.log(`❌ FAIL: WebSocket connection error - ${error.message}`);
      if (timeout) clearTimeout(timeout);
      resolve(false);
    });
  });
}

// Add fetch polyfill for Node.js if needed
if (typeof fetch === 'undefined') {
  global.fetch = require('node-fetch');
}

// Run the comprehensive test
comprehensiveWebSocketTest()
  .then(success => {
    if (success) {
      console.log('\n🎉 COMPREHENSIVE WEBSOCKET TEST: PASSED');
      console.log('✅ Ready for Phase 2: User Interactive Testing');
      process.exit(0);
    } else {
      console.log('\n❌ COMPREHENSIVE WEBSOCKET TEST: FAILED');
      console.log('🔧 Automated testing must pass before user validation');
      process.exit(1);
    }
  })
  .catch(error => {
    console.error('❌ Test execution failed:', error);
    process.exit(1);
  });
