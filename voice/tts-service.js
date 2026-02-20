#!/usr/bin/env node

/**
 * TTS Service - Unified Text-to-Speech Service
 * Supports: espeak (free), piper (neural), elevenlabs (API)
 * 
 * Usage:
 *   node tts-service.js --engine espeak --text "Hello world"
 *   node tts-service.js --engine piper --voice amy --text "Hello"
 *   node tts-service.js --engine elevenlabs --voice adam --text "Hello"
 * 
 * Or use as API:
 *   GET /speak?engine=espeak&text=Hello
 */

const { exec, spawn } = require('child_process');
const fs = require('fs');
const path = require('path');
const http = require('http');
const url = require('url');

// Configuration
const CONFIG = {
  port: process.env.TTS_PORT || 3847,
  engines: {
    espeak: {
      binary: '/usr/bin/espeak',
      available: null // Checked at runtime
    },
    piper: {
      binary: '/opt/piper/piper',
      voiceDir: '/opt/piper/voices',
      model: null, // Set with --model flag
      available: null
    },
    elevenlabs: {
      // API key - set via ELEVENLABS_API_KEY environment variable
      // Get from: https://elevenlabs.io/app/settings/api-keys
      apiKey: process.env.ELEVENLABS_API_KEY || '',
      
      // Use eleven_flash_v2_5 (works on free tier)
      model: 'eleven_flash_v2_5',
      
      // Voice IDs stored for reference
      // Note: ztnpYzQJyWffPj1VC5Uw provided by Captain but key was invalid
      // Note: krsfpqv6ExDAAyh8Ea6y = Miles voice ID
      // Voice IDs for AGI Company
      // Organized by gender: 2 male, 2 female
      voiceMap: {
        // MALE VOICES
        'mortimer': 'ztnpYzQJyWffPj1VC5Uw', // Mortimer (Captain provided)
        'miles': 'krsfpqv6ExDAAyh8Ea6y',    // Miles (my voice!)
        
        // FEMALE VOICES
        'mylthrees': 'AA30ZfOdY16oVkASrrGJ', // Mylthrees
        'claiE': '50BdVlngDYeoh9pVuQof',     // Claie
        
        // STANDARD VOICES
        'adam': 'pNInz6obpgDQGcFmaJgB',
        'rachel': '21m00Tcm4TlvDq8ikWAM',
        'sam': 'ODqDArmn3iD25GAF5W2S'
      },
      
      // GM/Pi Voice Modulation (based on Captain's aesthetic constants)
      // GM = 1.618033988749895 (Golden Ratio)
      // PI = 3.141592653589793
      gmPiSettings: {
        pitch: 1.618,        // GM for pitch
        rate: 1.94,          // PI / GM for rate
        style: 1.618,        // GM for style (expressiveness)
        stability: 0.618,    // 1/GM for consistency
        similarityBoost: 0.618 // 1/GM for clarity
      },
      available: null
    }
  },
  defaultEngine: 'espeak',
  outputDir: '/tmp/tts-output'
};

// Ensure output directory exists
if (!fs.existsSync(CONFIG.outputDir)) {
  fs.mkdirSync(CONFIG.outputDir, { recursive: true });
}

// Check engine availability
function checkEngine(engine) {
  if (engine === 'espeak') {
    try {
      return fs.existsSync('/usr/bin/espeak');
    } catch (e) { return false; }
  }
  
  if (engine === 'piper') {
    try {
      return fs.existsSync('/opt/piper/piper');
    } catch (e) { return false; }
  }
  
  if (engine === 'elevenlabs') {
    return !!CONFIG.engines.elevenlabs.apiKey;
  }
  
  return false;
}

// espeak TTS
function speakEspeak(text, options = {}) {
  return new Promise((resolve, reject) => {
    const outputFile = path.join(CONFIG.outputDir, `espeak_${Date.now()}.wav`);
    const args = [
      '-w', outputFile,
      '-s', options.speed || '150',
      '-v', options.voice || 'en-us',
      text
    ];
    
    exec(`/usr/bin/espeak ${args.join(' ')}`, (error, stdout, stderr) => {
      if (error) {
        reject(error);
        return;
      }
      resolve(outputFile);
    });
  });
}

// piper TTS
function speakPiper(text, options = {}) {
  return new Promise((resolve, reject) => {
    const outputFile = path.join(CONFIG.outputDir, `piper_${Date.now()}.wav`);
    const model = options.model || 'en_US-amy-low';
    const modelPath = path.join(CONFIG.engines.piper.voiceDir, model + '.onnx');
    const configPath = path.join(CONFIG.engines.piper.voiceDir, model + '.json');
    
    // Check if model exists
    if (!fs.existsSync(modelPath)) {
      reject(new Error(`Piper voice model not found: ${model}`));
      return;
    }
    
    const piper = spawn('/opt/piper/piper', [
      '-m', modelPath,
      '-c', configPath,
      '-f', outputFile
    ]);
    
    piper.stdin.write(text);
    piper.stdin.end();
    
    piper.on('close', (code) => {
      if (code === 0) {
        resolve(outputFile);
      } else {
        reject(new Error(`Piper exited with code ${code}`));
      }
    });
  });
}

