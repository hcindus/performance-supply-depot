/**
 * ==========================================
 * Reward System - Myl0n ROS Library
 * ==========================================
 * Extracted from: myl0n.js.txt (awardReward function)
 * Purpose: Point-based reward system for agent behavior
 * 
 * Usage:
 *   const reward = require('./reward-system.js');
 *   reward.init();
 *   reward.award(10, "Completed task");
 *   let balance = reward.getBalance();
 */

const REWARD_STORAGE_PATH = '/sdcard/myl0n/rewards.json';

let rewards = {
    points: 0,
    history: [],
    streak: 0,
    lastReward: null
};

function loadRewards() {
    try {
        // For Node.js environment
        const fs = require('fs');
        if (fs.existsSync(REWARD_STORAGE_PATH)) {
            const data = fs.readFileSync(REWARD_STORAGE_PATH, 'utf8');
            rewards = JSON.parse(data);
        }
    } catch (e) {
        console.log('Reward system: Starting fresh');
    }
    return rewards;
}

function saveRewards() {
    try {
        const fs = require('fs');
        const dir = '/sdcard/myl0n';
        if (!fs.existsSync(dir)) {
            fs.mkdirSync(dir, { recursive: true });
        }
        fs.writeFileSync(REWARD_STORAGE_PATH, JSON.stringify(rewards, null, 2));
    } catch (e) {
        console.log('Reward system: Could not save', e.message);
    }
}

function awardReward(points, reason) {
    const now = new Date();
    
    // Check streak
    if (rewards.lastReward) {
        const lastDate = new Date(rewards.lastReward.date);
        const diffDays = Math.floor((now - lastDate) / (1000 * 60 * 60 * 24));
        
        if (diffDays === 1) {
            rewards.streak++;
            // Bonus for streak
            points += Math.floor(rewards.streak / 7) * 5; // +5 every 7 days
        } else if (diffDays > 1) {
            rewards.streak = 0;
        }
    }
    
    rewards.points += points;
    rewards.lastReward = {
        date: now.toISOString(),
        points: points,
        reason: reason,
        streak: rewards.streak
    };
    
    rewards.history.push({
        date: now.toISOString(),
        points: points,
        reason: reason,
        total: rewards.points,
        streak: rewards.streak
    });
    
    // Keep last 100 history
    if (rewards.history.length > 100) {
        rewards.history = rewards.history.slice(-100);
    }
    
    saveRewards();
    
    return {
        points: points,
        total: rewards.points,
        streak: rewards.streak,
        reason: reason
    };
}

function getBalance() {
    return rewards.points;
}

function getHistory(limit = 10) {
    return rewards.history.slice(-limit);
}

function getStreak() {
    return rewards.streak;
}

function getStats() {
    return {
        points: rewards.points,
        streak: rewards.streak,
        totalRewards: rewards.history.length,
        lastReward: rewards.lastReward
    };
}

function init(options = {}) {
    loadRewards();
    return {
        award: awardReward,
        balance: getBalance,
        history: getHistory,
        streak: getStreak,
        stats: getStats
    };
}

module.exports = { init, awardReward, getBalance, getHistory, getStreak, getStats };
