function loadTable(tableName) {
    fetch(`/table/${tableName}`)
    .then(response => response.json())
    .then(data => {
        let tableDataDiv = document.getElementById('table-data');
        let html = `<div class="name-block">Table: ${tableName}</div><table class=""><thead><tr><th>Name</th><th>Action</th></tr></thead><tbody>`;

        data.forEach(record => {
            console.log('Processing record:', record);
            let id = record[0];
            let name = record[1];
            let value = record[2];
            if (id !== undefined) {
                html += `<tr class="lesson"><td>${name}</td><td><button id="button-${id}" onclick="updateValue('${tableName}', '${id}')">${value}</button></td></tr>`;
            } else {
                console.error('ID is undefined in record:', record);
            }
        });

        html += `</tbody></table>`;
        tableDataDiv.innerHTML = html;
    })
    .catch(error => {
        console.error('Error fetching table data:', error);
    });
}

function updateValue(tableName, id) {
    fetch('/update', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ table_name: tableName, id: id })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            document.getElementById(`button-${id}`).innerText = data.new_value;
        } else {
            alert('Failed to update value.');
        }
    })
    .catch(error => {
        console.error('Error updating value:', error);
    });
}
