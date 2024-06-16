// ==UserScript==
// @name         Scoreboard Service Status Summary per Column with Column Names
// @namespace    http://tampermonkey.net/
// @version      0.5
// @description  Summarize the status of services per column on the scoreboard page and replace the table with the summary
// @author       a_misc
// @match        http://localhost:5001/scoreboard*
// ==/UserScript==

(function () {
    'use strict';

    let initialized = false;
    let summaryTable; // Variable to hold the summary table

    // Function to summarize the service statuses per column and create the summary table
    function createSummaryTable() {
        // Select the table
        const table = document.querySelector('table.scoreboard');
        console.log(table);
        if (!table) return; // If the table is not found, return

        // get names
        let names = document.querySelector('thead').querySelectorAll('td');
        names = Array.from(names).map(x => x.innerText);
        names = names.slice(1, names.length);

        // Select all rows except the header
        let rows = table.querySelectorAll('tr.otherrow');
        rows = Array.from(rows).map(x => x.querySelectorAll('td'));
        rows = rows.map(x => Array.from(x).map(y => y.className));
        rows = rows.map(x => x.slice(3, x.length));

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

        // Create the summary table
        summaryTable = document.createElement('table');
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

        // Iterate over each service in serviceCounts and populate the summary table
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
        const existingSummaryTable = document.querySelector('.summary-table');
        if (existingSummaryTable) {
            existingSummaryTable.parentNode.removeChild(existingSummaryTable);
        }
        // Find the existing scoreboard table and insert the summary table before it
        table.parentNode.insertBefore(summaryTable, table);
    }

    // Function to update the summary table when changes are detected (e.g., scoreboard updates)
    function updateSummaryTable() {
        console.log('updateSummaryTable');

        // Call createSummaryTable to regenerate the summary table with updated data
        createSummaryTable();
    }
    const observer2 = new MutationObserver(updateSummaryTable);

    function initializeScript() {
        console.log('initializeScript');
        const t = document.querySelector('table.scoreboard');
        if (!t) return;
        console.log('initializeScript: table found');
        if (!initialized) {
            console.log('initializeScript: initializing');
            initialized = true;
            const node = document.querySelector('table.scoreboard');
            console.log("attached to node: ", node);
            observer2.observe(node, { childList: true, subtree: true });
            createSummaryTable();
        }
    }

    // Run the summary function when the page loads
    window.addEventListener('load', createSummaryTable);


    // Use MutationObserver to monitor changes in the DOM that indicate updates
    const observer = new MutationObserver(initializeScript);
    observer.observe(document.body, { childList: true, subtree: true });
})();
