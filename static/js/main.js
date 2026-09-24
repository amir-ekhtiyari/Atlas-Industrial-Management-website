/* ==========================================================================
   ATLAS — تعاملات سایت
   بدون کتابخانه‌ی بیرونی. هر بخش مستقل است و اگر عنصرش در صفحه نباشد،
   بی‌صدا رد می‌شود. بدون JS، همه‌ی محتوا و ناوبری کار می‌کند.

   01 دراور ناوبری     05 نقاط راهنمای نقشه
   02 هدر چسبان        06 شمارنده و نمودار ارتفاع
   03 ظهور تدریجی      07 بازگشت به بالا
   04 گالری محصول      08 ناوبری درون‌صفحه‌ای محصول
   ========================================================================== */

(function () {
    'use strict';

    var root = document.documentElement;
    root.classList.remove('no-js');

    var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    /** رویداد اسکرول را به یک فریم در هر تیک محدود می‌کند. */
    function onScroll(handler) {
        var queued = false;
        function run() { queued = false; handler(); }
        window.addEventListener('scroll', function () {
            if (queued) return;
            queued = true;
            window.requestAnimationFrame(run);
        }, { passive: true });
        handler();
    }

    /* ------------------------------------------------ 01 · دراور ناوبری */

    function initDrawer() {
        var toggle = document.querySelector('[data-drawer-toggle]');
        var drawer = document.querySelector('[data-drawer]');
        if (!toggle || !drawer) return;

        var scrim = document.querySelector('[data-drawer-scrim]');
        var closeBtn = drawer.querySelector('[data-drawer-close]');
        var lastFocus = null;

        function isOpen() { return document.body.classList.contains('nav-open'); }

        function open() {
            lastFocus = document.activeElement;
            document.body.classList.add('nav-open');
            toggle.setAttribute('aria-expanded', 'true');
            var first = drawer.querySelector('a, button');
            if (first) first.focus({ preventScroll: true });
        }

        function close() {
            document.body.classList.remove('nav-open');
            toggle.setAttribute('aria-expanded', 'false');
            if (lastFocus && lastFocus.focus) lastFocus.focus({ preventScroll: true });
        }

        toggle.addEventListener('click', function () { isOpen() ? close() : open(); });
        if (scrim) scrim.addEventListener('click', close);
        if (closeBtn) closeBtn.addEventListener('click', close);
        drawer.querySelectorAll('a').forEach(function (a) {
            a.addEventListener('click', function () { if (isOpen()) close(); });
        });
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape' && isOpen()) close();
        });
        // Safari < 14 روی MediaQueryList متد addEventListener ندارد؛ بدون این
        // بررسی، خطای پرتاب‌شده بقیه‌ی راه‌اندازی‌ها (از جمله initReveal) را
        // متوقف می‌کند و محتوای .reveal برای همیشه نامرئی می‌ماند.
        var wide = window.matchMedia('(min-width: 1180px)');
        if (wide.addEventListener) {
            wide.addEventListener('change', function (e) {
                if (e.matches && isOpen()) close();
            });
        }
    }

    /* ------------------------------------------------- 02 · هدر چسبان */

    function initMasthead() {
        var head = document.querySelector('[data-masthead]');
        if (!head) return;
        onScroll(function () { head.classList.toggle('is-pinned', window.scrollY > 6); });
    }

    /* ----------------------------------------------- 03 · ظهور تدریجی */

    function initReveal() {
        var items = document.querySelectorAll('.reveal');
        if (!items.length) return;

        if (reduceMotion || !('IntersectionObserver' in window)) {
            items.forEach(function (el) { el.classList.add('is-in'); });
            return;
        }

        var io = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (!entry.isIntersecting) return;
                entry.target.classList.add('is-in');
                io.unobserve(entry.target);
            });
        }, { rootMargin: '0px 0px -10% 0px', threshold: 0.06 });

        items.forEach(function (el) { io.observe(el); });
    }

    /* ------------------------------------------------ 04 · گالری محصول */

    function initGallery() {
        var gallery = document.querySelector('[data-gallery]');
        if (!gallery) return;

        var stage = gallery.querySelector('[data-gallery-stage]');
        var thumbs = gallery.querySelectorAll('[data-gallery-thumb]');
        if (!stage || !thumbs.length) return;

        thumbs.forEach(function (thumb) {
            thumb.addEventListener('click', function () {
                var src = thumb.getAttribute('data-src');
                if (!src) return;
                stage.src = src;
                stage.alt = thumb.getAttribute('data-alt') || '';
                thumbs.forEach(function (other) {
                    var on = other === thumb;
                    other.classList.toggle('is-active', on);
                    other.setAttribute('aria-current', on ? 'true' : 'false');
                });
            });
        });
    }

    /* ---------------------------------------- 05 · نقاط راهنمای نقشه */

    function initHotspots() {
        var scope = document.querySelector('[data-spots]');
        if (!scope) return;

        var spots = scope.querySelectorAll('[data-spot]');
        var notes = document.querySelectorAll('[data-spot-note]');
        if (!spots.length) return;

        function select(key) {
            spots.forEach(function (s) {
                var on = s.getAttribute('data-spot') === key;
                s.classList.toggle('is-active', on);
                s.setAttribute('aria-pressed', on ? 'true' : 'false');
            });
            notes.forEach(function (n) {
                n.classList.toggle('is-active', n.getAttribute('data-spot-note') === key);
            });
        }

        spots.forEach(function (s) {
            var key = s.getAttribute('data-spot');
            s.addEventListener('click', function () { select(key); });
            s.addEventListener('mouseenter', function () { select(key); });
            s.addEventListener('focus', function () { select(key); });
        });
        notes.forEach(function (n) {
            var key = n.getAttribute('data-spot-note');
            n.addEventListener('click', function () { select(key); });
            n.addEventListener('mouseenter', function () { select(key); });
            n.addEventListener('focus', function () { select(key); });
        });

        var first = spots[0].getAttribute('data-spot');
        if (first) select(first);
    }

    /* ------------------------------ 06 · شمارنده و نمودار ارتفاع */

    function initCounters() {
        var counters = document.querySelectorAll('[data-count]');
        if (!counters.length) return;

        if (reduceMotion || !('IntersectionObserver' in window)) return;

        var formatter;
        try {
            formatter = new Intl.NumberFormat(root.lang || 'fa');
        } catch (e) {
            formatter = { format: function (n) { return String(n); } };
        }

        function run(el) {
            var target = parseFloat(el.getAttribute('data-count'));
            if (isNaN(target)) return;
            var started = performance.now();
            var duration = 1000;

            function step(now) {
                var p = Math.min((now - started) / duration, 1);
                var eased = 1 - Math.pow(1 - p, 3);
                el.textContent = formatter.format(Math.round(target * eased));
                if (p < 1) window.requestAnimationFrame(step);
            }
            window.requestAnimationFrame(step);
        }

        var io = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (!entry.isIntersecting) return;
                run(entry.target);
                io.unobserve(entry.target);
            });
        }, { threshold: 0.5 });

        counters.forEach(function (el) { io.observe(el); });
    }

    /** میله‌های نمودار ارتفاع از صفر به عرض هدف رشد می‌کنند. */
    function initBars() {
        var bars = document.querySelectorAll('[data-bar]');
        if (!bars.length) return;

        if (reduceMotion || !('IntersectionObserver' in window)) {
            bars.forEach(function (b) { b.style.setProperty('--w', b.getAttribute('data-bar') + '%'); });
            return;
        }

        bars.forEach(function (b) { b.style.setProperty('--w', '0%'); });

        var io = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (!entry.isIntersecting) return;
                var el = entry.target;
                el.style.setProperty('--w', el.getAttribute('data-bar') + '%');
                io.unobserve(el);
            });
        }, { threshold: 0.3 });

        bars.forEach(function (b) { io.observe(b); });
    }

    /* --------------------------------------------- 07 · بازگشت به بالا */

    function initToTop() {
        var btn = document.querySelector('[data-to-top]');
        if (!btn) return;

        onScroll(function () { btn.classList.toggle('is-shown', window.scrollY > 700); });
        btn.addEventListener('click', function () {
            window.scrollTo({ top: 0, behavior: reduceMotion ? 'auto' : 'smooth' });
        });
    }

    /* ------------------------------ 08 · ناوبری درون‌صفحه‌ای محصول */

    function initSubnav() {
        var nav = document.querySelector('[data-subnav]');
        if (!nav) return;

        var links = Array.prototype.slice.call(nav.querySelectorAll('a[href^="#"]'));
        var targets = links
            .map(function (a) { return document.getElementById(a.getAttribute('href').slice(1)); })
            .filter(Boolean);
        if (!targets.length) return;

        function mark(id) {
            links.forEach(function (a) {
                a.classList.toggle('is-active', a.getAttribute('href') === '#' + id);
            });
        }

        if ('IntersectionObserver' in window) {
            var io = new IntersectionObserver(function (entries) {
                entries.forEach(function (entry) {
                    if (entry.isIntersecting) mark(entry.target.id);
                });
            }, { rootMargin: '-45% 0px -50% 0px', threshold: 0 });
            targets.forEach(function (t) { io.observe(t); });
        }

        mark(targets[0].id);
    }

    /* ---------------------------------------------------- فرم‌ها */

    function initForms() {
        document.querySelectorAll('[data-form]').forEach(function (form) {
            form.addEventListener('submit', function () {
                if (!form.checkValidity()) return;
                var submit = form.querySelector('[type="submit"]');
                if (!submit) return;
                submit.setAttribute('aria-busy', 'true');
            });

            // اعتبارسنجی سمت کاربر: پس از خروج از هر فیلد، وضعیت درست/نادرست
            // آن دیده می‌شود. اعتبارسنجی سرور دست‌نخورده باقی می‌ماند.
            form.querySelectorAll('.field').forEach(function (field) {
                field.addEventListener('blur', function () {
                    var group = field.closest('.field-group');
                    if (!group) return;
                    var valid = field.checkValidity();
                    var filled = field.value.trim() !== '';
                    group.classList.toggle('field-group--bad', !valid);
                    group.classList.toggle('field-group--ok', valid && filled);
                    field.setAttribute('aria-invalid', valid ? 'false' : 'true');
                });
            });
        });
    }

    /* ------------------------------------------------------- init */

    function init() {
        // هر بخش مستقل اجرا می‌شود: خطای یکی نباید بقیه را از کار بیندازد،
        // وگرنه (چون کلاس no-js همان ابتدا برداشته شده) محتوای .reveal با
        // opacity:0 روی صفحه قفل می‌ماند.
        [
            initDrawer, initMasthead, initReveal, initGallery, initHotspots,
            initCounters, initBars, initToTop, initSubnav, initForms,
        ].forEach(function (fn) {
            try {
                fn();
            } catch (error) {
                if (window.console) window.console.error(fn.name, error);
            }
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
