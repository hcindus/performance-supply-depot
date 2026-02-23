/**
 * Self-Destruct Integration for Digital Drill
 * Auto-detonates after mission completion
 */

const { SelfDestruct } = require('../self_destruct/self_destruct.js');

class DrillSelfDestructIntegration {
    constructor(drillInstance) {
        this.drill = drillInstance;
        this.selfDestruct = new SelfDestruct({
            level: 1,  // SOFT default
            autoTriggers: ['mission_complete', 'dead_mans_switch'],
            deadMansSwitchTimeout: 3600000  // 1 hour
        });
        
        this.wireIntegration();
    }
    
    wireIntegration() {
        // Pre-mission: Arm self-destruct
        this.drill.on('mission_start', () => {
            console.log('[Self-Destruct] Armed for mission');
            this.selfDestruct.arm();
        });
        
        // Post-mission: Auto-detonate
        this.drill.on('mission_complete', (data) => {
            console.log('[Self-Destruct] Mission complete - auto-detonating...');
            this.selfDestruct.detonate({
                reason: 'mission_complete',
                dataExtracted: data.size,
                target: data.target
            });
        });
        
        // Honeypot detection: Emergency Level 3
        this.drill.on('honeypot_detected', () => {
            console.log('[Self-Destruct] 🚨 HONEYPOT DETECTED - LEVEL 3 DETONATION');
            this.selfDestruct.level = 3;  // THERMONUCLEAR
            this.selfDestruct.detonate({
                reason: 'honeypot_detection',
                level: 3,
                emergency: True
            });
        });
    }
}

module.exports = { DrillSelfDestructIntegration };
