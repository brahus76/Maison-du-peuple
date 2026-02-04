document.addEventListener("DOMContentLoaded", function () {
    const selectArtiste = document.getElementById("filtre-artiste");
    const events = document.querySelectorAll(".event-item");

    selectArtiste.addEventListener("change", function () {
        const artisteId = this.value;

        events.forEach(event => {
            const artistes = event.dataset.artistes.split(",");

            if (artisteId === "all" || artistes.includes(artisteId)) {
                event.style.display = "block";
            } else {
                event.style.display = "none";
            }
        });
    });
});
