/**
 * ==========================================
 * Folder Management System - Myl0n ROS Library
 * ==========================================
 * Extracted from: myl0n.js.txt (learn_folder, setupAdditionalFolders)
 * Purpose: File system organization for agent memory
 * 
 * Usage:
 *   const folders = require('./folder-manager.js');
 *   folders.init();
 *   folders.learn('new_pattern');
 */

const FS = require('fs');
const PATH = require('path');

const BASE_PATH = '/sdcard/myl0n';
const MEMORY_PATH = `${BASE_PATH}/memory`;
const SKILLS_PATH = `${BASE_PATH}/skills`;
const DATA_PATH = `${BASE_PATH}/data`;
const LOGS_PATH = `${BASE_PATH}/logs`;
const CACHE_PATH = `${BASE_PATH}/cache`;

const folders = {
    memory: MEMORY_PATH,
    skills: SKILLS_PATH,
    data: DATA_PATH,
    logs: LOGS_PATH,
    cache: CACHE_PATH
};

function ensureFolders() {
    Object.values(folders).forEach(path => {
        try {
            if (!FS.existsSync(path)) {
                FS.mkdirSync(path, { recursive: true });
                console.log(`Created folder: ${path}`);
            }
        } catch (e) {
            console.log(`Error creating folder ${path}:`, e.message);
        }
    });
    return folders;
}

function createFolderAndFile(folderPath, filePath, fileContent) {
    try {
        // Create folder if not exists
        if (!FS.existsSync(folderPath)) {
            FS.mkdirSync(folderPath, { recursive: true });
        }
        
        // Write file
        FS.writeFileSync(filePath, fileContent, 'utf8');
        console.log(`Created file: ${filePath}`);
        
        return { success: true, path: filePath };
    } catch (e) {
        console.log(`Error creating file ${filePath}:`, e.message);
        return { success: false, error: e.message };
    }
}

function readFileContent(filePath) {
    try {
        if (FS.existsSync(filePath)) {
            return FS.readFileSync(filePath, 'utf8');
        }
        return null;
    } catch (e) {
        console.log(`Error reading file ${filePath}:`, e.message);
        return null;
    }
}

function learn_folder() {
    // Learn from folder structure - build mental map
    const folderMap = {};
    
    function scanDir(dir, depth = 0) {
        if (depth > 5) return; // Max depth
        
        try {
            const items = FS.readdirSync(dir);
            folderMap[dir] = {
                files: items.filter(i => FS.statSync(PATH.join(dir, i)).isFile()),
                subdirs: items.filter(i => FS.statSync(PATH.join(dir, i)).isDirectory())
            };
            
            items.forEach(item => {
                const fullPath = PATH.join(dir, item);
                if (FS.statSync(fullPath).isDirectory()) {
                    scanDir(fullPath, depth + 1);
                }
            });
        } catch (e) {
            // Permission denied or other error
        }
    }
    
    scanDir(BASE_PATH);
    return folderMap;
}

function getMemoryUsage() {
    const usage = {
        memory: 0,
        skills: 0,
        data: 0,
        logs: 0,
        cache: 0,
        total: 0
    };
    
    function getDirSize(dir) {
        let size = 0;
        try {
            const items = FS.readdirSync(dir);
            items.forEach(item => {
                const fullPath = PATH.join(dir, item);
                const stat = FS.statSync(fullPath);
                if (stat.isDirectory()) {
                    size += getDirSize(fullPath);
                } else {
                    size += stat.size;
                }
            });
        } catch (e) {}
        return size;
    }
    
    Object.keys(folders).forEach(key => {
        usage[key] = getDirSize(folders[key]);
        usage.total += usage[key];
    });
    
    return usage;
}

function cleanupOldFiles(maxAgeDays = 30) {
    const maxAge = maxAgeDays * 24 * 60 * 60 * 1000;
    const now = Date.now();
    let deleted = 0;
    
    function cleanDir(dir) {
        try {
            const items = FS.readdirSync(dir);
            items.forEach(item => {
                const fullPath = PATH.join(dir, item);
                const stat = FS.statSync(fullPath);
                
                if (stat.isDirectory()) {
                    cleanDir(fullPath);
                    // Remove empty dirs
                    try {
                        if (FS.readdirSync(fullPath).length === 0) {
                            FS.rmdirSync(fullPath);
                        }
                    } catch (e) {}
                } else {
                    if (now - stat.mtimeMs > maxAge) {
                        FS.unlinkSync(fullPath);
                        deleted++;
                    }
                }
            });
        } catch (e) {}
    }
    
    cleanDir(CACHE_PATH);
    cleanDir(LOGS_PATH);
    
    return { deleted };
}

function init(options = {}) {
    ensureFolders();
    
    return {
        folders,
        ensure: ensureFolders,
        createFile: createFolderAndFile,
        readFile: readFileContent,
        learn: learn_folder,
        getUsage: getMemoryUsage,
        cleanup: cleanupOldFiles
    };
}

module.exports = { init, ensureFolders, createFolderAndFile, readFileContent, learn_folder, getMemoryUsage, cleanupOldFiles };
