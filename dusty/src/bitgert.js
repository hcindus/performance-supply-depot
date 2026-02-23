/**
 * Dusty Bitgert/BRISE Integration
 * ============================================
 * EVM-compatible chain with near-zero gas fees
 * 
 * Network Info:
 * - Chain ID: 32520
 * - RPC: https://rpc.icecreamswap.com/32520
 * - Block Explorer: https://brisescan.com
 * 
 * Version: 1.0.0
 * Updated: 2026-02-22
 */

const { ethers } = require('ethers');
const fs = require('fs');
const path = require('path');

// Load configuration
let config;
try {
  config = require('./bitgert.config.js');
} catch (e) {
  console.warn('[Bitgert] No config found, using defaults');
  config = {
    network: { chainId: 32520, chainName: 'Bitgert', symbol: 'BRISE', decimals: 18 },
    rpc: { primary: 'https://rpc.icecreamswap.com/32520', backup: [], timeout: 10000, retries: 3 },
    dust: { threshold: 0.0001, sweepThreshold: 1, consolidationEnabled: true },
    gas: { maxGasPrice: '50000000000', gasLimit: 21000 },
    explorer: 'https://brisescan.com',
    logging: { level: 'info' }
  };
}

// Ensure logs directory exists
const logsDir = path.join(__dirname, 'logs');
if (!fs.existsSync(logsDir)) {
  fs.mkdirSync(logsDir, { recursive: true });
}

// Logging utility
const LOG_FILE = path.join(logsDir, `bitgert-${new Date().toISOString().split('T')[0]}.log`);
function log(level, message, data = null) {
  const timestamp = new Date().toISOString();
  const entry = JSON.stringify({ timestamp, level, message, data });
  if (level === 'error') console.error(`[Bitgert ERROR] ${message}`, data || '');
  else if (level === 'warn') console.warn(`[Bitgert WARN] ${message}`, data || '');
  else console.log(`[Bitgert] ${message}`, data || '');
  try { fs.appendFileSync(LOG_FILE, entry + '\n'); } catch (e) {}
}

// Global state
let provider = null;
let wallet = null;
let connected = false;

/**
 * Initialize Bitgert provider with fallback support
 */
function initProvider(rpcUrl = null) {
  const rpc = rpcUrl || config.rpc.primary;
  try {
    provider = new ethers.JsonRpcProvider(rpc, {
      chainId: config.network.chainId,
      name: config.network.chainName,
      ensAddress: null
    });
    provider.getBlockNumber().then((block) => {
      connected = true;
      log('info', 'Connected to Bitgert network', { rpc, block });
    }).catch(() => { connected = false; });
    log('info', 'Initializing Bitgert provider', { rpc });
    return provider;
  } catch (error) {
    log('error', 'Failed to initialize provider', { error: error.message });
    return createMockProvider();
  }
}

function createMockProvider() {
  log('info', 'Using DEMO/MOCK mode');
  return {
    getBalance: async () => ethers.parseEther('0'),
    getTransactionCount: async () => 0,
    getNetwork: async () => ({ chainId: BigInt(config.network.chainId), name: config.network.chainName }),
    getBlockNumber: async () => 0,
    getFeeData: async () => ({ gasPrice: BigInt(config.gas.maxGasPrice) }),
    estimateGas: async () => BigInt(config.gas.gasLimit),
    sendTransaction: async () => ({ hash: '0xmock' })
  };
}

function initWallet(privateKey, rpcUrl = null) {
  if (!provider) initProvider(rpcUrl);
  wallet = new ethers.Wallet(privateKey, provider);
  log('info', 'Wallet initialized', { address: wallet.address });
  return wallet;
}

async function getBalance(address) {
  if (!provider) initProvider();
  try {
    const balance = await provider.getBalance(address);
    return { raw: balance.toString(), brise: ethers.formatEther(balance), usd: 0 };
  } catch (error) {
    log('error', 'Failed to get balance', { address, error: error.message });
    return { raw: '0', brise: '0', usd: 0 };
  }
}

async function getGasPrice() {
  if (!provider) initProvider();
  try {
    const feeData = await provider.getFeeData();
    return ethers.formatUnits(feeData.gasPrice, 'gwei') + ' gwei';
  } catch (error) { return '1 gwei'; }
}

async function scanForDust(walletAddress) {
  const balance = await getBalance(walletAddress);
  const brise = parseFloat(balance.brise);
  return {
    hasDust: brise > 0 && brise < config.dust.sweepThreshold,
    amount: brise,
    worthCollecting: brise >= config.dust.threshold
  };
}

async function consolidateDust(sourcePrivateKey, destinationAddress) {
  if (!config.dust.consolidationEnabled) return null;
  if (!provider) initProvider();
  try {
    const sourceWallet = new ethers.Wallet(sourcePrivateKey, provider);
    const balance = await getBalance(sourceWallet.address);
    const brise = parseFloat(balance.brise);
    if (brise < config.dust.threshold) return null;
    const gasLimit = config.gas.gasLimit;
    const gasPrice = (await provider.getFeeData()).gasPrice;
    const gasCost = ethers.formatEther(gasLimit * gasPrice);
    const sendAmount = brise - parseFloat(gasCost);
    if (sendAmount <= 0) return null;
    log('info', 'Consolidating dust', { from: sourceWallet.address, to: destinationAddress, amount: sendAmount });
    const tx = { to: destinationAddress, value: ethers.parseEther(sendAmount.toString()), gasLimit, gasPrice };
    const receipt = await sourceWallet.sendTransaction(tx);
    return { hash: receipt.hash, amount: sendAmount, explorer: `${config.explorer}/tx/${receipt.hash}` };
  } catch (error) {
    log('error', 'Consolidation failed', { error: error.message });
    return null;
  }
}

async function getNetworkInfo() {
  if (!provider) initProvider();
  try {
    const network = await provider.getNetwork();
    const blockNumber = await provider.getBlockNumber();
    return { chainId: Number(network.chainId), name: network.name, blockNumber, connected: true };
  } catch (error) {
    return { chainId: config.network.chainId, name: config.network.chainName, blockNumber: 0, connected: false };
  }
}

async function healthCheck() {
  try {
    const info = await getNetworkInfo();
    const gasPrice = await getGasPrice();
    return { status: info.connected ? 'healthy' : 'degraded', network: { chainId: info.chainId, blockNumber: info.blockNumber, gasPrice } };
  } catch (error) { return { status: 'error', error: error.message }; }
}

module.exports = {
  config, initProvider, initWallet, getBalance, getGasPrice, getNetworkInfo,
  scanForDust, consolidateDust, healthCheck,
  DUST_THRESHOLD: config.dust.threshold, CHAIN_ID: config.network.chainId, EXPLORER: config.explorer
};

log('info', 'Bitgert module loaded', { version: '1.0.0', chainId: config.network.chainId });
