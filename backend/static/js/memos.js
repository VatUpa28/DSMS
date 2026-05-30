let clientData = null;

async function loadClient() {
  const code = document.getElementById("client_code").value;

  const res = await fetch(`/clients/by-code/${code}`);

  if (!res.ok) {
    alert("Client not found");
    return;
  }

  const data = await res.json();
  clientData = data;

  const c = data.client;

  document.getElementById("client_id").value = c.id;
  document.getElementById("client_name").value = c.name;
  document.getElementById("client_address").value = c.address;

  document.getElementById("ship_to_address").value = c.address;
}

function toggleShipping() {
  const checked = document.getElementById("alt_ship").checked;

  if (!checked && clientData) {
    document.getElementById("ship_to_address").value =
      clientData.client.address;
  }
}

function openShippingModal() {
  if (!clientData) {
    alert("Load client first");
    return;
  }

  const list = document.getElementById("shipping_list");
  list.innerHTML = "";

  clientData.shipping_addresses.forEach((a) => {
    const row = document.createElement("tr");

    row.innerHTML = `
            <td>${a.label || ""}</td>
            <td>${a.manager || ""}</td>
            <td>${a.address}</td>
            <td>
                <button class="btn btn-sm btn-primary"
                    onclick="selectShipping(${a.id})">
                    Select
                </button>
            </td>
        `;

    list.appendChild(row);
  });

  new bootstrap.Modal(document.getElementById("shippingModal")).show();
}

function selectShipping(id) {
  const a = clientData.shipping_addresses.find((x) => x.id === id);

  if (!a) return;

  document.getElementById("ship_to_address").value =
    `${a.address}, ${a.city || ""}, ${a.state || ""}, ${a.country || ""}`;

  bootstrap.Modal.getInstance(document.getElementById("shippingModal")).hide();
}
