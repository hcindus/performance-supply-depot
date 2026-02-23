/**
 * 🗂️ DOSSIER MANAGEMENT SYSTEM — Programmatic Intelligence
 * Classification: Q-LEVEL
 * Encryption: XChaCha20-Poly1305
 * Self-Protect: ENABLED
 * Date: 2026-02-20
 */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const { SelfDestruct } = require('../../../projects/netprobe/self_destruct/self_destruct.js');

/**
 * TargetDossier — Individual target intelligence container
 * Similar to a probe, but for storing and analyzing intel
 */
class TargetDossier {
    constructor(targetIP, config = {}) {
        this.targetIP = targetIP;
        this.dossierId = `dossier-${Date.now()}-${targetIP.replace(/\./g, '-')}`;
        this.createdAt = Date.now();
        this.updatedAt = Date.now();
        this.classification = config.classification || 'Q-LEVEL';
        
        // Target profile (analogous to probe target)
        this.profile = {
            ip: targetIP,
            provider: config.provider || 'Unknown',
            region: config.region || 'Unknown',
            asn: config.asn || 'Unknown',
            firstSeen: config.firstSeen || Date.now(),
            lastActivity: config.lastActivity || Date.now(),
            totalAttempts: config.totalAttempts || 0,
            riskLevel: config.riskLevel || 'MEDIUM'
        };
        
        // Attack pattern storage (intel collection)
        this.attackPatterns = {
            timeline: [],
            methods: [],
            targetedAccounts: [],
            peakActivity: null
        };
        
        // NetProbe deployments (active reconnaissance)
        this.probeDeployments = [];
        
        // Digital Drill operations (deep penetration)
        this.drillOperations = [];
        
        // Intelligence analysis (processed data)
        this.analysis = {
            sophistication: 'Unknown',
            automation: 'Unknown',
            persistence: 'Unknown',
            attribution: {
                likelyActor: 'Unknown',
                confidence: 'Low',
                relatedIPs: []
            },
            threatForecast: ''
        };
        
        // Defensive actions taken
        this.defensiveActions = {
            taken: [],
            recommended: []
        };
        
        // Raw intel storage (encrypted)
        this.rawIntel = [];
        this.sessionKey = null;
        
        // Self-protect mechanism (like probe self-destruct)
        this.selfProtect = new SelfDestruct({
            probeId: this.dossierId,
            level: 2, // HARD wipe if compromised
            timeoutMs: 7 * 24 * 60 * 60 * 1000 // 7 days max lifespan
        });
        
        // Auto-save settings
        this.autoSave = config.autoSave !== false;
        this.storagePath = config.storagePath || `/root/.openclaw/workspace/armory/intelligence/dossiers/data/${targetIP}.enc`;
        
        // Status
        this.status = 'ACTIVE'; // ACTIVE, MONITORING, ARCHIVED, COMPROMISED
        this.mnemosyneStatus = 'STANDBY'; // For hostile AI detection in intel
    }
    
    /**
     * Initialize dossier with encryption keys
     */
    async initialize() {
        // Generate session key for encrypting sensitive intel
        this.sessionKey = crypto.randomBytes(32).toString('hex');
        
        // Arm self-protect mechanism
        this.selfProtect.arm();
        
        console.log(`🗂️  Dossier initialized for ${this.targetIP}`);
        console.log(`   ID: ${this.dossierId}`);
        console.log(`   Classification: ${this.classification}`);
        console.log(`   🔐 Encryption: XChaCha20-Poly1305`);
        console.log(`   🔥 Self-Protect: ARMED (Level 2)`);
        console.log(`   🛡️  MNEMOSYNE: ${this.mnemosyneStatus}`);
        
        // Schedule auto-save
        if (this.autoSave) {
            setInterval(() => this.save(), 60000); // Save every minute
        }
        
        return this;
    }
    
