/**
 * PLC Data Simulator
 * Phase 32.1 - Multi-System Integration
 *
 * Generates realistic PLC data for testing WebSocket streaming
 */

import { EventEmitter } from 'events';
import { ControlLoopData, PLCDataPoint } from './types';

export class PLCDataSimulator extends EventEmitter {
  private timers: NodeJS.Timeout[] = [];
  private isRunning: boolean = false;

  // Simulated PLC tags
  private readonly plcTags = [
    { name: 'TANK_01_LEVEL', unit: '%', min: 0, max: 100 },
    { name: 'TANK_01_TEMP', unit: '°C', min: 20, max: 80 },
    { name: 'PUMP_01_SPEED', unit: 'RPM', min: 0, max: 3600 },
    { name: 'VALVE_01_POSITION', unit: '%', min: 0, max: 100 },
    { name: 'FLOW_01_RATE', unit: 'L/min', min: 0, max: 500 },
  ];

  // Simulated control loops
  private readonly controlLoops = [
    { id: 'LOOP_001', name: 'Tank Level Control' },
    { id: 'LOOP_002', name: 'Temperature Control' },
    { id: 'LOOP_003', name: 'Flow Control' },
  ];

  public start(): void {
    if (this.isRunning) return;

    this.isRunning = true;
    console.log('PLC data simulator started');

    // Generate PLC data every 100ms
    const plcTimer = setInterval(() => {
      this.generatePLCData();
    }, 100);
    this.timers.push(plcTimer);

    // Generate control loop data every 1000ms
    const loopTimer = setInterval(() => {
      this.generateControlLoopData();
    }, 1000);
    this.timers.push(loopTimer);
  }

  public stop(): void {
    this.isRunning = false;

    // Clear all timers
    this.timers.forEach(timer => clearInterval(timer));
    this.timers = [];

    console.log('PLC data simulator stopped');
  }

  private generatePLCData(): void {
    const tag = this.plcTags[Math.floor(Math.random() * this.plcTags.length)];

    // Generate realistic value with some noise
    const range = tag.max - tag.min;
    const baseValue = tag.min + range * 0.5 + Math.sin(Date.now() / 10000) * range * 0.3;
    const noise = (Math.random() - 0.5) * range * 0.05;
    const value = Math.max(tag.min, Math.min(tag.max, baseValue + noise));

    const dataPoint: PLCDataPoint = {
      timestamp: Date.now(),
      tagName: tag.name,
      value: parseFloat(value.toFixed(2)),
      quality: Math.random() > 0.95 ? 'uncertain' : 'good',
      unit: tag.unit,
    };

    this.emit('plc-data', dataPoint);
  }

  private generateControlLoopData(): void {
    const loop = this.controlLoops[Math.floor(Math.random() * this.controlLoops.length)];

    // Simulate control loop behavior
    const setpoint = 50 + Math.sin(Date.now() / 30000) * 20;
    const processVariable = setpoint + (Math.random() - 0.5) * 5;
    const error = setpoint - processVariable;
    const controlVariable = 50 + error * 2; // Simple P control

    const loopData: ControlLoopData = {
      loopId: loop.id,
      name: loop.name,
      setpoint: parseFloat(setpoint.toFixed(2)),
      processVariable: parseFloat(processVariable.toFixed(2)),
      controlVariable: parseFloat(controlVariable.toFixed(2)),
      mode: Math.random() > 0.9 ? 'manual' : 'auto',
      status: Math.random() > 0.95 ? 'fault' : 'running',
      performance: {
        overshoot: parseFloat((Math.random() * 10).toFixed(2)),
        settlingTime: parseFloat((10 + Math.random() * 20).toFixed(2)),
        steadyStateError: parseFloat((Math.random() * 2).toFixed(2)),
      },
    };

    this.emit('control-loop', loopData);
  }
}
