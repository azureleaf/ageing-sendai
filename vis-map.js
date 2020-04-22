towns = stats.data;

// Mapping from field name to index number;
// this improves the accessibility to the towns data
//    by creating the shorthand for indices
// e.g. "fields.total_pop" returns "1"
//    because it's the 2nd element in stats.columns
fields = {};
stats.columns.forEach((column, index) => {
  fields[column] = index;
});

const renderMap = () => {
  // Instantiate Map object: set initial view position & zoom level
  var mymap = new L.Map("mapid").setView([38.2682, 140.8694], 14);

  // Set tile layer
  var tile = L.tileLayer("http://{s}.tile.osm.org/{z}/{x}/{y}.png", {
    attribution:
      '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors',
  }).addTo(mymap);

  // Convert color notation from RGB to HEX
  const rgbToHex = (r = 0, g = 0, b = 0) => {
    let reducer = (acc, curr) => {
      // When the input isn't number, reject it
      if (isNaN(Number(curr))) {
        console.error("Incorrect RGB input");
        return;
      }

      // When the number is too large or too small, limit it
      if (Number(curr) >= 255) curr = 255;
      if (Number(curr) <= 0) curr = 0;

      hex = Number(Math.round(curr)).toString(16);

      // Append "0" when the hex isn't 2-digit
      if (hex.length < 2) hex = "0" + hex;
      return acc.toString() + hex;
    };
    return [r, g, b].reduce(reducer, "");
  };

  const useRedCmap = (pc_value) => {
    return "#" + rgbToHex(255, (100 - pc_value) * 2.55, (100 - pc_value) * 255);
  };

  const useHSVCmap = (pc_value) => {
    // Cut-off for old population ratio
    // e.g. 81%, 85%, 90%, 100% will be shown in the identical color
    //     when the upper cutoff is 80%
    // Strictly speaking, setting cut-off isn't scientific, tho
    const [lowerCutoff, upperCutoff] = [0, 50]; // Set between 0-100%
    if (pc_value > upperCutoff) pc_value = upperCutoff;
    if (pc_value < lowerCutoff) pc_value = lowerCutoff;
    const [hueMin, hueMax] = [0, 240]; // Set between 0-360 (deg)
    const hue = (pc_value * (hueMax - hueMin)) / (upperCutoff - lowerCutoff);
    return "hsl(" + hue + ", 100%, 50%)";
  };

  const useJetCmap = (pc_value) => {
    const b = pc_value > 25 ? -10.2 * pc_value + 640 : 10.2 * pc_value + 128;
    const g = pc_value > 50 ? -10.2 * pc_value + 896 : 10.2 * pc_value - 128;
    const r = pc_value > 75 ? -10.2 * pc_value + 1148 : 10.2 * pc_value - 384;
    return "#" + rgbToHex(r, g, b);
  };

  const useHotishCmap = (pc_value) => {
    return "#" + rgbToHex(-5.1 * pc_value + 510, -5.1 * pc_value + 255, 0);
  };

  // Plot circles
  towns.forEach((town) => {
    // % of old age population
    pc_old = town[fields.pc_old];

    const cmapSchema = "hsv";
    let plotColor = undefined;

    // Colormap: RGB vs HSL vs Hot-ish
    switch (cmapSchema) {
      case "hsv":
        plotColor = useHSVCmap(pc_old);
        break;
      case "red":
        plotColor = useRedCmap(pc_old);
        break;
      case "hotish":
        plotColor = useHotishCmap(pc_old);
        break;
      case "jet":
        plotColor = useJetCmap(pc_old);
        break;
    }

    const circle = L.circle([town[fields.lat], town[fields.lon]], {
      color: "gray", // stroke color
      fillColor: plotColor,
      fillOpacity: 0.8,
      weight: 1, // stroke width
      radius: 100,
    }).addTo(mymap);

    circle.bindPopup(
      `<span style='font-size: 130%'>${town[fields.town_name]}</span><br>\
      <span style='font-size: 120%'>高齢人口比率：<b style='font-size: 250%;'>\
      ${Math.round(town[fields.pc_old])}</b> ％</span>\
      <p style='margin-top: 15px;'>\
      老年化指数　：${town[fields.ageing_index]}<br>\
      総人口　　　：${town[fields.total_pop]}人<br>\
      高齢人口　　：${town[fields.pop_old]}人<br>\
      生産年齢人口：${town[fields.pop_working]}人<br>\
      年少人口　　：${town[fields.pop_young]}人<br>\
      女性100人に対する男性数：${town[fields.gender_ratio]}人</p>`
    );
  });
};

renderMap();
