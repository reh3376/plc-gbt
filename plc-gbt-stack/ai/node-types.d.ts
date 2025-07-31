/// <reference types="node" />

// Global Node.js type declarations for VS Code Language Server compatibility
declare global {
  var process: NodeJS.Process;
  var Buffer: BufferConstructor;
  var __dirname: string;
  var __filename: string;
  var console: Console;
  
  function setTimeout(callback: (...args: any[]) => void, ms?: number, ...args: any[]): NodeJS.Timeout;
  function clearTimeout(timeoutId: NodeJS.Timeout): void;
  function setInterval(callback: (...args: any[]) => void, ms?: number, ...args: any[]): NodeJS.Timeout;
  function clearInterval(intervalId: NodeJS.Timeout): void;
  function setImmediate(callback: (...args: any[]) => void, ...args: any[]): NodeJS.Immediate;
  function clearImmediate(immediateId: NodeJS.Immediate): void;
  
  var require: NodeRequire;
  var module: NodeModule;
  var exports: any;
}

// CommonJS module system types
declare var require: NodeRequire;
declare var module: NodeModule;
declare var exports: any;

// Node.js process global
declare var process: NodeJS.Process;

// Export empty to make this a module
export {};