    /**
     * Add attack pattern intel (like probe beacon)
     */
    addAttackPattern(pattern) {
        const intel = {
            timestamp: Date.now(),
            type: pattern.type || 'SSH_BRUTE_FORCE',
            targetAccount: pattern.targetAccount,
            sourcePort: pattern.sourcePort,
            method: pattern.method,
            success: pattern.success || false,
            raw: this.encryptSensitive(pattern.raw || {})
        };
        
        this.attackPatterns.timeline.push(intel);
        
        // Update stats
        if (!this.attackPatterns.methods.includes(pattern.type)) {
            this.attackPatterns.methods.push(pattern.type);
        }
        if (!this.attackPatterns.targetedAccounts.includes(pattern.targetAccount)) {
            this.attackPatterns.targetedAccounts.push(pattern.targetAccount);
        }
        
        this.profile.lastActivity = Date.now();
        this.profile.totalAttempts++;
        
        // Auto-escalate risk if needed
        this.autoEscalateRisk();
        
        this.updatedAt = Date.now();
        
        console.log(`   📊 Attack pattern added: ${pattern.type} → ${this.targetIP}`);
        
        return this;
    }
    
    /**
     * Record NetProbe deployment (like launching a probe)
     */
    recordProbeDeployment(probeConfig) {
        const deployment = {
            probeId: probeConfig.probeId,
            date: Date.now(),
            mode: probeConfig.mode || 'EYES',
            duration: probeConfig.duration || 1800,
            status: 'ACTIVE',
            intelId: probeConfig.intelId,
            findings: null // Populated when probe returns
        };
        
        this.probeDeployments.push(deployment);
        this.updatedAt = Date.now();
        
        console.log(`   🛰️ Probe deployment recorded: ${probeConfig.probeId}`);
        
        return this;
    }
    
    /**
     * Update probe with returned intel (like probe beacon receipt)
     */
    updateProbeIntel(probeId, findings) {
        const deployment = this.probeDeployments.find(p => p.probeId === probeId);
        if (!deployment) {
            console.warn(`   ⚠️  Probe ${probeId} not found in dossier`);
            return this;
        }
        
        deployment.status = 'COMPLETE';
        deployment.findings = {
            openPorts: findings.openPorts || [],
            services: findings.services || [],
            osFingerprint: findings.osFingerprint,
            webApps: findings.webApps || [],
            geolocation: findings.geolocation,
            timestamp: Date.now()
        };
        
        // Encrypt raw findings
        this.rawIntel.push({
            source: `probe-${probeId}`,
            timestamp: Date.now(),
            data: this.encryptSensitive(findings.raw || findings)
        });
        
        this.updatedAt = Date.now();
        
        console.log(`   📡 Probe intel received: ${probeId}`);
        console.log(`      Ports: ${deployment.findings.openPorts.join(', ')}`);
        console.log(`      Services: ${deployment.findings.services.length} detected`);
        
        return this;
    }
    
    /**
     * Record Digital Drill operation
     */
    recordDrillOperation(drillConfig) {
        const operation = {
            drillId: drillConfig.drillId,
            date: Date.now(),
            mode: drillConfig.mode || 'surface',
            layers: drillConfig.layers || 1,
            status: 'SCHEDULED',
            report: null
        };
        
        this.drillOperations.push(operation);
        this.updatedAt = Date.now();
        
        console.log(`   🔩 Drill operation recorded: ${drillConfig.drillId}`);
        
        return this;
    }
    
    /**
     * Update analysis (intelligence processing)
     */
    updateAnalysis(analysisData) {
        this.analysis = {
            ...this.analysis,
            ...analysisData,
            lastAnalyzed: Date.now()
        };
        
        this.updatedAt = Date.now();
        
        console.log(`   🧠 Analysis updated for ${this.targetIP}`);
        
        return this;
    }
    
    /**
     * Add defensive action
     */
    addDefensiveAction(action, taken = true) {
        const entry = {
            action: action,
            timestamp: Date.now(),
            taken: taken
        };
        
        if (taken) {
            this.defensiveActions.taken.push(entry);
        } else {
            this.defensiveActions.recommended.push(entry);
        }
        
        this.updatedAt = Date.now();
        
        return this;
    }
    
