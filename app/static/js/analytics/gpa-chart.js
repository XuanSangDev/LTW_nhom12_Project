/* Biểu đồ GPA: đường cong mượt + hiệu ứng "đi lên rồi lắng xuống" khi biểu đồ lộ ra màn hình.
   Dữ liệu lấy từ <script id="gpa-chart-data"> (do Flask xuất ra). Không có JS thì vẫn hiện bản tĩnh. */
(function () {
  var svg = document.getElementById('gpa-chart');
  var raw = document.getElementById('gpa-chart-data');
  var series = document.getElementById('gpa-series');
  if (!svg || !raw || !series) return;

  var c = JSON.parse(raw.textContent);
  var P = c.points, n = P.length, base = c.base;
  var NS = 'http://www.w3.org/2000/svg';
  var DUR = 950, STAGGER = 130, TOTAL = (n - 1) * STAGGER + DUR;

  function el(name, attrs, parent) {
    var e = document.createElementNS(NS, name);
    for (var k in attrs) e.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(e);
    return e;
  }
  function clamp(v, a, b) { return Math.min(b, Math.max(a, v)); }

  /* Đường cong đơn điệu (không bị "vọt" ra ngoài dữ liệu) */
  function curve(p) {
    var m = n - 1, dx = [], s = [], t = [], i;
    if (n < 2) return 'M' + p[0][0] + ',' + p[0][1];
    for (i = 0; i < m; i++) { dx[i] = p[i + 1][0] - p[i][0]; s[i] = (p[i + 1][1] - p[i][1]) / dx[i]; }
    t[0] = s[0]; t[m] = s[m - 1];
    for (i = 1; i < m; i++) t[i] = (s[i - 1] * s[i] <= 0) ? 0 : (s[i - 1] + s[i]) / 2;
    for (i = 0; i < m; i++) {
      if (s[i] === 0) { t[i] = 0; t[i + 1] = 0; continue; }
      var a = t[i] / s[i], b = t[i + 1] / s[i], q = a * a + b * b;
      if (q > 9) { var k = 3 / Math.sqrt(q); t[i] = k * a * s[i]; t[i + 1] = k * b * s[i]; }
    }
    var d = 'M' + p[0][0] + ',' + p[0][1];
    for (i = 0; i < m; i++) {
      var h = dx[i];
      d += ' C' + (p[i][0] + h / 3) + ',' + (p[i][1] + t[i] * h / 3) +
           ' ' + (p[i + 1][0] - h / 3) + ',' + (p[i + 1][1] - t[i + 1] * h / 3) +
           ' ' + p[i + 1][0] + ',' + p[i + 1][1];
    }
    return d;
  }

  /* vọt lên một chút rồi lắng xuống đúng giá trị */
  function easeOutBack(u) { var c1 = 1.2, c3 = c1 + 1; return 1 + c3 * Math.pow(u - 1, 3) + c1 * Math.pow(u - 1, 2); }

  /* Dựng lại các phần tử động (thay bản tĩnh) */
  series.textContent = '';
  var area = el('path', { fill: 'url(#gpaGradient)' }, series);
  var line = el('path', { fill: 'none', stroke: '#fe932c', 'stroke-width': 3, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, series);
  var items = P.map(function (p) {
    var g = el('g', {}, series);
    var halo = p.last ? el('circle', { r: 12, fill: '#fe932c', 'fill-opacity': 0.18 }, g) : null;
    var dot = el('circle', { r: p.last ? 6 : 5, fill: p.last ? '#fe932c' : '#0f2042', stroke: '#ffffff', 'stroke-width': 2.5 }, g);
    var tip = el('title', {}, dot); tip.textContent = p.label + ': GPA ' + p.gpa.toFixed(2);
    var txt = el('text', {
      'text-anchor': 'middle', 'font-size': 14, 'font-weight': 700, fill: p.last ? '#904d00' : '#0f2042',
      stroke: '#f6f7f9', 'stroke-width': 4, 'stroke-linejoin': 'round', 'paint-order': 'stroke'
    }, g);
    txt.textContent = p.gpa.toFixed(2);
    return { p: p, halo: halo, dot: dot, txt: txt };
  });

  function draw(ys, alphas) {
    var pts = P.map(function (p, i) { return [p.x, ys[i]]; });
    var d = curve(pts);
    line.setAttribute('d', d);
    area.setAttribute('d', d + ' L' + P[n - 1].x + ',' + base + ' L' + P[0].x + ',' + base + ' Z');
    items.forEach(function (it, i) {
      it.dot.setAttribute('cx', it.p.x); it.dot.setAttribute('cy', ys[i]);
      if (it.halo) { it.halo.setAttribute('cx', it.p.x); it.halo.setAttribute('cy', ys[i]); it.halo.setAttribute('opacity', alphas[i]); }
      it.txt.setAttribute('x', it.p.x); it.txt.setAttribute('y', ys[i] - 16);
      it.txt.setAttribute('opacity', alphas[i]);
    });
  }

  function frame(t) {
    var ys = [], al = [];
    P.forEach(function (p, i) {
      var u = clamp((t - i * STAGGER) / DUR, 0, 1);
      ys.push(base + (p.y - base) * easeOutBack(u));
      al.push(clamp((u - 0.4) / 0.6, 0, 1));
    });
    draw(ys, al);
  }

  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (reduce) { frame(TOTAL + 1); return; }

  frame(0);
  series.style.opacity = '0';
  var started = false;
  function play() {
    if (started) return;
    started = true;
    series.style.opacity = '1';
    var t0 = null;
    (function step(ts) {
      if (t0 === null) t0 = ts;
      var t = ts - t0;
      if (t < TOTAL) { frame(t); requestAnimationFrame(step); } else { frame(TOTAL + 1); }
    })(performance.now ? performance.now() : 0);
  }
  /* Chạy khi biểu đồ lộ ra ít nhất ~35% (biểu đồ nằm dưới màn hình đầu tiên) */
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { if (e.isIntersecting) { play(); io.disconnect(); } });
    }, { threshold: 0.35 });
    io.observe(svg);
  } else { play(); }
})();