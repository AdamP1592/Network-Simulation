export class queue {
    constructor() {
        this.items = [];
        this.length = 0; // Initialize length property
    }

    /**
     * Adds an element to the back of the queue.
     * @param {*} element - The element to add.
     */
    enqueue(element) {
        this.items.push(element);
        // Update the length to match the items array.
        this.length = this.items.length;
    }

    /**
     * Removes and returns the front element of the queue.
     * @returns {*} The removed element, or null if the queue is empty.
     */
    dequeue() {
        if (this.isEmpty()) {
            console.warn("Underflow: Queue is empty.");
            return null;
        }
        const elem = this.items.shift();
        // Update the length to match the items array.
        this.length = this.items.length;
        return elem;
    }

    /**
     * Returns the front element of the queue without removing it.
     * @returns {*} The front element, or null if the queue is empty.
     */
    peek() {
        if (this.isEmpty()) {
            console.warn("Empty Queue");
            return null;
        }
        return this.items[0];
    }

    /**
     * Returns the element at the specified index.
     * @param {number} index - The index of the element.
     * @returns {*} The element at the index, or undefined if out of range.
     */
    get(index) {
        if (index < 0 || index >= this.items.length) {
            console.warn("Index out of range");
            return undefined;
        }
        return this.items[index];
    }

    /**
     * Checks if the queue is empty.
     * @returns {boolean} True if the queue is empty, false otherwise.
     */
    isEmpty() {
        return this.items.length === 0;
    }

    /**
     * Returns a string representation of the queue.
     * @returns {string} A string representing the queue.
     */
    toString() {
        return String(this.items);
    }
}