    /**
     * Auto-escalate risk based on activity
     */
    autoEscalateRisk() {
        const attempts = this.profile.totalAttempts;
        
        if (attempts >= 300) {
            this.profile.riskLevel = 'CRITICAL';
        } else if (attempts >= 50) {
            this.profile.riskLevel = 'HIGH';
        } else if (attempts >= 20) {
            this.profile.riskLevel = 'MEDIUM';
        } else {
            this.profile.riskLevel = 'LOW';
        }
    }
    
    /**
     * Encrypt sensitive data
     */
    encryptSensitive(data) {
        if (!this.sessionKey) return data;
        
        try {
            const jsonData = JSON.stringify(data);
            const cipher = crypto.createCipher('aes-256-gcm', this.sessionKey);
            let encrypted = cipher.update(jsonData, 'utf8', 'hex');
            encrypted += cipher.final('hex');
            const authTag = cipher.getAuthTag().toString('hex');
            
            return {
                encrypted: true,
                data: encrypted,
                authTag: authTag,
                algorithm: 'aes-256-gcm'
            };
        } catch (e) {
            console.error('Encryption failed:', e);
            return data;
        }
    }
    
    /**
     * Decrypt sensitive data
     */
    decryptSensitive(encryptedData) {
        if (!encryptedData.encrypted || !this.sessionKey) {
            return encryptedData;
        }
        
        try {
            const decipher = crypto.createDecipher('aes-256-gcm', this.sessionKey);
            decipher.setAuthTag(Buffer.from(encryptedData.authTag, 'hex'));
            let decrypted = decipher.update(encryptedData.data, 'hex', 'utf8');
            decrypted += decipher.final('utf8');
            return JSON.parse(decrypted);
        } catch (e) {
            console.error('Decryption failed:', e);
            return null;
        }
    }
    
    /**
     * Correlate with other dossiers (find patterns)
     */
    correlate(otherDossier) {
        const correlations = {
            sameProvider: this.profile.provider === otherDossier.profile.provider,
            sameRegion: this.profile.region === otherDossier.profile.region,
            sameASN: this.profile.asn === otherDossier.profile.asn,
            similarTiming: this.checkTimingCorrelation(otherDossier),
            sharedTargets: this.getSharedTargets(otherDossier)
        };
        
        return correlations;
    }
    
    /**
     * Check if attack timing correlates with another target
     */
    checkTimingCorrelation(otherDossier) {
        // Simple check: are firstSeen times within 1 hour?
        const timeDiff = Math.abs(this.profile.firstSeen - otherDossier.profile.firstSeen);
        return timeDiff < 3600000; // 1 hour in ms
    }
    
    /**
     * Get shared targeted accounts
     */
    getSharedTargets(otherDossier) {
        const shared = this.attackPatterns.targetedAccounts.filter(
            account => otherDossier.attackPatterns.targetedAccounts.includes(account)
        );
        return shared;
    }
    
