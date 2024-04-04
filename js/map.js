function createMap(id) {

    $("#map").hide();

    $.ajax({
        url: `https://api.github.com/repos/lrenti/flylatmap/contents/data/Routes/${id}.json`,
        type: 'GET',
        dataType: 'json',
        //headers: {"Authorization": "token" + ACCESS_TOKEN},
        cache: false,
        success: function(response) {
            $("#map").show();
            const content = atob(response.content);
            const data = JSON.parse(content);

            routelist = data.routes;
            airlineName = data.name;
            airlineid = data.id;
            const timestamp = data.updateTimestamp * 1000;
            lastupdate = new Date(timestamp).toLocaleString();
            $("#airline-name").append(`<b> ${airlineName}</b> `);
            $("#airline-time").append(`Last update: ${lastupdate}`);
            $("#airline-link").attr("href", `https://flylat.net/company/${airlineid}`);

            const airlineId = data.id || '';

            var map = L.map('map', {
            }).setView([0, 0], 2);

            L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
                maxZoom: 19,
                attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            }).addTo(map);
    
            let countRoutes = 0;
            let countMissingRoutes = 0;
    
            routelist.forEach(route => {
                const departureInfo = route.departure || {};
                const destinationInfo = route.destination || {};
    
                if (departureInfo.latitude && departureInfo.longitude && destinationInfo.latitude && destinationInfo.longitude) {
                    countRoutes++;
    
                    L.marker([departureInfo.latitude, departureInfo.longitude])
                        .bindPopup(`${departureInfo.name || 'Unknown'} (${departureInfo.ICAO || 'Unknown'})`)
                        .addTo(map);
                    
                    L.marker([destinationInfo.latitude, destinationInfo.longitude])
                        .bindPopup(`${destinationInfo.name || 'Unknown'} (${destinationInfo.ICAO || 'Unknown'})`)
                        .addTo(map);
    
                    L.polyline([
                        [departureInfo.latitude, departureInfo.longitude],
                        [destinationInfo.latitude, destinationInfo.longitude]
                    ], {color: 'lightblue'})
                    .bindTooltip(`(${departureInfo.ICAO || 'Unknown'}) - (${destinationInfo.ICAO || 'Unknown'})`)
                    .addTo(map);
                } else {
                    countMissingRoutes++;
                    console.log("Skipping route with missing or invalid coordinates");
                }
            });
    
            const filename = `${id}.html`;
            const folder = 'maps/';


            console.log(countRoutes + " Routes added to the map.");
            if (countMissingRoutes > 0) {
                console.log(countMissingRoutes + " Routes could not be added to the map due to missing or invalid coordinates.");
            }
        },
        error: function(response) {
            if (response.status === 403) {
                console.log("API rate limit exceeded. Please try again later.");
                $("#error").append("<p class=\"alert alert-danger\" role=\"alert\">API rate limit exceeded. Please try again later.</p>");
            }
            if (response.status === 401) {
                $("#error").append("<p class=\"alert alert-danger\" role=\"alert\">Unauthorized! Please check your GitHub Token</p>");
            }
            if (response.status === 404) {
                $("#error").append("<p class=\"alert alert-danger\" role=\"alert\">Airline not found!</p>");
            }
        }
    })   
}
// Example usage:
createMap(100172)
