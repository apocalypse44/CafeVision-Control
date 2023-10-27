
// // Your payment.js code
// document.addEventListener("DOMContentLoaded", function () {
//     // Get the coffeeType from the URL query parameters
//     const urlParams = new URLSearchParams(window.location.search);
//     const coffeeType = urlParams.get("coffeeType");

//     // Make an AJAX request to the server to get additional details
//     fetch(`/get_coffee_details?coffeeType=${coffeeType}`)
//         .then((response) => response.json())
//         .then((data) => {
//             // Now you can use the 'data' to access details related to the coffeeType
//             console.log(data);

//             // Example: Update the coffee details on the payment page
//             const coffeeName = document.getElementById("coffee-name");
//             coffeeName.textContent = data.name;
//         })
//         .catch((error) => {
//             console.error("Error fetching coffee details:", error);
//         });
// });





document.addEventListener("DOMContentLoaded", function () {
    // Get the coffeeType from the URL query parameters
    const urlParams = new URLSearchParams(window.location.search);
    const coffeeType = urlParams.get("coffeeType");

    // Create a Stripe instance with your publishable key
    
    var stripe = Stripe('pk_test_51O57hNSIvsFPoooMTlrFgxiONAuEr35izWS6vDb2OMfVJ8V6x8mFejgyTNP1gDawgSspELQQFW1eWrc4RKwyQXLJ00MCNXFedV'); // Replace with your Stripe publishable key
    console.log('S', stripe, coffeeType)
    // Create an instance of Elements
    var elements = stripe.elements();
    console.log('E', elements)
    // Create an instance of the card Element
    var card = elements.create('card');

    // Add an instance of the card Element into the `card-element` div
    card.mount('#card-element');

    // Handle form submission
    var form = document.getElementById('payment-form');
    form.addEventListener('submit', function (event) {
        event.preventDefault();

        // Disable the submit button to prevent multiple submissions
        document.getElementById('submit').disabled = true;

        // Create a PaymentMethod
        stripe
            .createPaymentMethod({
                type: 'card',
                card: card,
            })
            .then(function (result) {
                if (result.error) {
                    // Display error message to your user
                    var errorElement = document.getElementById('card-errors');
                    errorElement.textContent = result.error.message;

                    // Re-enable the submit button
                    document.getElementById('submit').disabled = false;
                } else {
                    // PaymentMethod was successfully created, proceed with payment
                    var coffeeType = document.getElementById('coffeeType').value;

                    // Make an AJAX request to your server to complete the payment
                    fetch('/charge', {
                        method: 'POST',
                        body: JSON.stringify({ coffeeType: coffeeType }),
                        headers: {
                            'Content-Type': 'application/json',
                        },
                    })
                        .then(function (response) {
                            return response.json();
                        })
                        .then(function (responseJson) {
                            if (responseJson.error) {
                                // Handle the error from your server
                                var errorElement = document.getElementById('card-errors');
                                errorElement.textContent = responseJson.error;

                                // Re-enable the submit button
                                document.getElementById('submit').disabled = false;
                            } else {
                                // The payment was successful
                                // You can redirect to a thank you page or perform other actions here
                                console.log('Payment successful:', responseJson);

                                // Example: Show a thank you message
                                var paymentFormContainer = document.getElementById('payment-form-container');
                                paymentFormContainer.innerHTML = '<h2>Thank you for your order!</h2>';
                            }
                        });
                }
            });
    });
});

