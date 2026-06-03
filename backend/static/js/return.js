const scanned = [];

const input = document.getElementById("barcodeInput");

input.addEventListener("keydown", async (e) => {

    if (e.key !== "Enter")
        return;

    const stockNumber = input.value.trim();

    input.value = "";

    const response = await fetch(
        `/api/stone-by-stock/${stockNumber}`
    );

    const stone = await response.json();

    if (!stone.id)
        return;

    scanned.push(stone.id);

    document
        .getElementById("returnList")
        .insertAdjacentHTML(
            "beforeend",
            `
            <tr>
                <td>${stone.stock_number}</td>
                <td>${stone.status}</td>
            </tr>
            `
        );
});