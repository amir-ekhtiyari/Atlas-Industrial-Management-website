/* ==========================================================================
   Atlas — سوییچ زبان محتوا در پنل مدیریت
   django-modeltranslation برای هر فیلد ترجمه‌شده، دو ورودی جدا می‌سازد و به
   هرکدام کلاس `mt` و `mt-field-<name>-<lang>` می‌دهد. این اسکریپت نوار
   انتخاب زبان می‌سازد و ردیف فیلدهای زبان غیرفعال را پنهان می‌کند تا فرم
   کوتاه و خوانا بماند. بدون JS، همه‌ی فیلدها همان‌طور که هستند نمایش
   داده می‌شوند.
   ========================================================================== */

(function () {
    'use strict';

    var LANG_PATTERN = /(?:^|\s)mt-field-[\w-]*-([a-z]{2})(?:_[a-z]{2})?(?:\s|$)/i;
    var STORAGE_KEY = 'atlas-admin-content-language';

    function detectLanguage(field) {
        var match = LANG_PATTERN.exec(field.className || '');
        return match ? match[1].toLowerCase() : null;
    }

    function closestRow(element) {
        var node = element;
        while (node && node !== document.body) {
            if (node.classList && node.classList.contains('form-row')) return node;
            node = node.parentNode;
        }
        return null;
    }

    function labelFor(row) {
        return row ? row.querySelector('label') : null;
    }

    function init() {
        var form = document.querySelector('#content-main form');
        if (!form) return;

        var translated = form.querySelectorAll('.mt');
        if (!translated.length) return;

        var rowsByLang = {};
        var order = [];

        translated.forEach(function (field) {
            var lang = detectLanguage(field);
            if (!lang) return;

            var row = closestRow(field);
            if (!row) return;

            // ردیف‌های ترکیبی (چند فیلد در یک ردیف) را دست نمی‌زنیم تا چیزی گم نشود.
            var langsInRow = {};
            row.querySelectorAll('.mt').forEach(function (sibling) {
                var siblingLang = detectLanguage(sibling);
                if (siblingLang) langsInRow[siblingLang] = true;
            });
            if (Object.keys(langsInRow).length > 1) return;

            row.classList.add('atlas-lang-row');
            row.setAttribute('data-atlas-lang', lang);

            var label = labelFor(row);
            if (label && !label.querySelector('.atlas-lang-tag')) {
                var tag = document.createElement('span');
                tag.className = 'atlas-lang-tag';
                tag.setAttribute('data-lang', lang);
                tag.textContent = lang.toUpperCase();
                label.appendChild(tag);
            }

            if (!rowsByLang[lang]) {
                rowsByLang[lang] = [];
                order.push(lang);
            }
            rowsByLang[lang].push(row);
        });

        if (order.length < 2) return;

        var switcher = document.createElement('div');
        switcher.className = 'atlas-lang-switch';

        var caption = document.createElement('span');
        caption.className = 'atlas-lang-switch__label';
        caption.textContent = 'زبان محتوا:';
        switcher.appendChild(caption);

        var buttons = {};

        function apply(active) {
            order.forEach(function (lang) {
                var visible = lang === active;
                rowsByLang[lang].forEach(function (row) {
                    row.classList.toggle('atlas-hidden', !visible);
                });
                if (buttons[lang]) {
                    buttons[lang].classList.toggle('is-active', visible);
                    buttons[lang].setAttribute('aria-pressed', visible ? 'true' : 'false');
                }
            });
            try {
                window.localStorage.setItem(STORAGE_KEY, active);
            } catch (error) {
                /* حالت مرور خصوصی: نادیده گرفته می‌شود */
            }
        }

        order.forEach(function (lang) {
            var button = document.createElement('button');
            button.type = 'button';
            button.textContent = lang.toUpperCase();
            button.setAttribute('aria-pressed', 'false');
            button.addEventListener('click', function () { apply(lang); });
            buttons[lang] = button;
            switcher.appendChild(button);
        });

        var showAll = document.createElement('button');
        showAll.type = 'button';
        showAll.textContent = '↔';
        showAll.title = 'نمایش هر دو زبان';
        showAll.addEventListener('click', function () {
            order.forEach(function (lang) {
                rowsByLang[lang].forEach(function (row) { row.classList.remove('atlas-hidden'); });
                if (buttons[lang]) {
                    buttons[lang].classList.remove('is-active');
                    buttons[lang].setAttribute('aria-pressed', 'false');
                }
            });
        });
        switcher.appendChild(showAll);

        var anchor = form.querySelector('fieldset') || form.firstElementChild;
        if (anchor && anchor.parentNode) {
            anchor.parentNode.insertBefore(switcher, anchor);
        } else {
            form.insertBefore(switcher, form.firstChild);
        }

        var stored = null;
        try {
            stored = window.localStorage.getItem(STORAGE_KEY);
        } catch (error) {
            stored = null;
        }
        apply(order.indexOf(stored) !== -1 ? stored : order[0]);

        // اگر فیلدی خطای اعتبارسنجی دارد، زبان آن باید دیده شود.
        var firstError = form.querySelector('.form-row.errors[data-atlas-lang]');
        if (firstError) {
            apply(firstError.getAttribute('data-atlas-lang'));
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
