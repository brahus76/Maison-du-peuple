const ctx = document.getElementById('activityChart');

new Chart(ctx, {
    type: 'bar',
    data: {
        labels: ['Tickets', 'Réservations'],
        datasets: [
                {
                    label: 'Événements disponibles',
                    data: [window.totalEvenements, window.totalEvenements],
                    backgroundColor: '#dee2e6',
                    order: 0
                },
                {
                    label: 'Tickets achetés',
                    data: [window.totalTickets, 0],
                    backgroundColor: '#0d6efd',
                    order: 1
                },
                {
                    label: 'Réservations',
                    data: [0, window.totalReservations],
                    backgroundColor: '#198754',
                    order: 1
                }

        ]
    },
    options: {
        responsive: true,
        plugins: {
            legend: {
                position: 'top'
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                max: Math.max(
                    window.totalEvenements,
                    window.totalTickets,
                    window.totalReservations
                )
            }
        }
    }
});








// const ctx = document.getElementById('activityChart').getContext('2d');

// new Chart(ctx, {
//     type: 'bar',
//     data: {
//         labels: ['Tickets achetés'],
//         datasets: [
//             {
//                 label: 'Tickets achetés',
//                 data: [window.totalTickets],
//                 backgroundColor: '#0d6efd'
//             },
//             {
//                 label: 'Événements disponibles',
//                 data: [window.totalEvenements],
//                 backgroundColor: '#e9ecef'
//             }
//         ]
//     },
//     options: {
//         responsive: true,
//         scales: {
//             y: {
//                 beginAtZero: true,
//                 max: window.totalEvenements,
//                 ticks: {
//                     stepSize: 1
//                 }
//             }
//         }
//     }
// });



// document.addEventListener("DOMContentLoaded", function () {
//     const ctx = document.getElementById("activityChart");

//     if (!ctx) return;

//     new Chart(ctx, {
//         type: "bar",
//         data: {
//             labels: ["Tickets", "Réservations"],
//             datasets: [{
//                 label: "Activité du mois",
//                 data: [
//                     window.totalTickets,
//                     window.totalReservations
//                 ],
//                 backgroundColor: ["#0d6efd", "#198754"]
//             }]
//         },
//         options: {
//             responsive: true,
//             plugins: {
//                 legend: {
//                     display: false
//                 }
//             }
//         }
//     });
// });

