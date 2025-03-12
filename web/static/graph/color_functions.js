/**
 * Converts a color from HSB/HSV to RGB.
 * @param {number} h - Hue in degrees (0-360).
 * @param {number} s - Saturation (0-1).
 * @param {number} v - Value (0-1).
 * @returns {Array} An array [r, g, b] with each value in the range 0-255.
 */
function hsbToRgb(h, s, v) {
    let r, g, b;
    // Calculate chroma.
    const c = v * s;
    // Normalize hue to a sector of 60°.
    const hPrime = h / 60;
    // Calculate the intermediate value for RGB conversion.
    const x = c * (1 - Math.abs((hPrime % 2) - 1));
    const m = v - c;
    // Determine the RGB values based on which 60° segment h falls into.
    const sector = Math.floor(hPrime);
    switch (sector) {
        case 0:
            r = c; g = x; b = 0;
            break;
        case 1:
            r = x; g = c; b = 0;
            break;
        case 2:
            r = 0; g = c; b = x;
            break;
        case 3:
            r = 0; g = x; b = c;
            break;
        case 4:
            r = x; g = 0; b = c;
            break;
        case 5:
            r = c; g = 0; b = x;
            break;
        default:
            r = 0; g = 0; b = 0;
            break;
    }
    // Convert to 0-255 range.
    return [Math.floor((r + m) * 255), Math.floor((g + m) * 255), Math.floor((b + m) * 255)];
}

/**
 * Performs linear interpolation between two values.
 * @param {number} minOut - The output minimum.
 * @param {number} maxOut - The output maximum.
 * @param {number} minValue - The input minimum.
 * @param {number} maxValue - The input maximum.
 * @param {number} value - The input value.
 * @returns {number} The interpolated output value.
 */
export function interpolate(minOut, maxOut, minValue, maxValue, value) {
    return minOut + (((value - minValue) * (maxOut - minOut)) / (maxValue - minValue));
}

/**
 * Determines an RGB color based on an HSB color range.
 * Maps the input value (clamped between minVal and maxVal) to a hue between minH and maxH.
 * For values above maxVal+1, sets hue to 115 as an override.
 * @param {number} minH - Minimum hue.
 * @param {number} maxH - Maximum hue.
 * @param {number} minVal - Minimum value.
 * @param {number} maxVal - Maximum value.
 * @param {number} val - Current value.
 * @returns {Array} An array [r, g, b] representing the color.
 */
export function hsbColorRangeFinder(minH, maxH, minVal, maxVal, val) {
    // Clamp val to the [minVal, maxVal] range.
    let tempVal = Math.max(minVal, Math.min(val, maxVal));
    // Interpolate hue from the given value.
    let h = interpolate(minH, maxH, minVal, maxVal, tempVal);

    // Override hue if the value exceeds maxVal + 1.
    if (val > maxVal + 1) {
        h = 115;
    }

    const s = 1;
    const b = 1;
    const rgb = hsbToRgb(h, s, b);

    return rgb;
}

/**
 * Converts an RGB array to a CSS rgb() string.
 * @param {Array} rgbArray - Array in the form [r, g, b].
 * @returns {string} A CSS color string, e.g., "rgb(255, 0, 0)".
 */
export function rgbToCss(rgbArray) {
    return `rgb(${rgbArray[0]}, ${rgbArray[1]}, ${rgbArray[2]})`;
}
