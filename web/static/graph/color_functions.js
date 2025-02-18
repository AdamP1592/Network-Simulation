function hsbToRGB(h, s, b){
    const i = Math.floor(h * 6); //for rgb calc
    const f = h * 6 - i;
    const p = b * (1 - s);
    const q = b * (1 - f * s);
    const t = b * (1 - (1 - f) * s);
    
    //
    switch (i % 6) {
      case 0: r = b, g = t, b = p; break; //  0 <= h <= 60
      case 1: r = q, g = b, b = p; break; // (60, 120)
      case 2: r = p, g = b, b = t; break; // (120, 180)
      case 3: r = p, g = q, b = b; break; // (180, 240)
      case 4: r = t, g = p, b = b; break; // (240, 300)
      case 5: r = b, g = p, b = q; break; // (300, 360)
    }
    
    let rgb = [Math.round(r * 255), Math.round(g * 255), Math.round(b * 255)];
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
    let h = hueInterpolator(minH, maxH, minVal, maxVal, val);
    let s = 100;
    let b = 100;

    return hsbToRGB(h, s, b);
}

