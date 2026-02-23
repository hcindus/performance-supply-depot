/**
 * Dusty Bitgert Configuration
 * Production settings
 */

module.exports = {
  network: { chainId: 32520, chainName: 'Bitgert', symbol: 'BRISE', decimals: 18 },
  rpc: { primary: 'https://rpc.icecreamswap.com/32520', backup: [], timeout: 10000, retries: 3 },
  dust: { threshold: 0.0001, sweepThreshold: 1, consolidationEnabled: true },
  gas: { maxGasPrice: '50 gwei', gasLimit: 21000 },
  explorer: 'https://brisescan.com',
  logging: { level: 'info', file: './logs/bitgert.log' }
};
