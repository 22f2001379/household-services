// src/utils/localStorage.js

/**
 * Set an item in Local Storage
 * @param {string} key - The key to store the value under
 * @param {any} value - The value to store (will be converted to JSON string)
 */
export function setLocalItem(key, value) {
    try {
        const serializedValue = JSON.stringify(value);
        localStorage.setItem(key, serializedValue);
    } catch (error) {
        console.error('Error setting item in Local Storage:', error);
    }
}

/**
 * Get an item from Local Storage
 * @param {string} key - The key to retrieve the value for
 * @returns {any} - The parsed value or null if not found/error
 */
export function getLocalItem(key) {
    try {
        const serializedValue = localStorage.getItem(key);
        if (serializedValue === null) return null;
        return JSON.parse(serializedValue);
    } catch (error) {
        console.error('Error getting item from Local Storage:', error);
        return null;
    }
}

/**
 * Remove an item from Local Storage
 * @param {string} key - The key of the item to remove
 */
export function removeLocalItem(key) {
    try {
        localStorage.removeItem(key);
    } catch (error) {
        console.error('Error removing item from Local Storage:', error);
    }
}

/**
 * Clear all items from Local Storage
 */
export function clearLocalStorage() {
    try {
        localStorage.clear();
    } catch (error) {
        console.error('Error clearing Local Storage:', error);
    }
}