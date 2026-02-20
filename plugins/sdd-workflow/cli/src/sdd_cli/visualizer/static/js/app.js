// Global variables
let nodeMetadata = {};
let nodeMetadata1 = {};
let nodeMetadata2 = {};
let currentZoom = 1.0;
let currentZoom1 = 1.0;
let currentZoom2 = 1.0;
const zoomStep = 0.2;
const minZoom = 0.3;
const maxZoom = 4.0;

// Current active tab
let activeTab = 'single';
let splitDataLoaded = false;
let singleDataLoaded = false;

// Mermaid generation functions
const FILE_TYPE_COLORS = {
    "requirement": "#bbf",
    "spec": "#bfb",
    "design": "#bff",
    "task": "#ffb"
};

const EDGE_STYLES = {
    "explicit": "-->",
    "implicit": "-.->",
    "link": "-->"
};

function sanitizeNodeId(path) {
    return path.replace(/[^a-zA-Z0-9_]/g, "_");
}

function generateMermaidCode(graphData) {
    const lines = [];
    lines.push("graph TD");
    lines.push("");

    const nodes = graphData.nodes || [];
    const edges = graphData.edges || [];

    // Handle empty graph
    if (nodes.length === 0) {
        lines.push("    EMPTY[No documents found]");
        lines.push("    style EMPTY fill:#f0f0f0,stroke:#999,stroke-dasharray: 5 5");
        return lines.join("\n");
    }

    // Check if CONSTITUTION exists
    const hasConstitution = nodes.some(node => node.id === "CONSTITUTION.md");
    if (!hasConstitution && nodes.length > 0) {
        lines.push("    CONSTITUTION[CONSTITUTION.md]");
        lines.push("");
    }

    // Generate node definitions
    for (const node of nodes) {
        const nodeId = sanitizeNodeId(node.id);
        const title = (node.title || node.id).replace(/"/g, '\\"');
        lines.push(`    ${nodeId}["${title}"]`);
    }

    lines.push("");

    // Generate edges
    const edgesAdded = new Set();
    for (const edge of edges) {
        const sourceId = sanitizeNodeId(edge.source);
        const targetId = sanitizeNodeId(edge.target);
        const edgeStyle = EDGE_STYLES[edge.type] || "-->";
        const edgeDef = `${sourceId} ${edgeStyle} ${targetId}`;
        if (!edgesAdded.has(edgeDef)) {
            lines.push(`    ${edgeDef}`);
            edgesAdded.add(edgeDef);
        }
    }

    // Add implicit edges from CONSTITUTION if not filtered
    if (!hasConstitution && nodes.length > 0) {
        // Collect nodes that already have an incoming edge (they have a parent in the graph)
        const nodesWithIncomingEdge = new Set();
        for (const edge of edges) {
            nodesWithIncomingEdge.add(edge.target);
        }

        // CONSTITUTION → top-level requirements (not nested under another requirement)
        const requirementNodes = nodes.filter(node => node.file_type === "requirement");
        for (const node of requirementNodes) {
            if (nodesWithIncomingEdge.has(node.id)) continue;
            const nodeId = sanitizeNodeId(node.id);
            const edgeDef = `CONSTITUTION -.-> ${nodeId}`;
            if (!edgesAdded.has(edgeDef)) {
                lines.push(`    ${edgeDef}`);
                edgesAdded.add(edgeDef);
            }
        }

        // CONSTITUTION → spec (for specs without a corresponding requirement)
        const requirementFeatureIds = new Set(requirementNodes.map(n => n.feature_id).filter(Boolean));
        const specNodes = nodes.filter(node => node.file_type === "spec");
        for (const node of specNodes) {
            if (nodesWithIncomingEdge.has(node.id)) continue;
            if (!requirementFeatureIds.has(node.feature_id)) {
                const nodeId = sanitizeNodeId(node.id);
                const edgeDef = `CONSTITUTION -.-> ${nodeId}`;
                if (!edgesAdded.has(edgeDef)) {
                    lines.push(`    ${edgeDef}`);
                    edgesAdded.add(edgeDef);
                }
            }
        }
    }

    lines.push("");

    // Generate styles
    for (const node of nodes) {
        const nodeId = sanitizeNodeId(node.id);
        let color;
        if (node.id === "CONSTITUTION.md") {
            color = "#f9f";
        } else {
            color = FILE_TYPE_COLORS[node.file_type] || "#ddd";
        }
        lines.push(`    style ${nodeId} fill:${color},stroke:#333`);
    }

    // Add CONSTITUTION style
    if (!hasConstitution && nodes.length > 0) {
        lines.push("    style CONSTITUTION fill:#f9f,stroke:#333");
    }

    return lines.join("\n");
}

// Initialize Mermaid
mermaid.initialize({
    startOnLoad: false,
    theme: 'default',
    themeVariables: {
        fontSize: '16px',
        fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
    },
    flowchart: {
        nodeSpacing: 80,
        rankSpacing: 100,
        padding: 20
    }
});

// Tab switching
function switchTab(tabName) {
    // Update tab buttons
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

    // Update tab content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(`tab-${tabName}`).classList.add('active');

    activeTab = tabName;

    // Load data if not loaded yet
    if (tabName === 'single' && !singleDataLoaded) {
        loadSingleData();
    } else if (tabName === 'split' && !splitDataLoaded) {
        loadSplitData();
    }

    // Update header based on active tab
    if (tabName === 'single') {
        document.getElementById('graph-title').textContent = 'SDD Dependency Graph';
        document.getElementById('graph-subtitle').textContent = 'Interactive dependency graph visualization';
    } else {
        document.getElementById('graph-title').textContent = 'SDD Dependency Graph (Split View)';
        document.getElementById('graph-subtitle').textContent = 'PRD-based and Direct documents';
    }

    // Update zoom display
    updateZoom();
}

// Setup tab click handlers
document.querySelectorAll('.tab-button').forEach(button => {
    button.addEventListener('click', () => {
        const tabName = button.dataset.tab;
        switchTab(tabName);
    });
});

// Single graph mode
async function loadSingleData() {
    try {
        const graphResponse = await fetch('/dependency-graph.json');
        if (!graphResponse.ok) {
            throw new Error(`Failed to load graph: ${graphResponse.status}`);
        }
        const graphData = await graphResponse.json();

        // Set title
        document.getElementById('graph-title').textContent = graphData.title || 'SDD Dependency Graph';
        document.getElementById('graph-subtitle').textContent = graphData.subtitle || 'Interactive dependency graph visualization';
        document.getElementById('single-title').textContent = graphData.title || 'SDD Dependency Graph';

        // Build node metadata
        nodeMetadata = {};
        for (const node of graphData.nodes) {
            const nodeId = sanitizeNodeId(node.id);
            nodeMetadata[nodeId] = {
                title: node.title,
                path: node.id,
                directory: node.directory,
                featureId: node.feature_id || 'N/A'
            };
        }

        // Build parent relationships from SDD hierarchy
        buildParentMap(graphData, nodeMetadata);

        // Generate Mermaid code
        const mermaidCode = generateMermaidCode(graphData);

        // Render Mermaid diagram
        const diagramElement = document.getElementById('mermaid-diagram');
        diagramElement.textContent = mermaidCode;
        diagramElement.removeAttribute('data-processed');

        const { svg } = await mermaid.render('graphDiv', mermaidCode);
        diagramElement.innerHTML = svg;

        singleDataLoaded = true;

        // Post-load initialization
        initializeAfterLoad('mermaid-diagram', nodeMetadata);
    } catch (error) {
        console.error('Error loading data:', error);
        document.getElementById('mermaid-diagram').innerHTML =
            `<div class="error-message">Error loading diagram: ${error.message}</div>`;
        document.getElementById('graph-subtitle').textContent = 'Error loading data';
    }
}

// Split graph mode
async function loadSplitData() {
    try {
        // Set title
        document.getElementById('graph-title').textContent = 'SDD Dependency Graph (Split View)';
        document.getElementById('graph-subtitle').textContent = 'PRD-based and Direct documents';

        // Graph 1: PRD-based
        await loadGraph('prd-based-graph', 'mermaid-diagram-1', 1);

        // Graph 2: Direct
        await loadGraph('direct-graph', 'mermaid-diagram-2', 2);

        splitDataLoaded = true;

        // Update node count
        updateSplitNodeCount();
    } catch (error) {
        console.error('Error loading split data:', error);
        document.getElementById('graph-subtitle').textContent = 'Error loading data';
    }
}

// Load individual graph
async function loadGraph(dataName, elementId, graphIndex) {
    const graphResponse = await fetch(`/${dataName}.json`);
    const graphData = await graphResponse.json();

    // Build node metadata
    const metadata = {};
    for (const node of graphData.nodes) {
        const nodeId = sanitizeNodeId(node.id);
        metadata[nodeId] = {
            title: node.title,
            path: node.id,
            directory: node.directory,
            featureId: node.feature_id || 'N/A'
        };
    }

    // Build parent relationships from SDD hierarchy
    buildParentMap(graphData, metadata);

    // Save node metadata
    if (graphIndex === 1) {
        nodeMetadata1 = metadata;
    } else {
        nodeMetadata2 = metadata;
    }

    // Generate Mermaid code
    const mermaidCode = generateMermaidCode(graphData);

    // Render Mermaid diagram
    const diagramElement = document.getElementById(elementId);
    diagramElement.textContent = mermaidCode;
    diagramElement.removeAttribute('data-processed');

    const { svg } = await mermaid.render(`graphDiv${graphIndex}`, mermaidCode);
    diagramElement.innerHTML = svg;

    // Post-load initialization
    const nodeMetadataForGraph = graphIndex === 1 ? nodeMetadata1 : nodeMetadata2;
    initializeAfterLoad(elementId, nodeMetadataForGraph, graphIndex);
}

function updateSplitNodeCount() {
    const nodes1 = document.querySelectorAll('#mermaid-diagram-1 .node').length;
    const edges1 = document.querySelectorAll('#mermaid-diagram-1 .flowchart-link, #mermaid-diagram-1 path.edge').length;
    const nodes2 = document.querySelectorAll('#mermaid-diagram-2 .node').length;
    const edges2 = document.querySelectorAll('#mermaid-diagram-2 .flowchart-link, #mermaid-diagram-2 path.edge').length;

    document.getElementById('node-count').textContent =
        `PRD: ${nodes1} nodes, ${edges1} edges | Direct: ${nodes2} nodes, ${edges2} edges`;
}

function initializeAfterLoad(elementId, metadata, graphIndex) {
    setTimeout(() => {
        updateZoom(graphIndex);

        const nodes = document.querySelectorAll(`#${elementId} .node`);

        if (activeTab === 'single') {
            // Single mode: update node count
            const edges = document.querySelectorAll(`#${elementId} .flowchart-link, #${elementId} .edge-pattern, #${elementId} path.edge`);
            const edgeCount = edges.length > 0 ? edges.length : document.querySelectorAll(`#${elementId} marker`).length / 2;
            document.getElementById('node-count').textContent =
                `${nodes.length} nodes, ${Math.floor(edgeCount)} edges`;
        }

        // Add click handlers to nodes
        nodes.forEach((node) => {
            node.style.cursor = 'pointer';
            node.addEventListener('click', () => {
                let nodeId = node.id || 'unknown';

                if (nodeId.startsWith('flowchart-')) {
                    nodeId = nodeId.substring('flowchart-'.length);
                    nodeId = nodeId.replace(/-\d+$/, '');
                }

                console.log('Node clicked:', nodeId, 'Available metadata keys:', Object.keys(metadata));

                const nodeData = metadata[nodeId] || {
                    title: node.textContent,
                    path: 'N/A',
                    directory: 'N/A',
                    featureId: 'N/A'
                };
                showNodeDetail(nodeId, nodeData);
            });
        });
    }, 1000);
}

// Zoom functionality
function updateZoom(graphIndex) {
    if (activeTab === 'single') {
        const svg = document.querySelector('#mermaid-diagram svg');
        if (svg) {
            svg.style.transform = `scale(${currentZoom})`;
            svg.style.transformOrigin = 'top left';
        }
        document.getElementById('zoom-level').textContent = Math.round(currentZoom * 100) + '%';
    } else {
        const svg1 = document.querySelector('#mermaid-diagram-1 svg');
        const svg2 = document.querySelector('#mermaid-diagram-2 svg');
        if (svg1) {
            svg1.style.transform = `scale(${currentZoom1})`;
            svg1.style.transformOrigin = 'top left';
        }
        if (svg2) {
            svg2.style.transform = `scale(${currentZoom2})`;
            svg2.style.transformOrigin = 'top left';
        }
        document.getElementById('zoom-level').textContent =
            `PRD: ${Math.round(currentZoom1 * 100)}% | Direct: ${Math.round(currentZoom2 * 100)}%`;
    }
}

function zoomIn() {
    if (activeTab === 'single') {
        if (currentZoom < maxZoom) {
            currentZoom += zoomStep;
            updateZoom();
        }
    } else {
        if (currentZoom1 < maxZoom) currentZoom1 += zoomStep;
        if (currentZoom2 < maxZoom) currentZoom2 += zoomStep;
        updateZoom();
    }
}

function zoomOut() {
    if (activeTab === 'single') {
        if (currentZoom > minZoom) {
            currentZoom -= zoomStep;
            updateZoom();
        }
    } else {
        if (currentZoom1 > minZoom) currentZoom1 -= zoomStep;
        if (currentZoom2 > minZoom) currentZoom2 -= zoomStep;
        updateZoom();
    }
}

function resetZoom() {
    if (activeTab === 'single') {
        currentZoom = 1.0;
    } else {
        currentZoom1 = 1.0;
        currentZoom2 = 1.0;
    }
    updateZoom();
}

// Pan functionality
function setupPanZoom(containerId) {
    let isPanning = false;
    let startX, startY;
    let scrollLeft, scrollTop;

    const container = document.getElementById(containerId);
    if (!container) return;

    container.addEventListener('mousedown', (e) => {
        isPanning = true;
        startX = e.pageX - container.offsetLeft;
        startY = e.pageY - container.offsetTop;
        scrollLeft = container.scrollLeft;
        scrollTop = container.scrollTop;
    });

    container.addEventListener('mouseleave', () => {
        isPanning = false;
    });

    container.addEventListener('mouseup', () => {
        isPanning = false;
    });

    container.addEventListener('mousemove', (e) => {
        if (!isPanning) return;
        e.preventDefault();
        const x = e.pageX - container.offsetLeft;
        const y = e.pageY - container.offsetTop;
        const walkX = (x - startX) * 1.5;
        const walkY = (y - startY) * 1.5;
        container.scrollLeft = scrollLeft - walkX;
        container.scrollTop = scrollTop - walkY;
    });

    // Mouse wheel zoom
    container.addEventListener('wheel', (e) => {
        e.preventDefault();
        if (e.deltaY < 0) {
            zoomIn();
        } else {
            zoomOut();
        }
    });
}

// Setup pan/zoom for containers after page load
window.addEventListener('load', () => {
    setTimeout(() => {
        setupPanZoom('mermaid-diagram');
        setupPanZoom('mermaid-diagram-1');
        setupPanZoom('mermaid-diagram-2');
    }, 1500);
});

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    if (e.key === '+' || e.key === '=') {
        e.preventDefault();
        zoomIn();
    } else if (e.key === '-') {
        e.preventDefault();
        zoomOut();
    } else if (e.key === '0') {
        e.preventDefault();
        resetZoom();
    } else if (e.key === 'Escape') {
        closeNodeDetail();
    }
});

