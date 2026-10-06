/* Presentation and existing same-origin APIs only. Django owns data and permissions. */
(() => {
  'use strict';
  if (document.querySelector('.pilot-page, .edit-page, .visit-page, .person-page')) document.body.classList.add('profile-view');
  const element = (tag, className, text) => {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text != null) node.textContent = text;
    return node;
  };
  const personTabs = [...document.querySelectorAll('[data-person-tab]')];
  if (personTabs.length) {
    const activate = () => {
      const active = location.hash === '#person-tasks' ? 'person-tasks' : 'person-about';
      personTabs.forEach(link => {
        const selected = link.dataset.personTab === active;
        link.classList.toggle('is-current', selected);
        if (selected) link.setAttribute('aria-current', 'location'); else link.removeAttribute('aria-current');
        document.getElementById(link.dataset.personTab).hidden = !selected;
      });
    };
    personTabs.forEach(link => link.addEventListener('click', event => { event.preventDefault(); history.pushState(null, '', link.hash); activate(); }));
    window.addEventListener('hashchange', activate); window.addEventListener('popstate', activate); activate();
    document.querySelectorAll('[data-person-tasks]').forEach(container => {
      const lines = container.innerHTML.split(/<br\s*\/?\s*>/i).map(line => { const item = element('span'); item.innerHTML = line; return item.textContent.trim(); }).filter(Boolean);
      const list = element('ul', 'task-list');
      lines.forEach(line => list.append(element('li', '', line))); container.replaceChildren(list);
    });
  }
  // The existing tasks field remains the only source of saved responsibilities.
  const tasksField = document.querySelector('textarea[name="tasks"]');
  if (tasksField) {
    const helper = element('div', 'task-editor');
    const hint = element('p', 'hint', 'Выберите нужную помощь. Повторное нажатие уберёт пункт. Свои обязанности можно дописать ниже.');
    const actions = element('div', 'choices'); actions.setAttribute('role', 'group'); actions.setAttribute('aria-label', 'Виды помощи');
    const buttons = [];
    for (const label of ['Приём лекарств', 'Покупка продуктов', 'Уборка', 'Прогулка', 'Приготовление еды', 'Помощь по дому', 'Общение']) {
      const button = element('button', 'choice', label); button.type = 'button'; button.setAttribute('aria-label', label);
      buttons.push([button, label]);
      button.addEventListener('click', () => {
        const tasks = tasksField.value.split('\n').map(task => task.trim()).filter(Boolean);
        {
          const value = (tasks.includes(label) ? tasks.filter(task => task !== label) : [...tasks, label]).join('\n');
          if (tasksField.maxLength > 0 && value.length > tasksField.maxLength) { tasksField.focus(); return; }
          tasksField.value = value; tasksField.dispatchEvent(new Event('input', { bubbles: true }));
        }
      }); actions.append(button);
    }
    const sync = () => buttons.forEach(([button, label]) => button.setAttribute('aria-pressed', String(tasksField.value.split('\n').map(task => task.trim()).includes(label))));
    tasksField.addEventListener('input', sync); sync();
    tasksField.placeholder = 'Например: полить цветы\nПомочь с оплатой квитанций';
    helper.append(hint, actions); tasksField.before(helper);
  }
  const visitTasks = document.getElementById('visit-tasks');
  if (visitTasks) {
    const form = visitTasks.closest('form');
    const text = form.querySelector('textarea[name="text"]');
    const tasks = [...new Set(JSON.parse(visitTasks.textContent).split('\n').map(value => value.trim()).filter(Boolean))];
    const fieldset = element('fieldset', 'checkbox-list');
    fieldset.append(element('legend', '', 'Что сделано во время визита?'));
    const count = element('p', 'hint'); count.setAttribute('role', 'status');
    const boxes = [];
    for (const task of tasks) {
      const label = element('label', 'checkbox'); const box = element('input', 'checkbox-control'); box.type = 'checkbox'; box.value = task;
      label.append(box, element('span', 'checkbox-label', task)); fieldset.append(label); boxes.push(box);
    }
    if (!tasks.length) fieldset.append(element('p', 'hint', 'В карточке ещё нет обязанностей. Опишите выполненные дела в заметке.'));
    const updateCount = () => { count.textContent = `Отмечено ${boxes.filter(box => box.checked).length} из ${tasks.length}`; };
    fieldset.addEventListener('change', updateCount); updateCount(); fieldset.append(count);
    const moodField = element('div', 'field');
    const moodLabel = element('label', 'field-label', 'Самочувствие и настроение'); moodLabel.htmlFor = 'visit-mood';
    const mood = element('select', 'field-control'); mood.id = 'visit-mood';
    for (const label of ['Не указано', 'Хорошее', 'Обычное', 'Есть жалобы']) { const option = element('option', '', label); option.value = label; mood.append(option); }
    moodField.append(moodLabel, mood, element('p', 'hint', 'Если есть жалобы, опишите их в заметке. Отметки сохранятся вместе с ней.'));
    text.closest('.field').before(fieldset, moodField);
    const label = text.closest('.field').querySelector('label'); label.textContent = 'Заметка о визите';
    const prefix = /^Итоги визита\nВыполнено:\n([\s\S]*?)\nНе отмечено:\n([\s\S]*?)\nСамочувствие: ([^\n]*)\n\nЗаметка:\n/;
    const previous = text.value.match(prefix);
    if (previous) {
      const done = previous[1].split('\n').map(item => item.replace(/^- /, ''));
      boxes.forEach(box => box.checked = done.includes(box.value));
      mood.value = [...mood.options].some(option => option.value === previous[3]) ? previous[3] : 'Не указано';
      text.value = text.value.slice(previous[0].length); updateCount();
    }
    const moodChoices = element('div', 'choices'); moodChoices.setAttribute('role', 'group'); moodChoices.setAttribute('aria-label', 'Самочувствие и настроение');
    const moodButtons = [];
    for (const [value, caption] of [['Не указано', 'Не оценивал(а)'], ['Хорошее', '☀ Хорошее'], ['Обычное', '○ Обычное'], ['Есть жалобы', '! Есть жалобы']]) {
      const button = element('button', 'choice', caption); button.type = 'button'; button.setAttribute('aria-label', caption);
      button.addEventListener('click', () => { mood.value = value; mood.dispatchEvent(new Event('change', { bubbles: true })); });
      moodButtons.push([button, value]); moodChoices.append(button);
    }
    const syncMood = () => moodButtons.forEach(([button, value]) => button.setAttribute('aria-pressed', String(mood.value === value)));
    mood.addEventListener('change', syncMood); syncMood(); mood.hidden = true; mood.after(moodChoices);
    const title = form.querySelector('input[name="title"]');
    const titles = element('div', 'choices'); titles.setAttribute('role', 'group'); titles.setAttribute('aria-label', 'Название визита');
    for (const value of ['Утренний визит', 'Дневной визит', 'Вечерний визит', 'Помощь по дому']) {
      const button = element('button', 'choice', value); button.type = 'button'; button.setAttribute('aria-label', value);
      const sync = () => button.setAttribute('aria-pressed', String(title.value === value));
      button.addEventListener('click', () => { title.value = value; title.dispatchEvent(new Event('input', { bubbles: true })); });
      title.addEventListener('input', sync); sync(); titles.append(button);
    }
    title.before(titles); title.placeholder = 'Или напишите своё название';
    if (form.classList.contains('visit-form')) {
      title.closest('.field').querySelector('label').innerHTML = 'Тема визита <em>*</em>';
      title.after(titles);
      text.closest('.field').querySelector('label').textContent = 'Подробности о самочувствии и настроении';
    }
    text.placeholder = 'Что важно знать близким? Подробности можно не добавлять, если отметок достаточно.';
    const noteField = text.closest('.field');
    if (!form.classList.contains('visit-form') && !text.required && !noteField.classList.contains('has-error')) {
      const details = element('details', 'extra'); details.open = Boolean(text.value);
      const summary = element('summary', '', 'Добавить подробности'); noteField.before(details); details.append(summary, noteField);
      mood.addEventListener('change', () => { if (mood.value === 'Есть жалобы') details.open = true; });
    }
    if (!form.classList.contains('visit-form')) form.prepend(element('p', 'form-intro', 'Несколько нажатий — и отчёт готов. Выберите название, отметьте сделанное и добавьте фото.'));
    form.addEventListener('formdata', event => {
      const done = boxes.filter(box => box.checked).map(box => '- ' + box.value).join('\n') || '—';
      const pending = boxes.filter(box => !box.checked).map(box => '- ' + box.value).join('\n') || '—';
      if (tasks.length || mood.value !== 'Не указано') event.formData.set('text', `Итоги визита\nВыполнено:\n${done}\nНе отмечено:\n${pending}\nСамочувствие: ${mood.value}\n\nЗаметка:\n${text.value}`);
    });
  }
  // Use a standard dialog: keyboard focus and Escape work without a custom trap.
  const photoLinks = document.querySelectorAll('a:has(.report-photo)');
  if (photoLinks.length) {
    const dialog = element('dialog', 'modal photo-modal');
    const heading = element('h2', '', 'Фото визита'); heading.id = 'photo-title'; dialog.setAttribute('aria-labelledby', heading.id);
    const close = element('button', 'button outline', 'Закрыть'); close.type = 'button';
    const picture = element('img', 'photo-full');
    const controls = element('div', 'actions');
    const previous = element('button', 'button light', 'Предыдущее'); previous.type = 'button';
    const next = element('button', 'button light', 'Следующее'); next.type = 'button';
    const caption = element('p', 'caption'); caption.setAttribute('role', 'status');
    controls.append(previous, next, close); dialog.append(heading, picture, caption, controls); document.body.append(dialog);
    let index = 0;
    const show = () => { picture.src = photoLinks[index].href; picture.alt = photoLinks[index].querySelector('img').alt; caption.textContent = `${index + 1} / ${photoLinks.length}`; previous.disabled = index === 0; next.disabled = index === photoLinks.length - 1; };
    close.addEventListener('click', () => dialog.close());
    previous.addEventListener('click', () => { if (index > 0) { index--; show(); } });
    next.addEventListener('click', () => { if (index < photoLinks.length - 1) { index++; show(); } });
    photoLinks.forEach((link, position) => link.addEventListener('click', event => { if (event.ctrlKey || event.metaKey || event.shiftKey) return; event.preventDefault(); index = position; show(); dialog.showModal(); }));
  }
  document.querySelectorAll('.form input[type="password"]').forEach(input => {
    const wrapper = element('div', 'password'); input.before(wrapper); wrapper.append(input);
    const toggle = element('button', 'button plain password-toggle', 'Показать'); toggle.type = 'button'; toggle.setAttribute('aria-pressed', 'false');
    toggle.addEventListener('click', () => { const visible = input.type === 'password'; input.type = visible ? 'text' : 'password'; toggle.textContent = visible ? 'Скрыть' : 'Показать'; toggle.setAttribute('aria-pressed', String(visible)); }); wrapper.append(toggle);
  });
  document.querySelectorAll('.form textarea[maxlength]').forEach(input => {
    const counter = element('span', 'hint'); const update = () => counter.textContent = `${input.value.length} / ${input.maxLength}`;
    input.after(counter); input.addEventListener('input', update); update();
  });
  const firstError = document.querySelector('.has-error input, .has-error textarea, .has-error select');
  if (firstError) firstError.focus();
  const personName = document.querySelector('.form input[name="full_name"]');
  if (personName && tasksField) {
    const form = personName.form;
    form.classList.add('person-form');
    if (!form.hasAttribute('data-create-form')) form.prepend(element('p', 'form-intro', 'Познакомимся с человеком и выберем, какая помощь нужна. Обязательные поля отмечены звёздочкой.'));
    personName.autocomplete = 'off'; personName.placeholder = 'Фамилия Имя Отчество';
    const description = form.querySelector('textarea[name="description"]');
    if (description) description.placeholder = 'Как обращаться к человеку, что он любит, о чём стоит знать пилоту';
    const health = form.querySelector('textarea[name="health_problems"]');
    if (health) { health.placeholder = 'Коротко: ограничения и особенности, которые важно учитывать при помощи'; health.rows = 3; }
    const birth = form.querySelector('input[name="date_birth"]');
    if (birth) {
      const value = birth.value;
      const localized = value.match(/^(\d{2})\.(\d{2})\.(\d{4})$/);
      const iso = localized ? `${localized[3]}-${localized[2]}-${localized[1]}` : value;
      if (!iso || /^\d{4}-\d{2}-\d{2}$/.test(iso)) { birth.type = 'date'; birth.value = iso; }
    }
  }
  const profileDescription = document.querySelector('.form textarea[name="description"]');
  if (profileDescription && !personName) profileDescription.form.classList.add('profile-form');
  if (profileDescription?.closest('.profile-edit')) {
    const form = profileDescription.form;
    profileDescription.closest('.field').querySelector('label').textContent = 'О себе';
    profileDescription.placeholder = 'Расскажите, с чем вы помогаете и что для вас важно в общении с сопровождаемыми';
    const phone = form.querySelector('input[name="telephone"]'); phone.type = 'tel'; phone.autocomplete = 'tel'; phone.placeholder = '+7 999 123-45-67';
    form.querySelector('input[name="max_name"]').placeholder = 'Имя в MAX';
    form.querySelector('input[name="vk_name"]').placeholder = 'Имя в VK';
  }
  document.querySelectorAll('.form input[type=file]').forEach(input => {
    const box = element('div', 'upload'); input.before(box);
    const label = element('label', 'upload-label', input.name === 'video' ? '＋ Добавить видео' : '＋ Загрузить фото'); label.htmlFor = input.id;
    box.append(label, input);
    if (input.closest('.visit-form')) {
      label.textContent = input.name === 'video' ? 'Загрузить видео' : 'Загрузить фото';
      box.classList.add(input.name === 'video' ? 'video-upload' : 'photo-upload');
    }
    if (input.closest('[data-create-form]')) {
      label.textContent = 'Загрузить фото';
      const hint = element('span', 'hint', 'JPG, PNG'); box.append(hint);
    }
    if (input.name === 'preview') {
      const field = input.closest('.field');
      const current = field.querySelector('a');
      if (current) {
        const photo = element('img', 'current-photo'); photo.src = current.href; photo.alt = 'Фото сопровождаемого';
        current.textContent = ''; current.append(photo);
      }
      for (const node of field.childNodes) {
        if (node.nodeType === Node.TEXT_NODE) node.textContent = node.textContent.replace('Currently:', '').replace('Change:', '');
      }
      const clear = field.querySelector('label[for$="-clear_id"]'); if (clear) clear.textContent = 'Удалить текущее фото';
    }
  });
  const createForm = document.querySelector('[data-create-form]');
  if (createForm) {
    document.body.classList.add('create-view');
    const grid = createForm.querySelector('.person-grid');
    const side = element('div', 'person-side'); const fields = element('div', 'person-fields');
    for (const field of [...grid.children]) {
      (field.classList.contains('field-preview') || field.classList.contains('field-responsible_person') ? side : fields).append(field);
    }
    grid.append(side, fields);
    const select = createForm.querySelector('select[name="responsible_person"]');
    const options = [...select.options].filter(option => option.value).map(option => ({ id: option.value, name: option.textContent.replace(/^Ответственное лицо /, '') }));
    const cards = [...createForm.querySelectorAll('[data-contact-id]')];
    const value = element('input'); value.type = 'hidden'; value.name = select.name; value.value = select.value;
    const search = element('input', 'contact-search'); search.type = 'search'; search.id = select.id; search.required = select.required; search.autocomplete = 'off'; search.placeholder = 'Найти по имени';
    const results = element('div', 'contact-results'); results.id = 'contact-results'; results.setAttribute('role', 'group'); results.setAttribute('aria-label', 'Подходящие ответственные лица'); search.setAttribute('aria-controls', results.id);
    const status = element('p', 'hint'); status.id = 'contact-status'; status.setAttribute('role', 'status'); search.setAttribute('aria-describedby', status.id);
    const clear = element('button', 'contact-clear', 'Убрать выбранного человека'); clear.type = 'button';
    select.replaceWith(search, value, results, status, clear);
    const showContact = () => {
      cards.forEach(card => card.hidden = card.dataset.contactId !== value.value);
      clear.hidden = !value.value;
      search.setCustomValidity(value.value || !search.required ? '' : 'Выберите ответственного человека из предложенных карточек.');
    };
    const choose = person => {
      value.value = person.id; search.value = person.name; results.replaceChildren(); status.textContent = 'Ответственное лицо выбрано.'; showContact(); search.focus();
    };
    const findContacts = () => {
      value.value = ''; showContact(); results.replaceChildren();
      const query = search.value.trim().toLocaleLowerCase();
      if (!query) { status.textContent = 'Введите имя, чтобы найти человека.'; return; }
      const matches = options.filter(person => person.name.toLocaleLowerCase().includes(query));
      status.textContent = matches.length ? `Найдено: ${matches.length}. Выберите карточку.` : 'Никого не найдено. Попробуйте другое имя.';
      for (const person of matches) {
        const button = element('button', 'contact-option'); button.type = 'button';
        const card = cards.find(card => card.dataset.contactId === person.id);
        if (card) { const copy = card.cloneNode(true); copy.hidden = false; copy.removeAttribute('data-contact-id'); button.append(copy); }
        else button.append(element('span', '', person.name));
        button.addEventListener('click', () => choose(person)); results.append(button);
      }
    };
    search.addEventListener('input', findContacts);
    search.addEventListener('keydown', event => {
      if (event.key === 'ArrowDown' && results.firstElementChild) { event.preventDefault(); results.firstElementChild.focus(); }
      if (event.key === 'Enter' && !value.value) { event.preventDefault(); results.firstElementChild?.focus(); }
      if (event.key === 'Escape') { results.replaceChildren(); status.textContent = value.value ? 'Ответственное лицо выбрано.' : 'Введите имя, чтобы найти человека.'; }
    });
    results.addEventListener('keydown', event => {
      const button = event.target.closest('button'); if (!button) return;
      if (event.key === 'ArrowDown') { event.preventDefault(); (button.nextElementSibling || button).focus(); }
      if (event.key === 'ArrowUp') { event.preventDefault(); (button.previousElementSibling || search).focus(); }
      if (event.key === 'Escape') { search.focus(); results.replaceChildren(); }
    });
    clear.addEventListener('click', () => { search.value = ''; findContacts(); search.focus(); });
    const initial = options.find(person => person.id === value.value);
    if (initial) choose(initial); else { value.value = ''; showContact(); status.textContent = 'Введите имя, чтобы найти человека.'; }
    const photo = createForm.querySelector('input[name="preview"]');
    const placeholder = createForm.querySelector('[data-person-photo]');
    photo.addEventListener('change', () => queueMicrotask(() => {
      const field = photo.closest('.field'); const preview = field.querySelector('.preview-list');
      if (preview) placeholder.after(preview);
      placeholder.hidden = Boolean(photo.files.length);
    }));
  }
  async function getJSON(path, signal) {
    const url = new URL(path, location.href);
    if (url.origin !== location.origin) throw new Error('Некорректный адрес страницы.');
    const response = await fetch(url, { credentials: 'same-origin', headers: { Accept: 'application/json' }, signal });
    if (!response.ok) throw new Error(response.status === 403 || response.status === 401 ? 'Нет доступа. Войдите в аккаунт заново.' : 'Не удалось загрузить данные. Попробуйте ещё раз.');
    if (!response.headers.get('content-type')?.includes('application/json')) throw new Error('Сессия завершилась. Войдите в аккаунт заново.');
    return response.json();
  }
  const directory = document.querySelector('[data-directory]');
  if (directory) {
    const status = directory.querySelector('[data-directory-status]');
    const results = directory.querySelector('[data-directory-results]');
    const city = directory.querySelector('select');
    const previous = directory.querySelector('[data-directory-previous]');
    const next = directory.querySelector('[data-directory-next]');
    let controller;
    let loaded = false;
    async function loadPilots(path) {
      controller?.abort(); controller = new AbortController();
      const current = controller;
      previous.disabled = next.disabled = true;
      status.textContent = 'Загружаем пилотов…'; results.replaceChildren(); results.setAttribute('aria-busy', 'true');
      try {
        const page = await getJSON(path, current.signal);
        if (controller !== current) return;
        const pilots = Array.isArray(page) ? page : page.results;
        for (const pilot of pilots) {
          const card = element('article', 'card');
          const name = [pilot.last_name, pilot.first_name].filter(Boolean).join(' ') || 'Пилот';
          card.append(element('h3', '', name));
          card.append(element('p', 'info-text', pilot.description || 'Описание пока не добавлено.'));
          for (const [title, value] of [['Телефон', pilot.telephone], ['MAX', pilot.max_name], ['VK', pilot.vk_name], ['Почта', pilot.email]]) {
            if (value) card.append(element('p', 'meta', `${title}: ${value}`));
          }
          results.append(card);
        }
        status.textContent = pilots.length ? `Найдено: ${page.count ?? pilots.length}` : 'В этом населённом пункте пока нет доступных пилотов.';
        previous.dataset.url = page.previous || ''; next.dataset.url = page.next || '';
        previous.disabled = !page.previous; next.disabled = !page.next;
      } catch (error) { if (error.name !== 'AbortError') status.textContent = error.message; }
      finally { if (controller === current) results.removeAttribute('aria-busy'); }
    }
    directory.addEventListener('toggle', async () => {
      if (!directory.open || loaded) return;
      loaded = true;
      loadPilots(directory.dataset.api);
      try {
        let url = directory.dataset.settlements;
        const names = new Set();
        while (url) {
          const page = await getJSON(url);
          for (const item of (Array.isArray(page) ? page : page.results)) names.add(item.name);
          url = page.next;
        }
        for (const name of [...names].sort((a, b) => a.localeCompare(b, 'ru'))) { const option = element('option', '', name); option.value = name; city.append(option); }
      } catch {
        // Text input keeps the server-side filter usable if the directory cannot load.
        const input = element('input', 'field-control'); input.id = city.id; input.name = city.name; input.placeholder = 'Название населённого пункта'; city.replaceWith(input);
      }
    });
    directory.querySelector('form').addEventListener('submit', event => {
      event.preventDefault(); const url = new URL(directory.dataset.api, location.href);
      const value = new FormData(event.target).get('city').trim();
      if (value) url.searchParams.set('settlements__name', value);
      loadPilots(url.href);
    });
    for (const button of [previous, next]) button.addEventListener('click', () => { if (button.dataset.url) loadPilots(button.dataset.url); });
  }
  const reportSearch = document.querySelector('[data-report-search]');
  if (reportSearch) {
    let controller;
    reportSearch.querySelector('form').addEventListener('submit', async event => {
      event.preventDefault();
      controller?.abort(); controller = new AbortController(); const current = controller;
      const status = reportSearch.querySelector('[data-report-status]');
      const results = reportSearch.querySelector('[data-report-results]');
      const day = new FormData(event.target).get('date');
      if (!/^\d{4}-\d{2}-\d{2}$/.test(day)) return;
      status.textContent = 'Загружаем отчёт…'; results.replaceChildren(); results.setAttribute('aria-busy', 'true');
      try {
        const report = await getJSON(reportSearch.dataset.api.replace('2000-01-01', day), current.signal);
        if (current !== controller) return;
        status.textContent = report.message || (report.report_notes?.length ? `Отчёт за ${day.split('-').reverse().join('.')}` : 'В отчёте за этот день пока нет заметок.');
        for (const note of report.report_notes || []) {
          const card = element('article', 'notice');
          card.append(element('h3', '', note.title), element('p', 'caption', [note.last_name, note.first_name].filter(Boolean).join(' ')), element('p', 'info-text', note.text));
          const media = element('div', 'grid');
          for (const [kind, list] of [['image', note.photos], ['video', note.videos]]) {
            for (const item of list || []) {
              const url = new URL(item.photo || item.video, location.href);
              if (!['http:', 'https:'].includes(url.protocol)) continue;
              const node = element(kind === 'image' ? 'img' : 'video', kind === 'image' ? 'report-photo' : 'report-video');
              node.src = url.href;
              if (kind === 'image') { node.alt = note.title; node.loading = 'lazy'; }
              else { node.controls = true; node.preload = 'metadata'; node.setAttribute('aria-label', note.title); }
              media.append(node);
            }
          }
          card.append(media); results.append(card);
        }
      } catch (error) { if (error.name !== 'AbortError') status.textContent = error.message; }
      finally { if (current === controller) results.removeAttribute('aria-busy'); }
    });
  }
  const search = document.querySelector('[data-search-input]');
  if (search) search.addEventListener('input', () => {
    let count = 0;
    document.querySelectorAll('[data-search-item]').forEach(card => {
      card.hidden = !card.dataset.searchItem.toLocaleLowerCase().includes(search.value.trim().toLocaleLowerCase());
      if (!card.hidden) count++;
    });
    document.querySelector('[data-search-empty]').hidden = count > 0;
  });
  const previews = new Map();
  document.querySelectorAll('input[type=file]').forEach(input => input.addEventListener('change', () => {
    if (input.closest('[data-media-form]')) {
      const video = input.name === 'video';
      const extensions = video ? ['mp4', 'avi', 'mkv', 'webm'] : ['jpg', 'jpeg', 'png'];
      const limit = (video ? 50 : 5) * 1024 * 1024;
      const invalid = [...input.files].some(file => file.size > limit || !extensions.includes(file.name.split('.').pop().toLowerCase()));
      input.setCustomValidity(invalid ? `Допустимы ${extensions.join(', ')} до ${video ? 50 : 5} МБ.` : '');
      if (invalid) input.reportValidity();
    }
    let container = document.querySelector(`[data-preview="${input.id}"]`);
    if (!container) { container = document.createElement('div'); container.className = 'preview-list'; container.dataset.preview = input.id; if (input.closest('.visit-form')) input.closest('.upload').after(container); else input.after(container); }
    if (input.closest('.visit-form')) input.closest('.upload').hidden = input.files.length > 0 && input.validity.valid;
    (previews.get(input) || []).forEach(url => URL.revokeObjectURL(url));
    const urls = []; container.replaceChildren();
    [...input.files].forEach(file => {
      if (!file.type.startsWith('image/') && !file.type.startsWith('video/')) return;
      const url = URL.createObjectURL(file); urls.push(url);
      const figure = document.createElement('figure'); figure.className = 'preview-item';
      const media = document.createElement(file.type.startsWith('image/') ? 'img' : 'video'); media.src = url;
      if (media.tagName === 'VIDEO') { media.controls = true; media.preload = 'metadata'; media.setAttribute('aria-label', file.name); } else media.alt = file.name;
      const caption = document.createElement('figcaption'); caption.textContent = file.name;
      const remove = element('button', 'button light small', 'Убрать файл'); remove.type = 'button';
      remove.addEventListener('click', () => { input.value = ''; input.setCustomValidity(''); input.dispatchEvent(new Event('change', { bubbles: true })); });
      figure.append(media, caption, remove); container.append(figure);
    });
    previews.set(input, urls);
  }));
  document.querySelectorAll('.form input, .form textarea, .form select').forEach(input => {
    if (input.type !== 'checkbox' && input.type !== 'hidden') input.classList.add('field-control');
  });
  document.querySelectorAll('[data-media-form] input[type=file]').forEach(input => {
    input.accept = input.name === 'video' ? '.mp4,.avi,.mkv,.webm' : '.jpg,.jpeg,.png';
  });
  document.querySelectorAll('.navigation a').forEach(link => {
    if (new URL(link.href).pathname === location.pathname) { link.classList.add('is-current'); link.setAttribute('aria-current', 'page'); }
  });
})();
