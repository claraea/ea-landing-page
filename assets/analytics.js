/* Google Analytics 4 (G-FGNHF3TWPW) com Consent Mode v2.
   Antes do consentimento o GA roda sem cookies (pings anônimos, dados modelados);
   ao aceitar, a escolha vai para localStorage e o consentimento é atualizado.
   Idioma do aviso segue o <html lang> da página. */
(function () {
  var ID = 'G-FGNHF3TWPW';
  var KEY = 'claraea-consent';
  var TEXT = {
    pt: { msg: 'Este site usa o Google Analytics para entender como é lido. Nenhum dado é usado para publicidade.', ok: 'Aceitar', no: 'Recusar', more: 'Saiba mais' },
    en: { msg: 'This site uses Google Analytics to understand how it is read. No data is used for advertising.', ok: 'Accept', no: 'Decline', more: 'Learn more' },
    es: { msg: 'Este sitio usa Google Analytics para entender cómo se lee. Ningún dato se usa para publicidad.', ok: 'Aceptar', no: 'Rechazar', more: 'Saber más' }
  };

  window.dataLayer = window.dataLayer || [];
  function gtag() { dataLayer.push(arguments); }
  window.gtag = gtag;

  var stored = null;
  try { stored = localStorage.getItem(KEY); } catch (e) {}

  gtag('consent', 'default', {
    analytics_storage: stored === 'granted' ? 'granted' : 'denied',
    ad_storage: 'denied', ad_user_data: 'denied', ad_personalization: 'denied',
    wait_for_update: 500
  });

  var s = document.createElement('script');
  s.async = true;
  s.src = 'https://www.googletagmanager.com/gtag/js?id=' + ID;
  document.head.appendChild(s);
  gtag('js', new Date());
  gtag('config', ID, { anonymize_ip: true });

  if (stored === 'granted' || stored === 'denied') return;

  function decide(value) {
    try { localStorage.setItem(KEY, value); } catch (e) {}
    gtag('consent', 'update', { analytics_storage: value });
    var el = document.getElementById('cookie-notice');
    if (el) el.remove();
  }

  function show() {
    var lang = (document.documentElement.lang || 'pt').slice(0, 2);
    var t = TEXT[lang] || TEXT.pt;
    var el = document.createElement('div');
    el.id = 'cookie-notice';
    el.setAttribute('role', 'dialog');
    el.setAttribute('aria-live', 'polite');
    el.innerHTML =
      '<p>' + t.msg + ' <a href="https://policies.google.com/technologies/partner-sites" target="_blank" rel="noopener">' + t.more + '</a></p>' +
      '<div class="cookie-notice__actions">' +
      '<button type="button" class="btn btn-outline btn-sm" data-consent="denied">' + t.no + '</button>' +
      '<button type="button" class="btn btn-primary btn-sm" data-consent="granted">' + t.ok + '</button>' +
      '</div>';
    el.addEventListener('click', function (ev) {
      var b = ev.target.closest('[data-consent]');
      if (b) decide(b.getAttribute('data-consent'));
    });
    document.body.appendChild(el);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', show);
  else show();
})();
