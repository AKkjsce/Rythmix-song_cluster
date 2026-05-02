// main.js
// handles all the interactivity on the Rythmix frontend
// written as plain vanilla JS, no frameworks, keeping it simple

// wait for the page to finish loading before doing anything
document.addEventListener("DOMContentLoaded", function() {

    // grab all the elements i'll be using throughout
    var navCharts   = document.getElementById("nav-charts");
    var navSearch   = document.getElementById("nav-search");
    var pageCharts  = document.getElementById("view-charts");
    var pageSearch  = document.getElementById("view-search");

    var tabSearchBtn    = document.getElementById("tab-search-btn");
    var tabClusterBtn   = document.getElementById("tab-cluster-btn");
    var clusterWrapper  = document.getElementById("tab-cluster-wrapper");
    var clusterMenu     = document.getElementById("cluster-dropdown-menu");
    var panelSearch     = document.getElementById("panel-search");
    var panelCluster    = document.getElementById("panel-cluster");

    var searchInput     = document.getElementById("search-box");
    var searchResults   = document.getElementById("results-area");

    var clusterPillBox  = document.getElementById("cluster-buttons");
    var clusterResults  = document.getElementById("cluster-results-area");

    var searchDelay;
    var activeClusterId = null;

    // ---- sidebar tab switching ----

    navCharts.addEventListener("click", function() {
        navCharts.classList.add("active");
        navSearch.classList.remove("active");
        pageCharts.classList.add("active");
        pageSearch.classList.remove("active");
    });

    navSearch.addEventListener("click", function() {
        navSearch.classList.add("active");
        navCharts.classList.remove("active");
        pageSearch.classList.add("active");
        pageCharts.classList.remove("active");

        if (clusterMenu.dataset.ready !== "true") {
            fetchAndBuildClusterMenu();
        }
    });


    // ---- discover sub-tabs (search vs browse by cluster) ----

    tabSearchBtn.addEventListener("click", function() {
        tabSearchBtn.classList.add("active");
        tabClusterBtn.classList.remove("active");
        panelSearch.classList.remove("hidden");
        panelCluster.classList.add("hidden");
        clusterMenu.classList.add("hidden");
    });

    tabClusterBtn.addEventListener("click", function(e) {
        e.stopPropagation();
        tabClusterBtn.classList.add("active");
        tabSearchBtn.classList.remove("active");
        panelCluster.classList.remove("hidden");
        panelSearch.classList.add("hidden");
        clusterMenu.classList.toggle("hidden");

        if (clusterMenu.dataset.ready !== "true") {
            fetchAndBuildClusterMenu();
        }
    });

    document.addEventListener("click", function() {
        clusterMenu.classList.add("hidden");
    });


    // ---- the song search bar ----
    searchInput.addEventListener("input", function() {
        var typed = searchInput.value.trim();

        // clear any pending search 
        clearTimeout(searchDelay);

        if (typed.length === 0) {
            if (tabSearchBtn.classList.contains("active")) {
                searchResults.innerHTML = "";
            } else {
                if (activeClusterId !== null) {
                    loadClusterTracks(activeClusterId);
                } else {
                    clusterResults.innerHTML = '<div class="empty-state">Pick a cluster from the dropdown above.</div>';
                }
            }
            return;
        }

        // wait 300ms, then search contextually
        searchDelay = setTimeout(function() {
            var isClusterMode = tabClusterBtn.classList.contains("active");
            var url = "/api/search?q=" + encodeURIComponent(typed);
            
            if (isClusterMode) {
                if (activeClusterId === null) {
                    clusterResults.innerHTML = '<div class="empty-state">Please select a cluster from the dropdown first to search within it.</div>';
                    return;
                }
                url += "&cluster=" + encodeURIComponent(activeClusterId);
            }

            var targetDiv = isClusterMode ? clusterResults : searchResults;
            targetDiv.innerHTML = '<div class="empty-state">Searching...</div>';

            fetch(url)
                .then(function(res) { return res.json(); })
                .then(function(songList) {
                    if (songList.length === 0) {
                        var msg = isClusterMode ? 'Nothing found in this cluster.' : 'Nothing found for "' + typed + '".';
                        targetDiv.innerHTML = '<div class="empty-state">' + msg + '</div>';
                        return;
                    }
                    targetDiv.innerHTML = buildTrackListHTML(songList, !isClusterMode);
                })
                .catch(function(err) {
                    console.log("search failed:", err);
                    targetDiv.innerHTML = '<div class="empty-state" style="color:#e74c3c">Something went wrong.</div>';
                });
        }, 300);
    });

    function loadClusterTracks(cid) {
        activeClusterId = cid;
        clusterResults.innerHTML = '<div class="empty-state">Fetching songs from Cluster ' + cid + '...</div>';

        fetch("/api/cluster/" + cid + "?limit=10")
            .then(function(r) { return r.json(); })
            .then(function(tracks) {
                if (tracks.length === 0) {
                    clusterResults.innerHTML = '<div class="empty-state">This cluster seems to be empty.</div>';
                    return;
                }
                clusterResults.innerHTML = buildTrackListHTML(tracks, false);
            })
            .catch(function(err) { console.log("cluster fetch failed:", err); });
    }


    // ---- similar songs feature ----
    // using event delegation here because the buttons are created dynamically
    // so i can't attach listeners to them directly when the page first loads

    searchResults.addEventListener("click", function(e) {
        if (!e.target.classList.contains("similar-btn")) return;

        var btn = e.target;
        var card = btn.closest(".track-item");
        var cluster = btn.dataset.cluster;
        var songName = btn.dataset.track;

        // toggle: if the panel is already there, just close it
        var alreadyOpen = card.querySelector(".similar-results");
        if (alreadyOpen) {
            alreadyOpen.remove();
            btn.textContent = "Discover Similar";
            return;
        }

        btn.textContent = "Loading...";

        // ask flask for 3 tracks from the same cluster, excluding the current song
        var url = "/api/cluster/" + cluster + "?limit=3&exclude=" + encodeURIComponent(songName);

        fetch(url)
            .then(function(res) { return res.json(); })
            .then(function(similar) {
                if (similar.length === 0) {
                    btn.textContent = "Nothing else here";
                    return;
                }

                // build a little list that slides in below the track card
                var block = '<div class="similar-results">';
                block += '<div class="similar-title">Tracks from the same cluster (sounds like this):</div>';

                for (var i = 0; i < similar.length; i++) {
                    var s = similar[i];
                    block += '<div class="similar-track">';
                    block += '<div class="s-title">' + s.track_name + '</div>';
                    block += '<div class="s-artist">' + s.artists + '</div>';
                    block += '</div>';
                }

                block += '</div>';
                card.insertAdjacentHTML("beforeend", block);
                btn.textContent = "Hide Similar";
            })
            .catch(function(err) {
                console.log("similar songs fetch failed:", err);
                btn.textContent = "Discover Similar";
            });
    });


    // ---- cluster dropdown inside the Browse by Cluster pill ----

    function fetchAndBuildClusterMenu() {
        fetch("/api/clusters")
            .then(function(res) { return res.json(); })
            .then(function(clusterList) {
                if (clusterList.length === 0) {
                    clusterMenu.innerHTML = '<div class="cdrop-empty">No clusters found.</div>';
                    clusterMenu.dataset.ready = "true";
                    return;
                }

                var html = "";
                for (var i = 0; i < clusterList.length; i++) {
                    var c = clusterList[i];
                    html += '<div class="cdrop-item" data-cid="' + c.cluster_id + '">';
                    html += 'Cluster ' + c.cluster_id;
                    html += ' <span class="cdrop-count">' + c.track_count.toLocaleString() + ' tracks</span>';
                    html += '</div>';
                }
                clusterMenu.innerHTML = html;
                clusterMenu.dataset.ready = "true";

                // handle item clicks
                clusterMenu.addEventListener("click", function(e) {
                    var item = e.target.closest(".cdrop-item");
                    if (!item) return;

                    // mark selected
                    clusterMenu.querySelectorAll(".cdrop-item").forEach(function(el) {
                        el.classList.remove("active");
                    });
                    item.classList.add("active");
                    clusterMenu.classList.add("hidden");  // close after picking

                    var cid = item.dataset.cid;
                    tabClusterBtn.childNodes[0].textContent = "Cluster " + cid + " ";
                    
                    // load the tracks using our new helper which also sets the active cluster
                    loadClusterTracks(cid);
                    
                    // clear the search box so we start fresh
                    searchInput.value = "";
                });
            })
            .catch(function(err) {
                clusterMenu.innerHTML = '<div class="cdrop-empty" style="color:#e74c3c">Failed to load clusters.</div>';
            });
    }

    // ---- shared helper: builds the track card HTML ----
    // showSimilar is a boolean — true when we want the "discover similar" button

    function buildTrackListHTML(tracks, showSimilar) {
        var output = '<div class="track-list">';

        for (var i = 0; i < tracks.length; i++) {
            var t = tracks[i];

            // only show genre if it's a real value (sometimes it's "nan" from pandas)
            var genreLabel = "";
            if (t.track_genre && t.track_genre !== "nan") {
                genreLabel = "Genre in dataset: " + t.track_genre;
            }

            // strip quotes from track name so they don't break the data attribute
            var safeName = t.track_name.replace(/"/g, "");

            var similarBtn = "";
            if (showSimilar) {
                similarBtn = '<button class="similar-btn" data-cluster="' + t.cluster + '" data-track="' + safeName + '">Discover Similar</button>';
            }

            output += '<div class="track-item">';
            output += '<div class="track-top-row">';
            output += '<div class="track-info">';
            output += '<div class="title">' + t.track_name + '</div>';
            output += '<div class="artist">' + t.artists + '</div>';
            output += '</div>';
            output += '<div class="track-meta">';
            output += '<div class="cluster-badge">Cluster ' + t.cluster + '</div>';
            output += '<span class="track-genre">' + genreLabel + '</span>';
            output += '</div>';
            output += '</div>';
            output += similarBtn;
            output += '</div>';
        }

        output += '</div>';
        return output;
    }

});
