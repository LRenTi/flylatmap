var map;

function chooseAirline() {
    fetch('data/airlines.json')
    .then(response => response.json())
    .then(data => {
      const select = document.getElementById('airline-select');
      for (const airline of data.airlines) {
        const option = document.createElement('option');
        option.value = airline.id;
        option.text = airline.name;
        select.appendChild(option);
      }

      select.addEventListener('change', function() {
        console.log('Changing map to airline ID:', this.value);  // Debugging-Information hinzufügen
        createMap(this.value);
      });

      if (data.airlines.length > 0) {
        console.log('Creating initial map for airline ID:', data.airlines[0].id);  // Debugging-Information hinzufügen
        createMap(data.airlines[0].id);
      }
    });
}


function createMap(id) {
    $("#map").hide();
    $("#airline-picture").attr("src", "https://flylat.net/images/airlines/" + id + ".png")

    $.ajax({
        url: "data/Routes/" + id + ".json",
        type: 'GET',
        dataType: 'json',
        cache: false,
        success: function(response) {
            $("#map").show();

            routelist = response.routes;
            airlineName = response.name;
            airlineid = response.id;
            const timestamp = response.updateTimestamp * 1000;
            lastupdate = new Date(timestamp).toLocaleString();

            if (map !== undefined) {
                map.remove();
            }

            map = L.map('map', {
                zoomControl: false,
            }).setView([0, 0], 2);

            L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
                maxZoom: 19,
                attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
            }).addTo(map);

            L.control.zoom({position: 'topright'}).addTo(map);

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

            $("#airline-name").text(airlineName).css("font-weight", "bold");
            $("#airline-time").text(`Last update: ${lastupdate}`);
            $("#airline-link").attr("href", `https://flylat.net/company/${airlineid}`);
            console.log(countRoutes + " Routes added to the map.");
            $("#routecount").text(countRoutes + " Routes");
            if (countMissingRoutes > 0) {
                console.log(countMissingRoutes + " Routes could not be added to the map due to missing or invalid coordinates.");
            }
        },
        error: function(response) {
            $("#error").show();
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
