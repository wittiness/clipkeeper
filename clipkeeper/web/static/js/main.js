document.addEventListener('DOMContentLoaded', () => {
    let searchTimeout;
    const searchInput = document.getElementById('search');

    const debounce = (func, wait) => {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    };

    const renderClipboardItem = (item) => {
        const time = new Date(item.timestamp).toLocaleTimeString([], { 
            hour: '2-digit', 
            minute: '2-digit' 
        });

        return `
            <div class="group bg-gray-900/50 rounded-lg border border-gray-800/50 overflow-hidden hover:border-gray-700/50 transition-all duration-300 hover:shadow-lg hover:shadow-black/20">
                <div class="content-area relative cursor-pointer shine-effect" onclick="copyItem(${item.id}, true)">
                    <div class="aspect-square">
                        ${item.content_type === 'image' 
                            ? `<img src="data:image/png;base64,${item.content}" class="w-full h-full object-cover" alt="Clipboard image">` 
                            : `<div class="h-full p-3 overflow-hidden">
                                <div class="clip-content overflow-hidden text-xs text-gray-400 font-mono">${escapeHtml(item.content)}</div>
                               </div>`
                        }
                    </div>
                    <div class="content-overlay absolute inset-0 flex flex-col items-center justify-center">
                        <div class="p-2 rounded-full bg-white/10 backdrop-blur-md mb-2 transform transition-transform duration-200 group-hover:scale-110">
                            <svg class="w-5 h-5 text-white/90" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-2M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2" />
                            </svg>
                        </div>
                        <div class="copy-feedback">
                            <span class="bg-white/10 rounded-full px-3 py-1.5 text-xs text-white/90 backdrop-blur-md border border-white/10">
                                Click to copy
                            </span>
                        </div>
                    </div>
                </div>
                <div class="px-3 py-2 bg-gray-900/80 flex items-center justify-between text-[10px] text-gray-500 border-t border-gray-800/50">
                    <span class="select-none">${time}</span>
                    <div class="flex gap-2">
                        <button onclick="copyItem(${item.id})" class="action-button hover:text-gray-300 transition-all p-1.5 hover:bg-gray-800/50 rounded-md" title="Copy">
                            <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-2M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2" />
                            </svg>
                        </button>
                        <button onclick="deleteItem(${item.id})" class="action-button hover:text-red-400 transition-all p-1.5 hover:bg-gray-800/50 rounded-md" title="Delete">
                            <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        </button>
                    </div>
                </div>
            </div>
        `;
    };

    const escapeHtml = (unsafe) => {
        if (!unsafe) return '';
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    };

    const updateHistoryWithLoading = async (searchTerm = '') => {
        const container = document.getElementById('history-container');
        
        if (searchTerm) {
            container.innerHTML = `
                <div class="col-span-full text-center py-12">
                    <div class="inline-block animate-spin mr-2">
                        <svg class="w-5 h-5 text-gray-500" fill="none" viewBox="0 0 24 24">
                            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                    </div>
                    <span class="text-sm text-gray-500">Searching...</span>
                </div>
            `;
        }

        try {
            const response = await fetch(`/api/history${searchTerm ? `?search=${encodeURIComponent(searchTerm)}` : ''}`);
            if (!response.ok) throw new Error('Failed to fetch clips');
            const data = await response.json();
            
            if (data.length === 0) {
                container.innerHTML = `
                    <div class="col-span-full text-center py-12">
                        <p class="text-sm text-gray-500">${searchTerm ? 'No matches found' : 'No clips yet'}</p>
                    </div>
                `;
            } else {
                container.innerHTML = data.map(renderClipboardItem).join('');
            }
        } catch (error) {
            console.error('Error:', error);
            container.innerHTML = `
                <div class="col-span-full text-center py-12">
                    <p class="text-sm text-red-400">Failed to load clips</p>
                </div>
            `;
        }
    };

    window.copyItem = async (id, isOverlay = false) => {
        const item = event.target.closest('.group');
        const button = isOverlay ? null : event.target.closest('button');
        const feedback = item.querySelector('.copy-feedback span');
        
        if (isOverlay) {
            feedback.textContent = 'Copying...';
            feedback.classList.remove('bg-green-500/20', 'text-green-300', 'bg-red-500/20', 'text-red-300');
        }

        if (button) {
            button.disabled = true;
            const originalHTML = button.innerHTML;
            button.innerHTML = `
                <svg class="w-3 h-3 animate-spin" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
            `;
        }

        try {
            const response = await fetch(`/api/copy/${id}`, { method: 'POST' });
            if (!response.ok) throw new Error('Failed to copy');
            
            item.classList.add('success-ring');
            setTimeout(() => item.classList.remove('success-ring'), 500);
            
            if (isOverlay) {
                feedback.textContent = 'Copied!';
                feedback.classList.add('bg-green-500/20', 'text-green-300');
                setTimeout(() => {
                    feedback.textContent = 'Click to copy';
                    feedback.classList.remove('bg-green-500/20', 'text-green-300');
                }, 1000);
            }
        } catch (error) {
            item.classList.add('error-shake');
            setTimeout(() => item.classList.remove('error-shake'), 400);
            
            if (isOverlay) {
                feedback.textContent = 'Failed to copy';
                feedback.classList.add('bg-red-500/20', 'text-red-300');
                setTimeout(() => {
                    feedback.textContent = 'Click to copy';
                    feedback.classList.remove('bg-red-500/20', 'text-red-300');
                }, 1000);
            }
        } finally {
            if (button) {
                setTimeout(() => {
                    button.disabled = false;
                    button.innerHTML = originalHTML;
                }, 1000);
            }
        }
    };

    window.deleteItem = async (id) => {
        const button = event.target.closest('button');
        const item = button.closest('.group');
        button.disabled = true;

        try {
            const response = await fetch(`/api/delete/${id}`, { method: 'DELETE' });
            if (!response.ok) throw new Error('Failed to delete');
            
            item.classList.add('delete-slide');
            setTimeout(() => {
                if (searchInput.value) {
                    updateHistoryWithLoading(searchInput.value);
                }
            }, 200);
        } catch (error) {
            button.disabled = false;
            item.classList.add('error-shake');
            setTimeout(() => item.classList.remove('error-shake'), 400);
        }
    };

    searchInput.addEventListener('input', (e) => {
        const debouncedSearch = debounce((searchTerm) => {
            updateHistoryWithLoading(searchTerm);
        }, 300);
        debouncedSearch(e.target.value);
    });

    const socket = io();

    socket.on('history_update', (data) => {
        if (!searchInput.value) {  // Only update if not searching
            const container = document.getElementById('history-container');
            container.innerHTML = data.map(renderClipboardItem).join('');
        }
    });

    updateHistoryWithLoading();
});