#!/usr/bin/env node

const http = require('http');

async function quickBackendTest() {
  console.log('🤖 AUTOMATED BACKEND TESTING (Corrected)');
  console.log('=========================================');

  // Test 1: Health endpoint (corrected path)
  console.log('\n📍 Test 1: Health Endpoint (corrected path)');
  try {
    const result = await fetch('http://localhost:8000/api/v1/health');
    const data = await result.json();
    console.log(`✅ Health check: ${result.status} - ${data.status}`);

    if (result.status === 200 && data.status === 'healthy') {
      console.log('✅ PASS: Health endpoint working correctly');
    } else {
      console.log('❌ FAIL: Health endpoint issue');
      return false;
    }
  } catch (error) {
    console.log(`❌ FAIL: Health endpoint error - ${error.message}`);
    return false;
  }

  // Test 2: Control Loop Instances endpoint
  console.log('\n📊 Test 2: Control Loop Instances');
  try {
    const result = await fetch('http://localhost:8000/api/v1/instances');
    const data = await result.json();
    console.log(`✅ Instances: ${result.status} - success: ${data.success}`);

    if (result.status === 200 && data.success && data.data?.total > 0) {
      console.log(`✅ PASS: Found ${data.data.total} control loop instances`);
    } else {
      console.log('❌ FAIL: Control loop instances issue');
      return false;
    }
  } catch (error) {
    console.log(`❌ FAIL: Instances endpoint error - ${error.message}`);
    return false;
  }

  console.log('\n📊 AUTOMATED TEST RESULTS');
  console.log('==========================');
  console.log('✅ Backend Health: PASS');
  console.log('✅ API Endpoints: PASS');
  console.log('🎯 Overall Score: 100%');
  console.log('✅ Ready for Phase 2: User Interactive Testing');

  return true;
}

// Add fetch polyfill for Node.js if needed
if (typeof fetch === 'undefined') {
  global.fetch = require('node-fetch');
}

// Run the test
quickBackendTest()
  .then(success => {
    process.exit(success ? 0 : 1);
  })
  .catch(error => {
    console.error('❌ Test execution failed:', error);
    process.exit(1);
  });