// Download functionality
function downloadSVG() {
    const svgElement = activeTab === 'single'
        ? document.querySelector('#mermaid-diagram svg')
        : document.querySelector('#mermaid-diagram-1 svg');
    if (!svgElement) {
        alert('Diagram not loaded yet');
        return;
    }

    const svgData = new XMLSerializer().serializeToString(svgElement);
    const blob = new Blob([svgData], { type: 'image/svg+xml' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'dependency-graph.svg';
    link.click();
    URL.revokeObjectURL(url);
}

function downloadPNG() {
    const svgElement = activeTab === 'single'
        ? document.querySelector('#mermaid-diagram svg')
        : document.querySelector('#mermaid-diagram-1 svg');
    if (!svgElement) {
        alert('Diagram not loaded yet');
        return;
    }

    const canvas = document.createElement('canvas');
    const bbox = svgElement.getBBox();
    canvas.width = bbox.width * 2;
    canvas.height = bbox.height * 2;

    const ctx = canvas.getContext('2d');
    ctx.scale(2, 2);

    const svgData = new XMLSerializer().serializeToString(svgElement);
    const img = new Image();
    const blob = new Blob([svgData], { type: 'image/svg+xml' });
    const url = URL.createObjectURL(blob);

    img.onload = () => {
        ctx.fillStyle = 'white';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(img, 0, 0);

        canvas.toBlob((pngBlob) => {
            const pngUrl = URL.createObjectURL(pngBlob);
            const link = document.createElement('a');
            link.href = pngUrl;
            link.download = 'dependency-graph.png';
            link.click();
            URL.revokeObjectURL(pngUrl);
            URL.revokeObjectURL(url);
        });
    };

    img.src = url;
}

// Resolve parent node from SDD hierarchy (file_type + path structure)
function buildParentMap(graphData, metadata) {
    const nodes = graphData.nodes || [];
    const requirementFeatureIds = new Set(
        nodes.filter(n => n.file_type === "requirement").map(n => n.feature_id).filter(Boolean)
    );

    for (const node of nodes) {
        const nodeId = sanitizeNodeId(node.id);
        if (!metadata[nodeId]) continue;

        const parent = findParentNode(node, nodes, requirementFeatureIds);
        if (parent) {
            metadata[nodeId].parent = parent.title || parent.id;
        }
    }
}

function findParentNode(node, allNodes, requirementFeatureIds) {
    const CONSTITUTION = { id: "CONSTITUTION.md", title: "CONSTITUTION.md" };

    if (node.file_type === "requirement") {
        // Nested requirement: parent is the index.md in the same directory
        const parts = node.id.split('/');
        if (parts.length > 2 && !node.id.endsWith('index.md')) {
            const parentDir = parts.slice(0, -1).join('/');
            const parentIndex = allNodes.find(n =>
                n.file_type === "requirement" &&
                n.id === parentDir + '/index.md'
            );
            if (parentIndex) return parentIndex;
        }
        return CONSTITUTION;
    }

    if (node.file_type === "spec") {
        // Parent is requirement with same feature_id, or CONSTITUTION
        const req = allNodes.find(n =>
            n.file_type === "requirement" && n.feature_id === node.feature_id
        );
        return req || CONSTITUTION;
    }

    if (node.file_type === "design") {
        // Parent is spec with same feature_id
        const spec = allNodes.find(n =>
            n.file_type === "spec" && n.feature_id === node.feature_id
        );
        return spec || null;
    }

    if (node.file_type === "task") {
        // Parent is design with same feature_id
        const design = allNodes.find(n =>
            n.file_type === "design" && n.feature_id === node.feature_id
        );
        return design || null;
    }

    return null;
}

// Node detail functionality
function showNodeDetail(nodeId, nodeData) {
    const parentHtml = nodeData.parent
        ? `<span class="parent-tag">${nodeData.parent}</span>`
        : 'N/A';

    const detailContent = document.getElementById('detail-content');
    detailContent.innerHTML = `
        <h2>${nodeData.title || nodeId}</h2>
        <div class="detail-item">
            <div class="detail-label">File Path</div>
            <div class="detail-value">${nodeData.path || 'N/A'}</div>
        </div>
        <div class="detail-item">
            <div class="detail-label">Directory</div>
            <div class="detail-value">${nodeData.directory || 'N/A'}</div>
        </div>
        <div class="detail-item">
            <div class="detail-label">Feature ID</div>
            <div class="detail-value">${nodeData.featureId || 'N/A'}</div>
        </div>
        <div class="detail-item">
            <div class="detail-label">Parent</div>
            <div class="detail-value">${parentHtml}</div>
        </div>
    `;
    document.getElementById('overlay').classList.add('active');
    document.getElementById('node-detail').classList.add('active');
}

function closeNodeDetail() {
    document.getElementById('overlay').classList.remove('active');
    document.getElementById('node-detail').classList.remove('active');
}

// Initialize on page load
async function init() {
    await loadSingleData();
}

window.addEventListener('load', init);
