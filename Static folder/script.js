document
    .getElementById("complaintForm")
    .addEventListener("submit", async function(event) {

        event.preventDefault();

        const data = {

            title: document.getElementById("title").value,

            description:
                document.getElementById("description").value,

            mode:
                document.getElementById("mode").value,

            location:
                document.getElementById("location").value
        };

        const response = await fetch("/submit", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify(data)

        });

        const result = await response.json();

        const box = document.getElementById("result");

        if (result.success) {

            box.innerHTML =
                `Issue submitted successfully.<br>
                 Complaint ID: #${result.id}<br>
                 Category: ${result.category}`;

            document.getElementById("complaintForm").reset();

        } else {

            box.innerHTML = result.message;

        }

    });


async function trackComplaint() {

    const id =
        document.getElementById("trackId").value;

    const response =
        await fetch("/complaints");

    const complaints =
        await response.json();

    const complaint =
        complaints.find(c => c.id == id);

    const box =
        document.getElementById("trackingResult");

    if (!complaint) {

        box.innerHTML =
            "Complaint not found.";

        return;
    }

    box.innerHTML = `
        <p><strong>Complaint:</strong> #${complaint.id}</p>
        <p><strong>Category:</strong> ${complaint.category}</p>
        <p><strong>Status:</strong> ${complaint.status}</p>
        <p><strong>Submitted:</strong> ${complaint.created_at}</p>
    `;
}
