/* Shared scientific line-icon system. Paths are installed into the stable shell sprite. */
(function (global) {
  'use strict';

  // 24-unit scientific instrument glyphs: measured spacing and distinct silhouettes.
  const ICON_PATHS = Object.freeze({
    dashboard: ["M3 4H11V11H3Z M13 4H21V9H13Z M13 11H21V20H13Z M3 13H11V20H3Z","M7 7H7.1 M16 6H18 M16 15H18 M6 17H8"],
    folder: ["M3 6H9L11 8H21V19H3Z","M3 10H21"],
    tools: ["M4 20L13 11 M14 4A5 5 0 0 0 20 10L16.5 13.5L10.5 7.5L14 4Z","M3 4H9V10H3Z"],
    import: ["M4 4H14V17H4Z","M7 7H11 M7 10H11 M19 8V20 M16 17L19 20L22 17"],
    settings: ["M4 5H20 M4 12H20 M4 19H20","M9 3V7 M15 10V14 M7 17V21"],
    modules: ["M4 4H20V20H4Z","M4 10H20 M4 15H20 M10 4V20"],
    foodweb: ["M3.5 5.5A2 2 0 1 0 7.5 5.5A2 2 0 1 0 3.5 5.5Z M16.5 5.5A2 2 0 1 0 20.5 5.5A2 2 0 1 0 16.5 5.5Z M10 18A2 2 0 1 0 14 18A2 2 0 1 0 10 18Z","M8 5.5H15 M12 3.5L15 5.5L12 7.5 M17 8L14 14 M17 12L14 14L13 10 M10 15L7 9 M7 13L7 9L10 10"],
    flask: ["M9 3H15 M10 3V10L5 18V21H19V18L14 10V3","M7 15H17"],
    clock: ["M6 4V2 M12 3V2 M18 4V2 M4 7H20V21H4Z","M12 11V15L16 17"],
    play: ["M4 4H12V20H4Z","M15 8L21 12L15 16Z"],
    globe: ["M12 3A9 9 0 1 0 12 21A9 9 0 1 0 12 3Z","M3 12H21 M12 3C8 6 8 18 12 21 M12 3C16 6 16 18 12 21 M5 8H19 M5 16H19"],
    map: ["M3 5L9 3L15 5L21 3V19L15 21L9 19L3 21Z","M9 3V19 M15 5V21"],
    cube: ["M12 3L20 7.5V16.5L12 21L4 16.5V7.5Z","M4 7.5L12 12L20 7.5 M12 12V21 M8 5.3L16 9.8"],
    chart: ["M4 4V20H21","M7 16L11 12L14 14L20 7"],
    target: ["M12 3V7 M12 17V21 M3 12H7 M17 12H21","M12 8A4 4 0 1 0 12 16A4 4 0 1 0 12 8Z"],
    refresh: ["M20 8V3 M20 8H15 M4 16V21 M4 16H9","M7 7A8 8 0 0 1 20 8 M17 17A8 8 0 0 1 4 16"],
    add: ["M12 3V21 M3 12H21"],
    upload: ["M4 15V20H20V15","M12 16V3 M8 7L12 3L16 7"],
    download: ["M4 15V20H20V15","M12 3V17 M8 13L12 17L16 13"],
    check: ["M3 12L9 18L21 5"],
    error: ["M12 3A9 9 0 1 0 12 21A9 9 0 1 0 12 3Z","M9 9L15 15 M15 9L9 15"],
    warning: ["M12 3L21 20H3Z","M12 8V13 M12 16V16.1"],
    info: ["M12 3A9 9 0 1 0 12 21A9 9 0 1 0 12 3Z","M12 11V16 M12 8V8.1"],
    list: ["M8 5H21 M8 10H21 M8 15H21 M8 20H21","M4 4V6 M4 9V11 M4 14V16 M4 19V21"],
    water: ["M3 6C6 4 9 8 12 6S18 4 21 6 M3 12C6 10 9 14 12 12S18 10 21 12 M3 18C6 16 9 20 12 18S18 16 21 18"],
    bio: ["M4 12C4 7 7 4 12 4C17 4 20 7 20 12C20 17 17 20 12 20C7 20 4 17 4 12Z","M12 6V18 M8 9H12 M12 15H16"],
    cloud: ["M4 5H20V19H4Z","M7 8H17 M7 12H11 M14 12H17 M7 16H17 M10 8V16 M14 12V16"],
    file: ["M5 3H14L19 8V21H5Z","M14 3V8H19 M8 12H16 M8 16H16"],
    ruler: ["M3 8H21V16H3Z","M6 8V13 M10 8V15 M14 8V13 M18 8V15"],
    save: ["M4 4H17L20 7V20H4Z","M7 4V10H16V4 M7 20V13H17V20"],
    river: ["M4 3C10 6 14 18 20 21 M20 3C14 6 10 18 4 21","M7 8H17 M8 12H16 M7 16H17"],
    pointer: ["M4 3L19 12L12 14L9 21Z","M12 14L17 20"],
    weather: ["M4 5H20V18H4Z","M7 9H17 M7 13H11 M14 13H17 M8 18L6 22 M15 18L13 22"],
    build: ["M3 20H21 M5 18V10L12 4L19 10V18Z","M9 18V13H15V18"],
    droplet: ["M12 3C9 7 6 10 6 14A6 6 0 0 0 18 14C18 10 15 7 12 3Z","M8 14H16 M9 17C10 18 11 19 12 19"],
    leaf: ["M4 20C4 9 10 4 20 4C20 14 15 20 4 20Z","M5 19L16 8 M10 14L10 11 M10 14L14 14"],
    health: ["M3 4H21V20H3Z","M5 13H8L10 9L13 17L16 11H19"],
    stop: ["M5 5H19V19H5Z"],
    search: ["M10 4A6 6 0 1 0 10 16A6 6 0 1 0 10 4Z","M14.5 14.5L21 21 M7 10H13 M10 7V13"],
    pin: ["M12 21L6 14V10A6 6 0 0 1 18 10V14Z","M9 10H15 M12 7V14"],
    draw: ["M4 20L8 19L19 8L15 4L4 15Z","M13 6L17 10 M4 15L9 20 M4 4H9"],
    previous: ["M5 4V20 M20 5L10 12L20 19Z"],
    next: ["M19 4V20 M4 5L14 12L4 19Z"],
    edit: ["M4 17L15 6L19 10L8 21H4Z","M13 8L17 12 M4 21L6 17 M16 5L18 7"],
    menu: ["M4 5H20 M4 10H20 M4 15H20 M4 20H20"],
    close: ["M4 4L20 20 M20 4L4 20"],
    chevron: ["M8 4L16 12L8 20"],
    up: ["M12 20V4 M7 9L12 4L17 9"],
    external: ["M13 4H20V11 M20 4L10 14","M18 13V20H4V6H11 M4 10H9"],
    undo: ["M8 7L4 11L8 15 M4 11H14V18H18"],
    redo: ["M16 7L20 11L16 15 M20 11H10V18H6"],
    pause: ["M5 4H10V20H5Z M14 4H19V20H14Z"],
    expand: ["M4 9V4H9 M15 4H20V9 M20 15V20H15 M9 20H4V15"],
    "zoom-in": ["M3 4H15V16H3Z","M15 15L21 21 M9 7V13 M6 10H12"],
    "zoom-out": ["M3 4H15V16H3Z","M15 15L21 21 M6 10H12"],
    down: ["M12 4V20 M7 15L12 20L17 15"],
    grid: ["M3 3H21V21H3Z M9 3V21 M15 3V21 M3 9H21 M3 15H21"],
    layers: ["M4 6L12 3L20 6L12 9Z M4 12L12 9L20 12 M4 18L12 15L20 18L12 21Z"],
  });

  function svg(name, className) {
    const symbol = String(name || 'info').replace(/[^a-z0-9-]/gi, '');
    const extra = String(className || '').replace(/[^a-z0-9 _-]/gi, '').trim();
    return `<svg class="studio-icon${extra ? ` ${extra}` : ''}" aria-hidden="true" focusable="false"><use href="#studio-icon-${symbol}"></use></svg>`;
  }

  function node(name, className) {
    const symbol = String(name || 'info').replace(/[^a-z0-9-]/gi, '');
    const extra = String(className || '').replace(/[^a-z0-9 _-]/gi, '').trim();
    const icon = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    icon.setAttribute('class', `studio-icon${extra ? ` ${extra}` : ''}`);
    icon.setAttribute('aria-hidden', 'true');
    icon.setAttribute('focusable', 'false');
    const use = document.createElementNS('http://www.w3.org/2000/svg', 'use');
    use.setAttribute('href', `#studio-icon-${symbol}`);
    icon.appendChild(use);
    return icon;
  }

  function installIconPaths(root = document) {
    for (const [name, paths] of Object.entries(ICON_PATHS)) {
      const symbol = root.querySelector(`#studio-icon-${name}`);
      if (!symbol) continue;
      const nodes = paths.map(d => {
        const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        path.setAttribute('d', d);
        return path;
      });
      symbol.replaceChildren(...nodes);
    }
  }

  function setStatus(element, name, label, className) {
    if (!element) return;
    element.replaceChildren(node(name, className), document.createTextNode(` ${String(label ?? '')}`));
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', () => installIconPaths(), { once: true });
  else installIconPaths();
  global.StudioIcons = Object.freeze({ svg, node, setStatus, installIconPaths, iconPaths: ICON_PATHS });
})(window);
