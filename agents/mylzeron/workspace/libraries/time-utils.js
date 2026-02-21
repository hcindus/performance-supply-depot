/**
 * ==========================================
 * Time Utilities - Myl0n ROS Library
 * ==========================================
 * Extracted from: myl0n.js.txt (GetTime, GetDay, FState)
 * Purpose: Time and date utilities
 * 
 * Usage:
 *   const time = require('./time-utils.js');
 *   let hour = time.GetTime();
 *   let day = time.GetDay();
 */

function GetTime() {
    const now = new Date();
    let hours = now.getHours();
    const minutes = now.getMinutes();
    const seconds = now.getSeconds();
    
    const ampm = hours >= 12 ? 'PM' : 'AM';
    hours = hours % 12;
    hours = hours ? hours : 12;
    
    return `${hours}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')} ${ampm}`;
}

function GetDay() {
    const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    const now = new Date();
    return days[now.getDay()];
}

function GetDate() {
    const now = new Date();
    return now.toISOString().split('T')[0];
}

function GetTimestamp() {
    return Date.now();
}

function FState() {
    // Full state - all time info
    return {
        time: GetTime(),
        day: GetDay(),
        date: GetDate(),
        timestamp: GetTimestamp(),
        hour: new Date().getHours(),
        minute: new Date().getMinutes(),
        second: new Date().getSeconds()
    };
}

function playTime() {
    // Get current time for play/activity tracking
    return {
        start: Date.now(),
        time: GetTime(),
        day: GetDay()
    };
}

function checkPlayTime(startTime) {
    if (!startTime || !startTime.start) return null;
    
    const elapsed = Date.now() - startTime.start;
    const seconds = Math.floor(elapsed / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    
    return {
        elapsed: elapsed,
        seconds: seconds,
        minutes: minutes,
        hours: hours,
        formatted: `${hours}h ${minutes % 60}m ${seconds % 60}s`
    };
}

function isWeekend() {
    const day = new Date().getDay();
    return day === 0 || day === 6;
}

function isBusinessHours(start = 9, end = 17) {
    const now = new Date();
    const hour = now.getHours();
    return hour >= start && hour < end && !isWeekend();
}

function getTimeGreeting() {
    const hour = new Date().getHours();
    
    if (hour >= 5 && hour < 12) return "Good morning";
    if (hour >= 12 && hour < 17) return "Good afternoon";
    if (hour >= 17 && hour < 21) return "Good evening";
    return "Good night";
}

module.exports = {
    GetTime,
    GetDay,
    GetDate,
    GetTimestamp,
    FState,
    playTime,
    checkPlayTime,
    isWeekend,
    isBusinessHours,
    getTimeGreeting
};
