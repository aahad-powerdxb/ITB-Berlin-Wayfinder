/**
 * Groups array items alphabetically by their title
 * @param {Array} items - Array of items with title property
 * @returns {Object} Dictionary with letter keys mapping to arrays of items
 */
export function groupItemsAlphabetically(items) {
    // Helper to strip HTML tags for clean sorting
    const stripHtml = (str) => str.replace(/<[^>]*>/g, '').trim();

    // Sort items alphabetically by title
    const sortedItems = [...items].sort((a, b) => {
        const titleA = stripHtml(a.title).toLowerCase();
        const titleB = stripHtml(b.title).toLowerCase();
        return titleA.localeCompare(titleB);
    });

    // Group by first letter
    const grouped = sortedItems.reduce((acc, item) => {
        // Get first letter, default to '#' for non-letter starts
        const firstLetter = stripHtml(item.title).charAt(0).toUpperCase();
        const letter = /[A-Z]/i.test(firstLetter) ? firstLetter : '#';
        
        // Create array for this letter if it doesn't exist
        if (!acc[letter]) {
            acc[letter] = [];
        }
        
        // Add item to its letter group
        acc[letter].push(item);
        
        return acc;
    }, {});

    return grouped;
}