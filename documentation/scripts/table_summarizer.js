// ==UserScript==
// @name         Scoreboard Service Status Summary per Column with Column Names
// @namespace    http://tampermonkey.net/
// @version      0.5
// @description  Summarize the status of services per column on the scoreboard page and replace the table with the summary
// @author       a_misc
// @match        http://localhost:5001/scoreboard
// ==/UserScript==

(function () {
    'use strict';

    // Function to summarize the service statuses per column and replace the table
    function summarizeAndReplaceTable() {
        // Select the table
        const table = document.querySelector('table.scoreboard');

        // get names
        let names = document.querySelector('thead').querySelectorAll('td');
        names = Array.from(names).map(x => x.innerText);
        names = names.slice(1, names.length);

        // Select all rows except the header
        let rows = table.querySelectorAll('tr.otherrow');
        rows = Array.from(rows).map(x => x.querySelectorAll('td'));
        rows = rows.map(x => Array.from(x).map(y => y.className));
        rows = rows.map(x => x.slice(3, x.length));
        console.log(rows);

        // Initialize an object to store the counts per service (column)
        let serviceCounts = {};

        for (let i = 0; i < names.length; i++) {
            serviceCounts[names[i]] = {
                OK: 0,
                MUMBLE: 0,
                INTERNAL_ERROR: 0,
                OFFLINE: 0
            };

            for (let j = 0; j < rows.length; j++) {
                if (rows[j][i].includes("service-OK")) {
                    serviceCounts[names[i]].OK++;
                } else if (rows[j][i].includes("service-MUMBLE")) {
                    serviceCounts[names[i]].MUMBLE++;
                } else if (rows[j][i].includes("service-INTERNAL_ERROR")) {
                    serviceCounts[names[i]].INTERNAL_ERROR++;
                } else if (rows[j][i].includes("service-OFFLINE")) {
                    serviceCounts[names[i]].OFFLINE++;
                }
            }
        }

        console.log(serviceCounts);

        const summaryTable = document.createElement('table');
        summaryTable.className = 'summary-table';
        summaryTable.style.width = '100%';
        summaryTable.style.borderCollapse = 'collapse';
        summaryTable.style.marginTop = '20px';
        summaryTable.style.fontFamily = 'Arial, sans-serif';

        // Create the header row
        const headerRow = document.createElement('tr');
        headerRow.style.backgroundColor = '#f2f2f2';
        headerRow.style.color = '#333';
        const headers = ['Service', 'OK', 'MUMBLE', 'INTERNAL ERROR', 'OFFLINE'];
        headers.forEach(headerText => {
            const headerCell = document.createElement('th');
            headerCell.textContent = headerText;
            headerCell.style.padding = '10px';
            headerCell.style.textAlign = 'center';
            headerCell.style.border = '1px solid #ddd';
            headerRow.appendChild(headerCell);
        });
        summaryTable.appendChild(headerRow);

        // Iterate over each service in serviceCounts
        Object.entries(serviceCounts).forEach(([serviceName, statusCounts]) => {
            const row = document.createElement('tr');

            // Service name cell
            const serviceNameCell = document.createElement('td');
            serviceNameCell.textContent = serviceName;
            serviceNameCell.style.padding = '10px';
            serviceNameCell.style.textAlign = 'center';
            serviceNameCell.style.border = '1px solid #ddd';
            row.appendChild(serviceNameCell);

            // Status cells
            const statusTypes = ['OK', 'MUMBLE', 'INTERNAL_ERROR', 'OFFLINE'];
            statusTypes.forEach(status => {
                const statusCell = document.createElement('td');
                statusCell.textContent = statusCounts[status];
                statusCell.style.padding = '10px';
                statusCell.style.textAlign = 'center';
                statusCell.style.border = '1px solid #ddd';
                row.appendChild(statusCell);
            });

            // Append row to table
            summaryTable.appendChild(row);
        });

        // Find the existing scoreboard table and replace it with the summary table
        console.log("existing table", table);
        console.log("summary table", summaryTable);
        console.log("replacing table");
        const existingTable = document.querySelector('table.summary-table');
        if (existingTable) {
            existingTable.parentNode.removeChild(existingTable);
        }
        table.parentNode.insertBefore(summaryTable, table);
        console.log("replaced table");

    }

    // Run the summary function when the page loads
    window.addEventListener('load', summarizeAndReplaceTable);

    // (Optional) Run the summary function when the page updates dynamically
    // Use MutationObserver if the page updates without a full reload
    const observer = new MutationObserver(summarizeAndReplaceTable);
    observer.observe(document.body, { childList: true, subtree: true });
})();
