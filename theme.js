// theme.js
function applyDynamicTheme() {
    const lat = 38.431702;
    const lng = -78.862391;
    const now = new Date();
    const times = SunCalc.getTimes(now, lat, lng)
    const sunsetTime = times.sunset;
    const sunriseTime = times.sunrise;
    const isNight = now >= sunsetTime || now < sunriseTime;
    //console.log("Sunrise = ", sunriseTime, "\nSunset = ", sunsetTime);
    //isNight = true

    if (isNight) {
        document.documentElement.setAttribute('data-theme', 'dark');
        console.log("🌙 Night mode active");
    } else {
        document.documentElement.removeAttribute('data-theme');
        console.log("☀️ Day mode active");
    }
}

// Run immediately and check every minute
applyDynamicTheme();
setInterval(applyDynamicTheme, 60000);