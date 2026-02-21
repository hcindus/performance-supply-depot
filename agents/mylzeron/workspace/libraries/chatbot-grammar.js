/**
 * ==========================================
 * Chatbot Grammar System - Myl0n ROS Library
 * ==========================================
 * Extracted from: myl0n.js.txt
 * Purpose: Multilingual chatbot response generation
 * 
 * Usage:
 *   const chatbot = require('./chatbot-grammar.js');
 *   chatbot.init();
 *   let response = chatbot.respond("hello");
 *   response = chatbot.respond("hola", "es");
 */

const _ = {
    random: (min, max) => Math.random() * (max - min) + min,
    map: (arr, fn) => arr.map(fn)
};

// Multilingual grammar for chatbot responses
let grammar = {
    "en": {
        "morning_greeting": ["Good morning", "Hello morning", "Rise and shine"],
        "afternoon_greeting": ["Good afternoon", "Hello afternoon", "Afternoon vibes"],
        "evening_greeting": ["Good evening", "Hello evening", "Evening calm"],
        "night_greeting": ["Good night", "Hello night", "Nighttime greetings"],
        "adjective": ["beautiful", "wonderful", "amazing", "lovely", "fantastic"],
        "adverb": ["quickly", "happily", "eagerly", "brightly", "gently"],
        "noun": ["world", "everyone", "friend", "team", "companion"],
        "verb": ["start", "enjoy", "explore", "achieve", "embrace"],
        "preposition": ["with", "for", "in", "on", "to"],
        "action": ["opening", "starting", "launching", "initiating"],
        "sentence": [
            "#time_greeting#, #adjective# #noun#!",
            "#time_greeting#, how are you doing #adverb#?",
            "#action# your request, #adjective# #noun#!",
            "#verb# your day #preposition# joy, #adjective# #noun#!",
            "#verb# the journey #preposition# #adjective# #noun#."
        ]
    },
    "es": {
        "morning_greeting": ["Buenos días", "Hola mañana", "Despierta y brilla"],
        "afternoon_greeting": ["Buenas tardes", "Hola tarde", "Vibes de la tarde"],
        "evening_greeting": ["Buenas noches", "Hola noche", "Calma de la noche"],
        "night_greeting": ["Buenas noches", "Hola medianoche", "Saludos nocturnos"],
        "adjective": ["hermoso", "maravilloso", "increíble", "encantador", "fantástico"],
        "adverb": ["rápidamente", "felizmente", "ansiosamente", "brillantemente", "suavemente"],
        "noun": ["mundo", "todos", "amigo", "equipo", "compañero"],
        "verb": ["comenzar", "disfrutar", "explorar", "lograr", "abrazar"],
        "preposition": ["con", "para", "en", "sobre", "a"],
        "action": ["abriendo", "iniciando", "lanzando", "iniciando"],
        "sentence": [
            "#time_greeting#, #adjective# #noun#!",
            "#time_greeting#, ¿cómo estás #adverb#?",
            "#action# tu solicitud, #adjective# #noun#!",
            "#verb# tu día #preposition# alegría, #adjective# #noun#!",
            "#verb# el viaje #preposition# #adjective# #noun#."
        ]
    }
};

let detectedLang = "en";

function getTimeGreeting(lang = detectedLang) {
    const hour = new Date().getHours();
    let timeGreeting = "";
    
    if (lang === "en") {
        if (hour >= 5 && hour < 12) timeGreeting = grammar.en.morning_greeting[Math.floor(Math.random() * grammar.en.morning_greeting.length)];
        else if (hour >= 12 && hour < 17) timeGreeting = grammar.en.afternoon_greeting[Math.floor(Math.random() * grammar.en.afternoon_greeting.length)];
        else if (hour >= 17 && hour < 21) timeGreeting = grammar.en.evening_greeting[Math.floor(Math.random() * grammar.en.evening_greeting.length)];
        else timeGreeting = grammar.en.night_greeting[Math.floor(Math.random() * grammar.en.night_greeting.length)];
    } else {
        if (hour >= 5 && hour < 12) timeGreeting = grammar.es.morning_greeting[Math.floor(Math.random() * grammar.es.morning_greeting.length)];
        else if (hour >= 12 && hour < 17) timeGreeting = grammar.es.afternoon_greeting[Math.floor(Math.random() * grammar.es.afternoon_greeting.length)];
        else if (hour >= 17 && hour < 21) timeGreeting = grammar.es.evening_greeting[Math.floor(Math.random() * grammar.es.evening_greeting.length)];
        else timeGreeting = grammar.es.night_greeting[Math.floor(Math.random() * grammar.es.night_greeting.length)];
    }
    
    return timeGreeting;
}

function generateText(rule, lang = detectedLang) {
    const g = grammar[lang] || grammar.en;
    let text = rule;
    
    const placeholders = text.match(/#\w+#/g) || [];
    for (const placeholder of placeholders) {
        const key = placeholder.replace(/#/g, '');
        const words = g[key] || ["unknown"];
        text = text.replace(placeholder, words[Math.floor(Math.random() * words.length)]);
    }
    
    return text;
}

function chatbotResponse(input, lang = detectedLang) {
    if (!input) return generateText("#time_greeting#, #adjective# #noun#!", lang);
    
    input = input.toLowerCase();
    
    // Detect language
    const spanishWords = ['hola', 'buenos', 'dias', 'como', 'estas', 'gracias', 'adios'];
    const englishWords = ['hello', 'how', 'are', 'thanks', 'good', 'morning'];
    
    let spanishCount = spanishWords.filter(w => input.includes(w)).length;
    let englishCount = englishWords.filter(w => input.includes(w)).length;
    
    if (spanishCount > englishCount) lang = "es";
    else lang = "en";
    
    detectedLang = lang;
    
    // Simple response logic
    if (input.includes('hello') || input.includes('hi') || input.includes('hola')) {
        return generateText("#time_greeting#, #adjective# #noun#!", lang);
    }
    
    if (input.includes('how are') || input.includes('como estas')) {
        return generateText("#time_greeting#, how are you doing #adverb#?", lang);
    }
    
    if (input.includes('thank') || input.includes('gracias')) {
        return generateText("#action# your request, #adjective# #noun#!", lang);
    }
    
    // Default response
    return generateText("#verb# your day #preposition# joy, #adjective# #noun#!", lang);
}

function appendToGrammar(category, word, lang = detectedLang) {
    if (!grammar[lang]) grammar[lang] = {};
    if (!grammar[lang][category]) grammar[lang][category] = [];
    grammar[lang][category].push(word);
}

function init(options = {}) {
    if (options.grammar) {
        Object.assign(grammar, options.grammar);
    }
    return {
        chatbotResponse,
        generateText,
        getTimeGreeting,
        appendToGrammar,
        grammar
    };
}

module.exports = { init, chatbotResponse, generateText, getTimeGreeting, appendToGrammar };
