// src/utils/sessionStorage.js

/**
 * Set an item in Session Storage
 * @param {string} key - The key to store the value under
 * @param {any} value - The value to store (will be converted to JSON string)
 */
export function setSessionItem(key, value) {
    try {
      const serializedValue = JSON.stringify(value);
      sessionStorage.setItem(key, serializedValue);
    } catch (error) {
      console.error('Error setting item in Session Storage:', error);
    }
  }
  
  /**
   * Get an item from Session Storage
   * @param {string} key - The key to retrieve the value for
   * @returns {any} - The parsed value or null if not found/error
   */
  export function getSessionItem(key) {
    try {
      const serializedValue = sessionStorage.getItem(key);
      if (serializedValue === null) return null;
      return JSON.parse(serializedValue);
    } catch (error) {
      console.error('Error getting item from Session Storage:', error);
      return null;
    }
  }
  
  /**
   * Remove an item from Session Storage
   * @param {string} key - The key of the item to remove
   */
  export function removeSessionItem(key) {
    try {
      sessionStorage.removeItem(key);
    } catch (error) {
      console.error('Error removing item from Session Storage:', error);
    }
  }
  
  /**
   * Clear all items from Session Storage
   */
  export function clearSessionStorage() {
    try {
      sessionStorage.clear();
    } catch (error) {
      console.error('Error clearing Session Storage:', error);
    }
  }