// ElevenLabs TTS
function speakElevenLabs(text, options = {}) {
  return new Promise((resolve, reject) => {
    const apiKey = CONFIG.engines.elevenlabs.apiKey;
    if (!apiKey) {
      reject(new Error('ElevenLabs API key not set'));
      return;
    }
    
    const voiceId = options.voice || 'adam';
    const outputFile = path.join(CONFIG.outputDir, `elevenlabs_${Date.now()}.mp3`);
    
    const postData = JSON.stringify({
      text: text,
      model_id: 'eleven_monolingual_v1',
      voice_settings: {
        stability: CONFIG.engines.elevenlabs.gmPiSettings.stability,
        similarity_boost: CONFIG.engines.elevenlabs.gmPiSettings.similarityBoost,
        style: CONFIG.engines.elevenlabs.gmPiSettings.style,
        speed: CONFIG.engines.elevenlabs.gmPiSettings.rate
      }
    });
    
    const options2 = {
      hostname: 'api.elevenlabs.io',
      path: `/v1/text-to-speech/${voiceId}`,
      method: 'POST',
      headers: {
        'Accept': 'audio/mpeg',
        'Content-Type': 'application/json',
        'xi-api-key': apiKey
      }
    };
    
    const req = http.request(options2, (res) => {
      if (res.statusCode !== 200) {
        reject(new Error(`ElevenLabs API error: ${res.statusCode}`));
        return;
      }
      
      const writeStream = fs.createWriteStream(outputFile);
      res.pipe(writeStream);
      
      writeStream.on('finish', () => {
        resolve(outputFile);
      });
    });
    
    req.on('error', reject);
    req.write(postData);
    req.end();
  });
}

// Main speak function
async function speak(text, engine = CONFIG.defaultEngine, options = {}) {
  const available = checkEngine(engine);
  
  if (!available) {
    throw new Error(`Engine ${engine} is not available`);
  }
  
  switch (engine) {
    case 'espeak':
      return speakEspeak(text, options);
    case 'piper':
      return speakPiper(text, options);
    case 'elevenlabs':
      return speakElevenLabs(text, options);
    default:
      throw new Error(`Unknown engine: ${engine}`);
  }
}

// HTTP Server
function startServer() {
  const server = http.createServer(async (req, res) => {
    const parsedUrl = url.parse(req.url, true);
    const pathname = parsedUrl.pathname;
    
    // CORS headers
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    
    if (parsedUrl.method === 'OPTIONS') {
      res.writeHead(204);
      res.end();
      return;
    }
    
    // Routes
    if (pathname === '/health' || pathname === '/') {
      const engines = {};
      for (const [name, config] of Object.entries(CONFIG.engines)) {
        engines[name] = checkEngine(name);
      }
      
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({
        status: 'ok',
        defaultEngine: CONFIG.defaultEngine,
        engines: engines
      }));
      return;
    }
    
    if (pathname === '/speak') {
      const { engine, text, voice, model, speed } = parsedUrl.query;
      
      if (!text) {
        res.writeHead(400, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: 'Missing text parameter' }));
        return;
      }
      
      const selectedEngine = engine || CONFIG.defaultEngine;
      
      try {
        const outputFile = await speak(text, selectedEngine, { 
          voice, 
          model,
          speed 
        });
        
        const stat = fs.statSync(outputFile);
        const fileStream = fs.createReadStream(outputFile);
        
        res.writeHead(200, {
          'Content-Type': 'audio/wav',
          'Content-Length': stat.size,
          'Content-Disposition': `attachment; filename="speech.wav"`
        });
        
        fileStream.pipe(res);
        
        // Cleanup after sending
        fileStream.on('close', () => {
          fs.unlink(outputFile, () => {});
        });
        
      } catch (error) {
        res.writeHead(500, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: error.message }));
      }
      return;
    }
    
    // 404
    res.writeHead(404);
    res.end('Not found');
  });
  
  server.listen(CONFIG.port, () => {
    console.log(`🎤 TTS Service running on port ${CONFIG.port}`);
    console.log(`   Available engines: ${Object.keys(CONFIG.engines).filter(e => checkEngine(e)).join(', ')}`);
    console.log(`   Default: ${CONFIG.defaultEngine}`);
  });
}

// CLI mode
if (require.main === module) {
  const args = process.argv.slice(2);
  
  if (args.includes('--help') || args.includes('-h')) {
    console.log(`
TTS Service - Unified Text-to-Speech

Usage:
  node tts-service.js --engine <espeak|piper|elevenlabs> --text "Hello world"
  node tts-service.js --server  # Start HTTP server

Options:
  --engine, -e     TTS engine to use (default: espeak)
  --text, -t       Text to speak
  --voice, -v      Voice/character to use
  --model, -m      Piper model name
  --speed, -s      Speech speed (espeak only)
  --server, -S     Start HTTP server mode
  
Environment:
  ELEVENLABS_API_KEY   API key for ElevenLabs
  TTS_PORT             Server port (default: 3847)
    `);
    process.exit(0);
  }
  
  if (args.includes('--server') || args.includes('-S')) {
    startServer();
  } else {
    // CLI mode
    let engine = CONFIG.defaultEngine;
    let text = '';
    let voice, model, speed;
    
    for (let i = 0; i < args.length; i++) {
      if (args[i] === '--engine' || args[i] === '-e') {
        engine = args[++i];
      } else if (args[i] === '--text' || args[i] === '-t') {
        text = args[++i];
      } else if (args[i] === '--voice' || args[i] === '-v') {
        voice = args[++i];
      } else if (args[i] === '--model' || args[i] === '-m') {
        model = args[++i];
      } else if (args[i] === '--speed' || args[i] === '-s') {
        speed = args[++i];
      }
    }
    
    if (!text) {
      console.error('Error: --text is required');
      process.exit(1);
    }
    
    speak(text, engine, { voice, model, speed })
      .then(file => {
        console.log(`🎤 Audio saved to: ${file}`);
      })
      .catch(err => {
        console.error('Error:', err.message);
        process.exit(1);
      });
  }
}

module.exports = { speak, checkEngine, CONFIG };
