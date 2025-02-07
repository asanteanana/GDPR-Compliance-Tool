// JavaScript for Progress Bar
function updateProgressBar(percent) {
    let progressBar = document.getElementById("progressBar");
    let progressContainer = document.getElementById("progressContainer");

    // Show the progress bar container when scan starts
    if (percent > 0) {
        progressContainer.style.display = "block";
    }

    progressBar.style.width = percent + "%";
    progressBar.setAttribute("aria-valuenow", percent);
}

document.getElementById("gdprForm").addEventListener("submit", async function(event) {
    event.preventDefault();
    const url = document.getElementById("websiteUrl").value;

    // Start Progress Bar and show it
    updateProgressBar(20);

    const response = await fetch("/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url })
    });

    // Update Progress Bar (increased progress)
    updateProgressBar(70);

    const data = await response.json();
    const resultsContainer = document.getElementById("results-container");
    const resultsTable = document.getElementById("results");

    resultsTable.innerHTML = `
        <tr><td>Website URL</td><td>${data["Website URL"]}</td></tr>
        <tr><td>HTTPS Enabled</td><td>${data["HTTPS Enabled"] ? "✅ Yes" : "❌ No"}</td></tr>
        <tr><td>Privacy Policy Found</td><td>${data["Privacy Policy Found"] ? "✅ Yes" : "❌ No"}</td></tr>
        <tr><td>Cookie Banner Detected</td><td>${data["Cookie Banner Detected"] ? "✅ Yes" : "❌ No"}</td></tr>
        <tr><td>Terms & Conditions Found</td><td>${data["Terms & Conditions Page Found"] ? "✅ Yes" : "❌ No"}</td></tr>
        <tr><td>Contact Page Found</td><td>${data["Contact Page Found"] ? "✅ Yes" : "❌ No"}</td></tr>
        <tr><td>Uses Cookies</td><td>${data["Uses Cookies"] ? "✅ Yes" : "❌ No"}</td></tr>
        <tr><td><strong>Compliance Score</strong></td><td><strong>${data["Compliance Score"]}/100</strong></td></tr>
    `;

    // End Progress Bar and update to 100%
    updateProgressBar(100);

    resultsContainer.style.display = "block";
    document.getElementById("downloadReport").style.display = "block";

    document.getElementById("downloadReport").onclick = async function() {
        const reportResponse = await fetch("/download-report", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        });

        const blob = await reportResponse.blob();
        const link = document.createElement("a");
        link.href = window.URL.createObjectURL(blob);
        link.download = `GDPR_Compliance_Report_${data["Scan Date"].replace(/:/g, "-")}.pdf`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };
});