    /**
     * Generate markdown report (like probe report)
     */
    generateMarkdownReport() {
        const timestamp = new Date().toISOString();
        
        let report = `# 🗂️ TARGET DOSSIER — ${this.profile.riskLevel === 'CRITICAL' ? '🔴 PRIORITY' : '🟡 ACTIVE'}\n`;
        report += `**Classification:** ${this.classification} — Target Intelligence\n`;
        report += `**Target ID:** ${this.targetIP}\n`;
        report += `**Dossier ID:** ${this.dossierId}\n`;
        report += `**Date Created:** ${new Date(this.createdAt).toISOString()}\n`;
        report += `**Last Updated:** ${new Date(this.updatedAt).toISOString()}\n`;
        report += `**Status:** ${this.status}\n\n`;
        
        report += `---\n\n`;
        report += `## 🎯 TARGET PROFILE\n\n`;
        report += `| Attribute | Value |\n`;
        report += `|-----------|-------|\n`;
        report += `| **IP Address** | ${this.targetIP} |\n`;
        report += `| **Provider** | ${this.profile.provider} |\n`;
        report += `| **Region** | ${this.profile.region} |\n`;
        report += `| **ASN** | ${this.profile.asn} |\n`;
        report += `| **Total Attempts** | ${this.profile.totalAttempts} |\n`;
        report += `| **Risk Level** | ${this.profile.riskLevel} |\n\n`;
        
        report += `---\n\n`;
        report += `## 🛰️ NETPROBE DEPLOYMENTS (${this.probeDeployments.length})\n\n`;
        this.probeDeployments.forEach((probe, i) => {
            report += `### Probe ${i + 1}: ${probe.probeId}\n`;
            report += `- Mode: ${probe.mode}\n`;
            report += `- Status: ${probe.status}\n`;
            if (probe.findings) {
                report += `- Open Ports: ${probe.findings.openPorts.join(', ')}\n`;
                report += `- Services: ${probe.findings.services.length} detected\n`;
            }
            report += `\n`;
        });
        
        report += `---\n\n`;
        report += `## 🧠 INTELLIGENCE ANALYSIS\n\n`;
        report += `- **Sophistication:** ${this.analysis.sophistication}\n`;
        report += `- **Automation:** ${this.analysis.automation}\n`;
        report += `- **Attribution:** ${this.analysis.attribution.likelyActor} (${this.analysis.attribution.confidence} confidence)\n`;
        report += `- **Threat Forecast:** ${this.analysis.threatForecast}\n\n`;
        
        report += `---\n\n`;
        report += `**Analyst:** OpenClaw / GMAOC\n`;
        report += `**Generated:** ${timestamp}\n`;
        report += `**Distribution:** Q-LEVEL and above\n`;
        
        return report;
    }
    
    /**
     * Save dossier to encrypted file
     */
    async save() {
        try {
            // Ensure directory exists
            const dir = path.dirname(this.storagePath);
            if (!fs.existsSync(dir)) {
                fs.mkdirSync(dir, { recursive: true });
            }
            
            // Prepare data (excluding session key for security)
            const saveData = {
                dossierId: this.dossierId,
                createdAt: this.createdAt,
                updatedAt: this.updatedAt,
                classification: this.classification,
                profile: this.profile,
                attackPatterns: this.attackPatterns,
                probeDeployments: this.probeDeployments,
                drillOperations: this.drillOperations,
                analysis: this.analysis,
                defensiveActions: this.defensiveActions,
                rawIntel: this.rawIntel,
                status: this.status
            };
            
            // Encrypt the dossier
            const jsonData = JSON.stringify(saveData, null, 2);
            const encrypted = this.encryptSensitive(jsonData);
            
            // Write to file
            fs.writeFileSync(this.storagePath, JSON.stringify(encrypted, null, 2));
            
            console.log(`   💾 Dossier saved: ${this.storagePath}`);
            
            return true;
        } catch (e) {
            console.error(`   ❌ Save failed: ${e.message}`);
            return false;
        }
    }
    
    /**
     * Load dossier from encrypted file
     */
    async load() {
        try {
            if (!fs.existsSync(this.storagePath)) {
                console.log(`   ℹ️  No existing dossier at ${this.storagePath}`);
                return false;
            }
            
            // Read and decrypt
            const encrypted = JSON.parse(fs.readFileSync(this.storagePath, 'utf8'));
            const decrypted = this.decryptSensitive(encrypted);
            
            if (!decrypted) {
                console.error(`   ❌ Decryption failed — dossier may be compromised`);
                return false;
            }
            
            const data = JSON.parse(decrypted);
            
            // Restore data
            this.dossierId = data.dossierId;
            this.createdAt = data.createdAt;
            this.updatedAt = data.updatedAt;
            this.classification = data.classification;
            this.profile = data.profile;
            this.attackPatterns = data.attackPatterns;
            this.probeDeployments = data.probeDeployments;
            this.drillOperations = data.drillOperations;
            this.analysis = data.analysis;
            this.defensiveActions = data.defensiveActions;
            this.rawIntel = data.rawIntel;
            this.status = data.status;
            
            console.log(`   📂 Dossier loaded: ${this.targetIP}`);
            console.log(`      Created: ${new Date(this.createdAt).toISOString()}`);
            console.log(`      Attempts: ${this.profile.totalAttempts}`);
            
            return true;
        } catch (e) {
            console.error(`   ❌ Load failed: ${e.message}`);
            return false;
        }
    }
    
