function hsbToRgb(h, s, v){
    var r, g, b;

    var c = v * s;

    var hPrime = h/60;

    let hMod = Math.abs( (hPrime % 2) - 1 )
    var x = c * (1 - hMod)
    var m = v - c

    var value = Math.floor(h / 60);

    
    switch(value){
        case 0: r = c, g = x, b = 0; break;
        case 1: r = x, g = c, b = 0; break;
        case 2: r = 0, g = c, b = x; break;
        case 3: r = 0, g = x, b = c; break;
        case 4: r = x, g = 0, b = c; break;
        case 5: r = v, g = 0, b = q; break;
    }

    return [(r + m) * 255, (g + m) * 255, (b + m) * 255];
}




function hsvToRgb(h, s, v){
    var r, g, b;

    var i = Math.floor(h * 6);
    var f = h * 6 - i;
    var p = v * (1 - s);
    var q = v * (1 - f * s);
    var t = v * (1 - (1 - f) * s);

    switch(i % 6){
        case 0: r = v, g = t, b = p; break;
        case 1: r = q, g = v, b = p; break;
        case 2: r = p, g = v, b = t; break;
        case 3: r = p, g = q, b = v; break;
        case 4: r = t, g = p, b = v; break;
        case 5: r = v, g = p, b = q; break;
    }

    return [r * 255, g * 255, b * 255];
}

//for neurons min = 0, max = 70,

function hueInterpolator(minH, maxH, minValue, maxValue, value){
     // linear interpolation
    let h = minH + (((value - minValue) * (maxH - minH))/(maxValue - minValue));
    return h;
}

//returns rgb
//
export function hsbColorRangeFinder(minH, maxH, minVal, maxVal, val){
    //edge cases
    console.log(val)
    let tempVal = val
    if (val < minVal){ tempVal = minVal}
    if (val > maxVal){ tempVal = maxVal}
    let h = hueInterpolator(minH, maxH, minVal, maxVal, tempVal);;
    
    if (val > maxVal + 1){
        h = 115;
    }

    
    let s = 1;
    let b = 1;
    let rgb = hsbToRgb(h, s, b);

    console.log(rgb)

    return rgb
}

