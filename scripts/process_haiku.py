<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Word Cloud with Circular Modal</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.5/d3.min.js"></script>
    <style>
        body {
            margin: 0;
            padding: 20px;
            background-color: #f0f9ff;
            font-family: Arial, sans-serif;
        }
        
        #main-viz {
            width: 100%;
            height: 80vh;
        }
        
        .word-label {
            opacity: 0;
            transition: opacity 0.2s;
        }

        g:hover .word-label { 
            opacity: 1; 
        }

        /* Modal Styles */
        #modal-backdrop {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.75);
            z-index: 1000;
            justify-content: center;
            align-items: center;
        }

        #modal-container {
            background: white;
            border-radius: 50%;  /* Make it circular */
            width: 80vmin;
            height: 80vmin;
            max-width: 600px;
            max-height: 600px;
            position: relative;
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.2);
        }

        #close-modal {
            position: absolute;
            right: 10%;
            top: 10%;
            width: 32px;
            height: 32px;
            background: #f3f4f6;
            border: none;
            border-radius: 50%;
            cursor: pointer;
            font-size: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 1002;
        }

        #modal-word {
            position: absolute;
            top: 15%;
            left: 50%;
            transform: translateX(-50%);
            font-size: 24px;
            text-align: center;
            color: #1e40af;
        }

        #modal-word .count {
            display: block;
            font-size: 16px;
            color: #666;
            margin-top: 5px;
        }

        #modal-svg {
            width: 100%;
            height: 100%;
            position: absolute;
            top: 0;
            left: 0;
        }

        .haiku-circle {
            cursor: pointer;
            transition: all 0.2s;
        }

        .haiku-circle:hover {
            filter: brightness(1.2);
        }

        .tooltip {
            position: fixed;
            background: white;
            padding: 10px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
            pointer-events: none;
            opacity: 0;
            transition: opacity 0.2s;
            z-index: 1003;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div id="main-viz"></div>
    
    <!-- Modal Structure -->
    <div id="modal-backdrop">
        <div id="modal-container">
            <button id="close-modal">×</button>
            <div id="modal-word"></div>
            <svg id="modal-svg"></svg>
        </div>
    </div>
    
    <div class="tooltip"></div>

    <script>
        const width = window.innerWidth - 40;
        const height = window.innerHeight * 0.8;
        
        // Main visualization
        const svg = d3.select("#main-viz")
            .append("svg")
            .attr("width", width)
            .attr("height", height);

        // Modal and tooltip elements
        const modal = document.getElementById('modal-backdrop');
        const modalSvg = d3.select("#modal-svg");
        const tooltip = d3.select(".tooltip");
        
        // Close modal when clicking outside or on close button
        modal.addEventListener('click', (e) => {
            if (e.target === modal) modal.style.display = 'none';
        });
        
        document.getElementById('close-modal').addEventListener('click', () => {
            modal.style.display = 'none';
        });

        function showHaikuCloud(word, size, haikuIndices) {
            // Show modal
            modal.style.display = 'flex';
            
            // Set word and count
            document.getElementById('modal-word').innerHTML = `
                ${word}
                <span class="count">${size} occurrences</span>
            `;

            // Clear previous SVG content
            modalSvg.selectAll("*").remove();

            const modalSize = document.getElementById('modal-container').offsetWidth;
            const center = modalSize / 2;
            const radius = modalSize * 0.3; // Radius for haiku number placement
            
            // Calculate positions in a circle
            const angleStep = (2 * Math.PI) / haikuIndices.length;
            const haikuData = haikuIndices.map((index, i) => ({
                index,
                x: center + radius * Math.cos(i * angleStep - Math.PI/2),
                y: center + radius * Math.sin(i * angleStep - Math.PI/2)
            }));

            // Create haiku number circles
            const haikuGroups = modalSvg.selectAll("g")
                .data(haikuData)
                .join("g")
                .attr("transform", d => `translate(${d.x},${d.y})`);

            // Add circles
            haikuGroups.append("circle")
                .attr("class", "haiku-circle")
                .attr("r", modalSize * 0.05)
                .style("fill", d3.interpolateBlues(0.3))
                .on("mouseover", function(event, d) {
                    d3.select(this).style("fill", d3.interpolateBlues(0.6));
                    tooltip
                        .style("opacity", 1)
                        .html(`<strong>Haiku #${d.index}</strong>`)
                        .style("left", (event.pageX + 10) + "px")
                        .style("top", (event.pageY - 10) + "px");
                })
                .on("mousemove", function(event) {
                    tooltip
                        .style("left", (event.pageX + 10) + "px")
                        .style("top", (event.pageY - 10) + "px");
                })
                .on("mouseout", function() {
                    d3.select(this).style("fill", d3.interpolateBlues(0.3));
                    tooltip.style("opacity", 0);
                });

            // Add number labels
            haikuGroups.append("text")
                .attr("text-anchor", "middle")
                .attr("dy", "0.35em")
                .style("font-size", "14px")
                .style("pointer-events", "none")
                .style("user-select", "none")
                .text(d => d.index);
        }

        // Load and create main visualization
        d3.json("haiku_word_cloud.json").then(data => {
            const root = {
                name: "words",
                children: data.map(d => ({
                    name: d.text,
                    value: d.size,
                    haiku_indices: d.haiku_indices
                }))
            };

            const pack = d3.pack()
                .size([width, height])
                .padding(3);

            const rootNode = d3.hierarchy(root)
                .sum(d => d.value)
                .sort((a, b) => b.value - a.value);

            const nodes = pack(rootNode).descendants().slice(1);

            const colorScale = d3.scaleSequential()
                .domain([0, d3.max(data, d => d.size)])
                .interpolator(d3.interpolateBlues);

            const circles = svg.selectAll("g")
                .data(nodes)
                .join("g")
                .attr("transform", d => `translate(${d.x},${d.y})`);

            circles.append("circle")
                .attr("r", d => d.r)
                .style("fill", d => colorScale(d.data.value))
                .style("cursor", "pointer")
                .on("click", (event, d) => {
                    showHaikuCloud(d.data.name, d.data.value, d.data.haiku_indices);
                });

            circles.append("text")
                .attr("class", "word-label")
                .attr("text-anchor", "middle")
                .attr("dy", "0.3em")
                .style("font-size", d => Math.min(d.r * 0.8, 16) + "px")
                .style("fill", d => d.data.value > d3.max(data, d => d.size) / 2 ? "white" : "black")
                .text(d => d.data.name);
        });
    </script>
</body>
</html>