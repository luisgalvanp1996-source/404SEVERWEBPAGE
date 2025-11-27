async function sendClientInfo() {
    const nav = navigator || {};

    const data = {
        userAgent: nav.userAgent || null,
        platform: nav.platform || null,
        language: nav.language || null,
        languages: nav.languages || null,
        vendor: nav.vendor || null,
        hardwareConcurrency: nav.hardwareConcurrency || null,
        maxTouchPoints: nav.maxTouchPoints || null,
        cookieEnabled: nav.cookieEnabled || null,
        doNotTrack: nav.doNotTrack || null,
        deviceMemory: nav.deviceMemory || null,

        screenWidth: screen.width,
        screenHeight: screen.height,
        screenAvailWidth: screen.availWidth,
        screenAvailHeight: screen.availHeight,
        screenColorDepth: screen.colorDepth,
        screenPixelDepth: screen.pixelDepth,

        viewportWidth: window.innerWidth,
        viewportHeight: window.innerHeight,

        devicePixelRatio: window.devicePixelRatio,

        orientationType: screen.orientation?.type || null,
        orientationAngle: screen.orientation?.angle || null,

        secChUA: nav.userAgentData?.brands || null,
        secChUAPlatform: nav.userAgentData?.platform || null,
        secChUAPlatformVersion: nav.userAgentData?.platformVersion || null,
        secChUAMobile: nav.userAgentData?.mobile || null,
        secChUAModel: nav.userAgentData?.model || null,

        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
        locale: navigator.language,

        effectiveConnectionType: navigator.connection?.effectiveType || null,
        downlink: navigator.connection?.downlink || null,
        rtt: navigator.connection?.rtt || null,
        saveData: navigator.connection?.saveData || null,

        referrer: document.referrer,
        pageURL: location.href
    };

    try {
        await fetch("/api/deviceinfo", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        });
        // console.log("Client info sent.");
    } catch (e) {
        console.error("Error sending client info:", e);
    }
}

// Ejecutar automáticamente al cargar la página
document.addEventListener("DOMContentLoaded", sendClientInfo);
