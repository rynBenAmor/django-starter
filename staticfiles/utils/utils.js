// utils.js

// Centralized export
export {
    // --- AJAX  ---
    loadPartial,
    fetchWithCSRF,

    // --- Form helpers ---
    formValidate,
    validateInputRegex,
    passwordStrengthRegex,
    togglePasswordVisibility,
    serializeForm,

    // --- Cookies ---
    getCookie,
    getCSRFToken,
    isCSRFTokenAvailable,

    // --- URL & Query Params ---
    getQueryParam,
    setQueryParam,
    removeQueryParam,
    getCurrentUrl,
    setCurrentUrl,

    // --- UI Helpers ---
    addFontAwesomeLoader,
    preserveScrollPos,
    scrollToTop,
    scrollToElementById,
    scrollToBottom,
    disableForm,
};



async function loadPartial(url, targetSelector) {
    const response = await fetchWithCSRF(url);
    const html = await response.text();
    const target = document.querySelector(targetSelector);
    if (target) target.innerHTML = html;
}


function disableForm(form, state = true) {
    [...form.elements].forEach(el => el.disabled = state);
}



function formValidate(form) {
    if (!form || !(form instanceof HTMLFormElement)) {
        console.error('Invalid form element provided for validation.');
        return false;
    }
    const inputs = form.querySelectorAll('input, select, textarea');

    function validateGenericInput(input) {
        if (input.checkValidity()) {
            input.classList.remove('is-invalid');
            input.classList.add('is-valid');
        } else {
            input.classList.remove('is-valid');
            input.classList.add('is-invalid');
        }
    }

    inputs.forEach(input => {
        input.addEventListener('input', function () {
            validateGenericInput(input);
        });
        input.addEventListener('blur', function () {
            input.dispatchEvent(new Event('input'));
        });
    });
}


function passwordStrengthRegex(password, regex) {
    /** can be used along css classes */
    if (!password || typeof password !== 'string') {
        console.error('Invalid password provided for strength validation.');
        return false;
    }
    if (!regex || !(regex instanceof RegExp)) {
        regex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/; // Default regex for strong password
    }

    return regex.test(password);
}


function togglePasswordVisibility(inputId, toggleButtonId) {
    const input = document.getElementById(inputId);
    const toggleButton = document.getElementById(toggleButtonId);

    if (!input || !toggleButton) {
        console.error('Invalid input or toggle button ID provided.');
        return;
    }

    toggleButton.addEventListener('click', function () {
        if (input.type === 'password') {
            input.type = 'text';
            toggleButton.innerHTML = "<i class='fa fa-eye'></i>";
        } else {
            input.type = 'password';
            toggleButton.innerHTML = "<i class='fa fa-eye-slash'></i>";
        }
    });
}





function validateInputRegex(input, regex) {
    if (!input || !(input instanceof HTMLInputElement)) {
        console.error('Invalid input element provided for regex validation.');
        return false;
    }
    if (!regex || !(regex instanceof RegExp)) {
        console.error('Invalid regex provided for validation.');
        return false;
    }

    input.addEventListener('input', function () {
        if (regex.test(input.value)) {
            input.classList.remove('is-invalid');
            input.classList.add('is-valid');
        } else {
            input.classList.remove('is-valid');
            input.classList.add('is-invalid');
        }
    });
    input.addEventListener('blur', function () {
        input.dispatchEvent(new Event('input'));
    });
}

function getCookie(name) {
    /** only if django HTTPONLY cookie setting is false */
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Check if this cookie string begins with the name we want
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


function getCSRFToken() {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    return csrfToken;
}



async function fetchWithCSRF(url, options = {}) {
    // options should be an object with method, headers, body, etc.
    const csrfToken = getCSRFToken();
    if (!options.headers) {
        options.headers = {};
    }
    options.headers['X-CSRFToken'] = csrfToken;
    try {
        const res = await fetch(url, options);
        if (!res.ok) {
            throw new Error(`HTTP error! status: ${res.status}`);
        }
        const data = await res.json();
        return data;
    }
    catch (error) {
        console.error('Fetch error:', error);
        throw error; // Re-throw the error for further handling
    }
}


function serializeForm(form) {
    const formData = new FormData(form);
    const serialized = {};
    for (const [key, value] of formData.entries()) {
        if (serialized.hasOwnProperty(key)) {
            // If the key already exists, convert it to an array
            if (!Array.isArray(serialized[key])) {
                serialized[key] = [serialized[key]];
            }
            serialized[key].push(value);
        } else {
            serialized[key] = value;
        }
    }
    return serialized;
}


function getQueryParam(param) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(param);
}


function setQueryParam(param, value) {
    const urlParams = new URLSearchParams(window.location.search);
    if (value === null || value === undefined) {
        urlParams.delete(param);
    } else {
        urlParams.set(param, value);
    }
    const newUrl = `${window.location.pathname}?${urlParams.toString()}`;
    window.history.pushState({}, '', newUrl);
}


function removeQueryParam(param) {
    const urlParams = new URLSearchParams(window.location.search);
    urlParams.delete(param);
    const newUrl = `${window.location.pathname}?${urlParams.toString()}`;
    window.history.pushState({}, '', newUrl);
}


function getCurrentUrl() {
    return window.location.href;
}


function setCurrentUrl(url) {
    if (url) {
        window.history.pushState({}, '', url);
    } else {
        console.warn('Invalid URL provided to setCurrentUrl.');
    }
}



function addFontAwesomeLoader(elementId, loading = true, text = 'Loading...', { size = '24px', color = '#000' } = {}) {
    const element = document.getElementById(elementId);
    if (!element) {
        console.warn(`Element with ID "${elementId}" not found.`);
        return;
    }

    const iconElement = document.createElement('i');
    iconElement.className = 'fa fa-spinner fa-spin';
    iconElement.style.fontSize = size;
    iconElement.style.color = color;

    if (!loading) {
        element_og_content = element.textContent; // Preserve original content
        element.textContent = ''; // Clear existing content
        element.textContent = text; // Set default loading text
        // Append the icon to the element
        element.appendChild(iconElement);
    } else {
        // Remove the icon and restore original content
        element.textContent = element_og_content || ''; // Restore original content if available
        if (iconElement.parentNode === element) {
            element.removeChild(iconElement);
        }
    }


}

function isCSRFTokenAvailable() {
    return !!getCSRFToken() || !!getCookie('csrftoken');
}



function preserveScrollPos() {
    const savedScrollPosition = localStorage.getItem('currentScrollPos');
    if (savedScrollPosition !== null) {
        window.scrollTo({
            top: Math.max(0, parseInt(savedScrollPosition, 10)),
            behavior: 'instant'
        });
        localStorage.removeItem('currentScrollPos'); // Clear after use
    }

    document.addEventListener('scroll', function () {
        const adjustedScroll = Math.max(0, window.scrollY); // Ensure non-negative value
        localStorage.setItem('currentScrollPos', adjustedScroll);
    });
}


function scrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
}



function scrollToElementById(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    } else {
        console.warn(`Element with ID ${elementId} not found.`);
    }
}



function scrollToBottom() {
    window.scrollTo({
        top: document.body.scrollHeight,
        behavior: 'smooth'
    });
}





