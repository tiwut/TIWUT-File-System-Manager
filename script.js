const allModules = [];

function sanitizeModuleName(name) {
    return name.trim().replace(/\s/g, '_');
}

async function fetchCode(moduleName) {
    const filename = `${sanitizeModuleName(moduleName)}.txt`;
    try {
        const response = await fetch(filename);
        if (!response.ok) {
            return `// Error: Could not load code for ${moduleName}. Check if file ${filename} exists.`;
        }
        return await response.text();
    } catch (error) {
        console.error('Error fetching code:', error);
        return `// Error fetching file: ${filename}`;
    }
}

function createSnippetElement(module) {
    const item = document.createElement('div');
    item.className = 'snippet-item';
    item.setAttribute('data-name', module.name.toLowerCase());
    item.setAttribute('data-code', module.code.toLowerCase());

    const header = document.createElement('div');
    header.className = 'snippet-header';
    header.innerHTML = `
        <span class="snippet-title">${module.name.replace(/_/g, ' ')}</span>
        <span class="toggle-icon">▼</span>
    `;

    const content = document.createElement('div');
    content.className = 'snippet-content';

    const codeWrapper = document.createElement('div');
    codeWrapper.className = 'code-wrapper';

    const copyButton = document.createElement('button');
    copyButton.className = 'copy-button';
    copyButton.textContent = 'Copy Code';
    copyButton.addEventListener('click', (e) => copyCode(e, module.code));

    const pre = document.createElement('pre');
    const code = document.createElement('code');
    code.className = 'language-markup';
    code.textContent = module.code; 
    
    pre.appendChild(code);
    codeWrapper.appendChild(copyButton);
    codeWrapper.appendChild(pre);
    content.appendChild(codeWrapper);

    item.appendChild(header);
    item.appendChild(content);

    header.addEventListener('click', () => {
        item.classList.toggle('active');
        const contentDiv = item.querySelector('.snippet-content');
        if (item.classList.contains('active')) {
            contentDiv.style.maxHeight = contentDiv.scrollHeight + 80 + 'px';
        } else {
            contentDiv.style.maxHeight = '0';
        }

        Prism.highlightElement(code, false); 
    });

    return item;
}

function copyCode(event, code) {
    navigator.clipboard.writeText(code).then(() => {
        const button = event.target;
        const originalText = button.textContent;
        button.textContent = 'Copied!';
        setTimeout(() => {
            button.textContent = originalText;
        }, 1500);
    }).catch(err => {
        console.error('Could not copy text: ', err);
        alert('Failed to copy code!');
    });
}

async function loadModules() {
    const listElement = document.getElementById('snippetList');
    const loadingMessage = document.getElementById('loadingMessage');
    
    try {
        const namesResponse = await fetch('APP_ID.txt');
        if (!namesResponse.ok) {
            loadingMessage.textContent = 'Error: Could not load APP_ID.txt.';
            return;
        }
        const namesText = await namesResponse.text();
        const moduleNames = namesText.split('\n')
            .map(name => name.trim())
            .filter(name => name.length > 0);

        listElement.innerHTML = '';
        
        for (const name of moduleNames) {
            const code = await fetchCode(name);
            const module = { name, code };
            allModules.push(module);

            const element = createSnippetElement(module);
            listElement.appendChild(element);
        }

        if (allModules.length === 0) {
            listElement.innerHTML = '<p id="noResults">No code modules found in APP_ID.txt.</p>';
        }

    } catch (error) {
        console.error('Error loading modules:', error);
        listElement.innerHTML = '<p id="noResults">A critical error occurred while loading the data.</p>';
    }
}

function handleSearch(event) {
    const searchTerm = event.target.value.toLowerCase().trim();
    const listElement = document.getElementById('snippetList');
    let resultsFound = false;

    const existingNoResults = document.getElementById('noResults');
    if (existingNoResults) existingNoResults.remove();
    
    document.querySelectorAll('.snippet-item').forEach(item => {
        const moduleName = item.getAttribute('data-name');
        const moduleCode = item.getAttribute('data-code');
        
        if (moduleName.includes(searchTerm) || moduleCode.includes(searchTerm)) {
            item.style.display = 'block';
            resultsFound = true;
        } else {
            item.style.display = 'none';
        }
    });

    if (!resultsFound && allModules.length > 0) {
        const noResults = document.createElement('p');
        noResults.id = 'noResults';
        noResults.textContent = `No results found for "${searchTerm}".`;
        listElement.appendChild(noResults);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    loadModules();
    
    const searchInput = document.getElementById('searchInput');
    searchInput.addEventListener('input', handleSearch);
});
