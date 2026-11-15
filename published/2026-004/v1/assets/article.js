// The article page's script. Nothing here is needed to read the article: with scripts off the
// text reads in full and every figure shows its static picture.
//
// 1. The site's menu and its light and dark reading toggle, kept as the site keeps them.
// 2. Each figure, drawn interactive from the figure written into the page, in the page's colors.
// 3. What changes after a version is frozen (later versions, the review status, the reviews),
//    read from the article's record beside its versions. A downloaded copy has no record to read
//    and says so in its own text.
(function () {
  'use strict';
  var root = document.documentElement;
  var article = document.querySelector('.hf-article');
  var PALETTE = {"light": ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"], "dark": ["#3987e5", "#d95926", "#199e70", "#c98500", "#d55181", "#008300", "#9085e9", "#e66767"]};

  // ---------- 1. Menu and theme ----------

  var navToggle = document.querySelector('.nav-toggle');
  var menu = document.getElementById('site-nav');
  if (navToggle && menu) {
    navToggle.addEventListener('click', function () {
      var open = menu.classList.toggle('open');
      navToggle.setAttribute('aria-expanded', String(open));
      document.body.style.overflow = open ? 'hidden' : '';
    });
    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape' && menu.classList.contains('open')) navToggle.click();
    });
  }

  function isDark() {
    if (root.dataset.theme === 'dark') return true;
    if (root.dataset.theme === 'light') return false;
    return window.matchMedia('(prefers-color-scheme: dark)').matches;
  }

  var themeToggle = document.querySelector('.theme-toggle');
  if (themeToggle) {
    themeToggle.addEventListener('click', function () {
      var next = isDark() ? 'light' : 'dark';
      root.dataset.theme = next;
      try {
        localStorage.setItem('hf-theme', next);
      } catch (error) {}
      drawAll();
    });
  }
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', drawAll);

  // The contents list is open where it sits beside the text, and closed where it sits above it.
  var contents = document.querySelector('.hf-contents details');
  if (contents && window.matchMedia('(min-width: 1240px)').matches) contents.open = true;

  // ---------- 2. Figures ----------

  var figures = [];
  document.querySelectorAll('.hf-figure').forEach(function (holder) {
    var source = holder.querySelector('.hf-spec');
    var plot = holder.querySelector('.hf-plot');
    if (!source || !plot) return;
    try {
      figures.push({ holder: holder, plot: plot, spec: JSON.parse(source.textContent), name: holder.dataset.figure });
    } catch (error) {}
  });

  function tokens() {
    var style = getComputedStyle(document.getElementById('main') || document.body);
    var read = function (name) {
      return style.getPropertyValue(name).trim();
    };
    return {
      text: read('--text'),
      muted: read('--muted'),
      grid: read('--line-soft'),
      axis: read('--line'),
      panel: read('--panel'),
      font: getComputedStyle(document.body).fontFamily,
    };
  }

  // A series written in one of the journal's colors takes that color's dark step in dark reading.
  function seriesColor(color, dark) {
    if (!dark || typeof color !== 'string') return color;
    var at = PALETTE.light.indexOf(color.toLowerCase());
    return at < 0 ? color : PALETTE.dark[at];
  }

  function themed(spec) {
    var dark = isDark();
    var t = tokens();
    var copy = JSON.parse(JSON.stringify(spec));
    (copy.data || []).forEach(function (trace) {
      ['line', 'marker'].forEach(function (part) {
        if (trace[part] && trace[part].color) trace[part].color = seriesColor(trace[part].color, dark);
      });
    });
    var layout = copy.layout || {};
    layout.autosize = true;
    delete layout.width;
    layout.height = layout.height || 460;
    layout.paper_bgcolor = 'rgba(0,0,0,0)';
    layout.plot_bgcolor = 'rgba(0,0,0,0)';
    layout.font = Object.assign({}, layout.font, { color: t.text, family: t.font });
    layout.legend = Object.assign({}, layout.legend, { bgcolor: 'rgba(0,0,0,0)' });
    layout.hoverlabel = Object.assign({}, layout.hoverlabel, {
      bgcolor: t.panel,
      bordercolor: t.axis,
      font: { color: t.text, family: t.font },
    });
    layout.modebar = { bgcolor: 'rgba(0,0,0,0)', color: t.muted, activecolor: t.text };
    Object.keys(layout).forEach(function (key) {
      if (/^[xy]axis\d*$/.test(key)) {
        layout[key] = Object.assign({}, layout[key], {
          gridcolor: t.grid,
          linecolor: t.axis,
          zerolinecolor: t.axis,
          tickcolor: t.axis,
          showline: true,
        });
      }
    });
    ['xaxis', 'yaxis'].forEach(function (key) {
      if (!layout[key]) layout[key] = { gridcolor: t.grid, linecolor: t.axis, zerolinecolor: t.axis, tickcolor: t.axis, showline: true };
    });
    copy.layout = layout;
    return copy;
  }

  function drawAll() {
    if (!window.Plotly) return;
    figures.forEach(function (figure) {
      var ready = themed(figure.spec);
      figure.plot.hidden = false;
      window.Plotly.react(figure.plot, ready.data, ready.layout, {
        responsive: true,
        displaylogo: false,
        toImageButtonOptions: { format: 'png', filename: figure.name, scale: 2 },
      }).then(
        function () {
          figure.holder.classList.add('is-live');
        },
        function () {
          figure.plot.hidden = true;
          figure.holder.classList.remove('is-live');
        }
      );
    });
  }
  drawAll();

  // ---------- 3. The article's record ----------

  if (!article) return;
  var here = Number(article.dataset.version);
  var STATUS = {
    'Review open': ['review-open', 'Published; reviews and comments are welcome.'],
    Reviewed: ['reviewed', 'Reviewed in public; the authors have answered or revised. Review stays open.'],
    Retracted: ['retracted', 'This article has been retracted. It is kept here, with the reason.'],
  };

  function text(tag, value, className) {
    var el = document.createElement(tag);
    el.textContent = value;
    if (className) el.className = className;
    return el;
  }

  function link(href, label) {
    var a = document.createElement('a');
    a.href = href;
    a.textContent = label;
    if (/^https?:/.test(href)) a.rel = 'noopener';
    return a;
  }

  function safeUrl(value) {
    return typeof value === 'string' && /^(https:\/\/|\.\.?\/|\/)/.test(value);
  }

  function apply(record) {
    if (!record || !Array.isArray(record.versions)) return;
    var latest = Number(record.latest);

    // The version selector, over every version that now exists.
    var slot = document.querySelector('.hf-select-label');
    if (slot && record.versions.length) {
      var select = document.createElement('select');
      select.className = 'hf-select';
      select.id = 'hf-version-select';
      record.versions.forEach(function (version) {
        var option = document.createElement('option');
        option.value = String(version.version);
        option.textContent =
          'Version ' + version.version + ', ' + version.date + (Number(version.version) === latest ? ' (latest)' : '');
        if (Number(version.version) === here) option.selected = true;
        select.appendChild(option);
      });
      select.addEventListener('change', function () {
        if (Number(select.value) !== here) window.location.href = '../v' + select.value + '/';
      });
      slot.textContent = 'Read ';
      slot.appendChild(select);
      slot.hidden = false;
      var list = document.querySelector('.hf-versions');
      if (list) list.hidden = true;
    }

    // A notice on any version that is not the latest.
    var notice = document.querySelector('.hf-notlatest');
    if (notice && latest > here) {
      var newest = record.versions[record.versions.length - 1];
      notice.textContent = '';
      notice.appendChild(text('span', 'A Later Version Exists', 'note-title'));
      var p = document.createElement('p');
      p.appendChild(document.createTextNode('This is version ' + here + '. The latest is version ' + latest + ', published ' + newest.date + '. '));
      p.appendChild(link('../v' + latest + '/', 'Read the latest version'));
      p.appendChild(document.createTextNode('.'));
      notice.appendChild(p);
      notice.hidden = false;
    }

    // Versions published after this one join its history.
    var later = document.getElementById('hf-history-later');
    if (later) {
      later.textContent = '';
      record.versions.forEach(function (version) {
        if (Number(version.version) <= here) return;
        var entry = document.createElement('p');
        var label = document.createElement('strong');
        label.appendChild(link('../v' + version.version + '/', 'Version ' + version.version));
        label.appendChild(document.createTextNode(', ' + version.date + '.'));
        entry.appendChild(label);
        entry.appendChild(document.createTextNode(' ' + (version.note || '') + ' (Published after this version.)'));
        later.appendChild(entry);
      });
    }

    // The status as it stands now.
    var banner = document.getElementById('hf-status');
    var known = STATUS[record.status];
    var reviews = Array.isArray(record.reviews) ? record.reviews : [];
    if (banner && known) {
      banner.dataset.status = known[0];
      banner.querySelector('.hf-status-name').textContent = record.status;
      var line = known[1];
      if (record.status === 'Reviewed' && reviews.length) {
        line = reviews.length + (reviews.length === 1 ? ' invited review is' : ' invited reviews are') + ' posted. ' + line;
      }
      if (record.status === 'Retracted' && record.retraction) line = 'Retracted: ' + record.retraction;
      banner.querySelector('.hf-status-text').textContent = line;
      var asOf = banner.querySelector('.hf-status-asof');
      if (asOf) asOf.remove();
    }

    // The reviews and the thread.
    var box = document.getElementById('hf-reviews-live');
    if (box) {
      box.textContent = '';
      if (reviews.length) {
        var ul = document.createElement('ul');
        ul.className = 'hf-reviews-list';
        reviews.forEach(function (review) {
          var li = document.createElement('li');
          var label = 'Review by ' + (review.reviewer || 'a reviewer whose name is withheld at their request');
          li.appendChild(safeUrl(review.url) ? link(review.url, label) : document.createTextNode(label));
          li.appendChild(document.createTextNode(
            (review.version ? ', of version ' + review.version : '') + (review.date ? ', ' + review.date : '') + '.'
          ));
          ul.appendChild(li);
        });
        box.appendChild(ul);
      } else {
        box.appendChild(text('p', 'No invited review has been posted yet.'));
      }
      if (safeUrl(record.thread)) {
        var thread = document.createElement('p');
        thread.appendChild(link(record.thread, 'The review thread'));
        thread.appendChild(document.createTextNode(': reviews, the authors’ answers, and comments from anyone.'));
        box.appendChild(thread);
      }
      var fallback = document.getElementById('hf-reviews-static');
      if (fallback) fallback.hidden = true;
    }
  }

  var recordUrl = article.dataset.record;
  if (recordUrl && window.location.protocol !== 'file:' && window.fetch) {
    fetch(recordUrl, { cache: 'no-cache' })
      .then(function (response) {
        return response.ok ? response.json() : null;
      })
      .then(apply)
      .catch(function () {});
  }
})();
