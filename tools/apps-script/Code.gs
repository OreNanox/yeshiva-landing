/**
 * ישיבת יראנו ניסים — application form receiver.
 *
 * Deployed as a Google Apps Script Web App, this receives the landing-page form
 * and emails the yeshiva team. The candidate never opens an email client.
 *
 * Security: no credentials live in the browser. The only public value is the
 * deployment URL, which accepts POSTs and can do nothing but send mail to the
 * fixed address below and append a row to the log sheet.
 *
 * ── SET THESE TWO ─────────────────────────────────────────────────────────── */

var TEAM_EMAIL = 'REPLACE_WITH_YESHIVA_EMAIL@example.com';  // ← where applications arrive
var ALSO_LOG_TO_SHEET = true;   // keep a spreadsheet log so no application is ever lost

/* ─────────────────────────────────────────────────────────────────────────── */

var FIELDS = [
  ['name',  'שם מלא'],
  ['phone', 'טלפון'],
  ['email', 'כתובת מייל'],
  ['age',   'גיל'],
  ['city',  'עיר מגורים'],
  ['now',   'מה אתה עושה היום'],
  ['about', 'על עצמי / למה עכשיו']
];

function json_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}

function doPost(e) {
  try {
    if (!e || !e.postData || !e.postData.contents) {
      return json_({ ok: false, error: 'empty request' });
    }

    var d = JSON.parse(e.postData.contents);

    // honeypot — silently accept so bots do not learn anything
    if (d._hp) return json_({ ok: true });

    // server-side validation: never trust the browser
    var missing = ['name', 'phone', 'email', 'age', 'about'].filter(function (k) {
      return !d[k] || String(d[k]).trim() === '';
    });
    if (missing.length) {
      return json_({ ok: false, error: 'missing: ' + missing.join(',') });
    }
    if (!/^[^\s@]+@[^\s@.]+(\.[^\s@.]+)+$/.test(String(d.email).trim())) {
      return json_({ ok: false, error: 'bad email' });
    }

    var name = String(d.name).trim();

    var lines = FIELDS.map(function (f) {
      return f[1] + ': ' + (d[f[0]] ? String(d[f[0]]).trim() : '—');
    });
    var body =
      'מועמדות חדשה לישיבת יראנו ניסים\n\n' +
      lines.join('\n') +
      '\n\n────────────────────\n' +
      'הגיע מהדף: ' + (d.page || '—') + '\n' +
      'זמן שליחה: ' + new Date().toLocaleString('he-IL') + '\n';

    MailApp.sendEmail({
      to: TEAM_EMAIL,
      subject: 'מועמדות חדשה — ' + name,
      body: body,
      replyTo: String(d.email).trim(),   // reply goes straight to the candidate
      name: 'טופס מועמדות — יראנו ניסים'
    });

    if (ALSO_LOG_TO_SHEET) {
      try { logRow_(d); } catch (err) { /* logging must never fail the submission */ }
    }

    return json_({ ok: true });

  } catch (err) {
    return json_({ ok: false, error: String(err) });
  }
}

/** Appends to a sheet bound to this script, creating the header row on first use. */
function logRow_(d) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  if (!ss) return;
  var sh = ss.getSheetByName('מועמדויות') || ss.insertSheet('מועמדויות');
  if (sh.getLastRow() === 0) {
    sh.appendRow(['תאריך'].concat(FIELDS.map(function (f) { return f[1]; })).concat(['דף']));
  }
  sh.appendRow([new Date()].concat(FIELDS.map(function (f) {
    return d[f[0]] ? String(d[f[0]]).trim() : '';
  })).concat([d.page || '']));
}

/** GET returns a plain heartbeat so the deployment can be verified in a browser. */
function doGet() {
  return json_({ ok: true, service: 'yiranu-nissim application form', method: 'POST only' });
}

/** Run once from the editor to confirm mail delivery works before going live. */
function selfTest() {
  var res = doPost({ postData: { contents: JSON.stringify({
    name: 'בדיקת מערכת', phone: '0500000000', email: 'test@example.com',
    age: '22', city: 'נתניה', now: 'בדיקה', about: 'שליחת בדיקה מהסקריפט',
    page: 'selfTest'
  })}});
  Logger.log(res.getContent());
}