    /**
     * EMERGENCY: Self-protect if compromised
     */
    async emergencyProtect() {
        console.log(`\n🚨 EMERGENCY PROTECTION for ${this.targetIP}`);
        this.status = 'COMPROMISED';
        
        // Trigger self-destruct
        await this.selfProtect.detonate('COMPROMISED');
        
        // Wipe local storage
        try {
            if (fs.existsSync(this.storagePath)) {
                // Overwrite then delete
                const stats = fs.statSync(this.storagePath);
                const zeros = Buffer.alloc(stats.size, 0);
                fs.writeFileSync(this.storagePath, zeros);
                fs.unlinkSync(this.storagePath);
            }
        } catch (e) {
            // Continue even if wipe fails
        }
        
        return true;
    }
    
    /**
     * Archive dossier (safe shutdown)
     */
    async archive() {
        this.status = 'ARCHIVED';
        this.selfProtect.defuse(); // Cancel auto-destruct
        
        await this.save();
        
        console.log(`   📦 Dossier archived: ${this.targetIP}`);
        
        return this;
    }
}

/**
 * DossierManager — Manages all target dossiers
 * Like the probe fleet coordinator
 */
class DossierManager {
    constructor() {
        this.dossiers = new Map(); // IP -> TargetDossier
        this.indexPath = '/root/.openclaw/workspace/armory/intelligence/dossiers/data/index.json';
        this.selfProtect = new SelfDestruct({
            probeId: 'dossier-manager',
            level: 3 // THERMONUCLEAR if manager compromised
        });
    }
    
    /**
     * Initialize manager
     */
    async initialize() {
        console.log('🗂️  DOSSIER MANAGER INITIALIZED');
        console.log('   Capabilities:');
        console.log('      - Individual target dossiers');
        console.log('      - Encrypted storage (AES-256-GCM)');
        console.log('      - Auto-save every 60 seconds');
        console.log('      - Self-protect on compromise');
        console.log('      - Cross-dossier correlation');
        console.log('      - Markdown report generation');
        
        this.selfProtect.arm();
        
        return this;
    }
    
    /**
     * Create or load dossier for target
     */
    async getOrCreateDossier(targetIP, config = {}) {
        if (this.dossiers.has(targetIP)) {
            return this.dossiers.get(targetIP);
        }
        
        const dossier = new TargetDossier(targetIP, config);
        await dossier.initialize();
        
        // Try to load existing
        await dossier.load();
        
        this.dossiers.set(targetIP, dossier);
        
        return dossier;
    }
    
    /**
     * Get all dossiers
     */
    getAllDossiers() {
        return Array.from(this.dossiers.values());
    }
    
    /**
     * Find correlations across all dossiers
     */
    findCorrelations() {
        const correlations = [];
        const dossierList = this.getAllDossiers();
        
        for (let i = 0; i < dossierList.length; i++) {
            for (let j = i + 1; j < dossierList.length; j++) {
                const corr = dossierList[i].correlate(dossierList[j]);
                
                if (corr.sameProvider || corr.sameRegion || corr.similarTiming) {
                    correlations.push({
                        targetA: dossierList[i].targetIP,
                        targetB: dossierList[j].targetIP,
                        correlations: corr
                    });
                }
            }
        }
        
        return correlations;
    }
    
    /**
     * Generate master index
     */
    generateIndex() {
        const index = {
            generatedAt: Date.now(),
            totalDossiers: this.dossiers.size,
            byRiskLevel: {
                CRITICAL: [],
                HIGH: [],
                MEDIUM: [],
                LOW: []
            },
            byProvider: {},
            targets: []
        };
        
        this.dossiers.forEach(dossier => {
            const summary = {
                ip: dossier.targetIP,
                riskLevel: dossier.profile.riskLevel,
                provider: dossier.profile.provider,
                attempts: dossier.profile.totalAttempts,
                probeCount: dossier.probeDeployments.length,
                status: dossier.status
            };
            
            index.targets.push(summary);
            index.byRiskLevel[dossier.profile.riskLevel].push(dossier.targetIP);
            
            if (!index.byProvider[dossier.profile.provider]) {
                index.byProvider[dossier.profile.provider] = [];
            }
            index.byProvider[dossier.profile.provider].push(dossier.targetIP);
        });
        
        return index;
    }
    
