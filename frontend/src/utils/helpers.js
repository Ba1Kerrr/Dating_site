export const escapeHtml = (text) => {
  const div = document.createElement('div')
  div.appendChild(document.createTextNode(String(text)))
  return div.innerHTML
}

export const sanitizeInput = (value) => {
  return value.replace(/[<>]/g, '')
}

export const getDelay = (index, base = 50) => `${index * base}ms`