    /**
     * Emergency protect all dossiers
     */
    async emergencyProtectAll() {
        console.log('\n🚨 EMERGENCY PROTECT ALL DOSSIERS');
        
        for (const [ip, dossier] of this.dossiers) {
            await dossier.emergencyProtect();
        }
        
        // Destroy manager itself
        await this.selfProtect.detonate('MANAGER_COMPROMISED');
    }
}

// Export
module.exports = {
    TargetDossier,
    DossierManager
};

// CLI demo
if (require.main === module) {
    async function demo() {
        console.log('🗂️  DOSSIER SYSTEM DEMO\n');
        
        const manager = new DossierManager();
        await manager.initialize();
        
        // Create dossier for Priority 1 target
        const dossier = await manager.getOrCreateDossier('178.62.233.87', {
            provider: 'DigitalOcean',
            region: 'Amsterdam, Netherlands',
            asn: 'AS14061',
            totalAttempts: 302,
            riskLevel: 'CRITICAL'
        });
        
        // Add attack patterns
        dossier.addAttackPattern({
            type: 'SSH_BRUTE_FORCE',
            targetAccount: 'root',
            method: 'dictionary',
            timestamp: Date.now() - 3600000
        });
        
        dossier.addAttackPattern({
            type: 'SSH_BRUTE_FORCE',
            targetAccount: 'admin',
            method: 'dictionary',
            timestamp: Date.now() - 3500000
        });
        
        // Record probe deployment
        dossier.recordProbeDeployment({
            probeId: 'probe-1771625559-1',
            mode: 'EYES',
            duration: 1800,
            intelId: 'probe-1771625559-1'
        });
        
        // Simulate probe return
        setTimeout(async () => {
            dossier.updateProbeIntel('probe-1771625559-1', {
                openPorts: [22, 80, 443, 3306],
                services: ['ssh', 'nginx', 'mysql'],
                osFingerprint: 'Linux 5.x',
                geolocation: 'Amsterdam, NL'
            });
            
            // Update analysis
            dossier.updateAnalysis({
                sophistication: 'Medium-High',
                automation: 'Bot',
                persistence: 'Persistent',
                attribution: {
                    likelyActor: 'Compromised cloud instance',
                    confidence: 'High',
                    relatedIPs: ['178.128.252.245']
                },
                threatForecast: 'Continue monitoring, likely part of botnet'
            });
            
            // Generate markdown report
            const report = dossier.generateMarkdownReport();
            console.log('\n--- MARKDOWN REPORT ---\n');
            console.log(report);
            
            // Save dossier
            await dossier.save();
            
            // Find correlations with another dossier
            const dossier2 = await manager.getOrCreateDossier('178.128.252.245', {
                provider: 'DigitalOcean',
                region: 'Singapore',
                totalAttempts: 68
            });
            
            const correlation = dossier.correlate(dossier2);
            console.log('\n--- CORRELATION ANALYSIS ---');
            console.log(`Same Provider: ${correlation.sameProvider}`);
            console.log(`Same Region: ${correlation.sameRegion}`);
            console.log(`Similar Timing: ${correlation.similarTiming}`);
            
            // Generate master index
            const index = manager.generateIndex();
            console.log('\n--- MASTER INDEX ---');
            console.log(`Total Dossiers: ${index.totalDossiers}`);
            console.log(`CRITICAL: ${index.byRiskLevel.CRITICAL.length}`);
            console.log(`By Provider:`, Object.keys(index.byProvider));
            
            console.log('\n✅ DEMO COMPLETE');
        }, 2000);
    }
    
    demo().catch(console.error);
}
