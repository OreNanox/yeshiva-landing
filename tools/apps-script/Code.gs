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

/* ── shared tracking sheet ──────────────────────────────────────────────────
   The sheet is not just a log — it is the team's working tool. Two extra
   columns (סטטוס, הערות צוות) belong to the team and are never overwritten,
   because new applications are only ever appended below.                      */

var STATUSES = ['חדש', 'נוצר קשר', 'נקבע ראיון', 'רואיין', 'התקבל', 'לא מתאים'];
var SHEET_NAME = 'מועמדויות';

function logRow_(d) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  if (!ss) return;

  var sh = ss.getSheetByName(SHEET_NAME);
  if (!sh) { sh = ss.insertSheet(SHEET_NAME); }
  if (sh.getLastRow() === 0) { setupSheet_(sh); }

  sh.appendRow(
    [new Date()]
      .concat(FIELDS.map(function (f) { return d[f[0]] ? String(d[f[0]]).trim() : ''; }))
      .concat([d.page || '', STATUSES[0], ''])
  );

  var row = sh.getLastRow();
  // status dropdown on the new row so the team can triage without typing
  sh.getRange(row, FIELDS.length + 3).setDataValidation(
    SpreadsheetApp.newDataValidation().requireValueInList(STATUSES, true).build()
  );
  sh.getRange(row, 1).setNumberFormat('dd/mm/yyyy HH:mm');
  sh.getRange(row, 1, 1, FIELDS.length + 4).setVerticalAlignment('top');
}

/** One-time formatting so the sheet is readable in Hebrew and easy to scan. */
function setupSheet_(sh) {
  var headers = ['תאריך']
    .concat(FIELDS.map(function (f) { return f[1]; }))
    .concat(['דף', 'סטטוס', 'הערות צוות']);

  sh.appendRow(headers);
  sh.setRightToLeft(true);                       // Hebrew reading order
  sh.setFrozenRows(1);                           // header stays visible while scrolling
  sh.getRange(1, 1, 1, headers.length)
    .setFontWeight('bold').setBackground('#0A1626').setFontColor('#E4BC62')
    .setVerticalAlignment('middle');
  sh.setRowHeight(1, 34);

  var widths = [130, 150, 120, 200, 55, 110, 190, 420, 90, 110, 220];
  widths.forEach(function (w, i) { if (i < headers.length) sh.setColumnWidth(i + 1, w); });

  // the free-text answer is long — wrap it instead of letting it run off screen
  sh.getRange(1, FIELDS.length + 1, sh.getMaxRows(), 1).setWrap(true);

  // colour-code the status column so the funnel is readable at a glance
  var statusCol = sh.getRange(2, FIELDS.length + 3, sh.getMaxRows() - 1, 1);
  var rules = [
    ['חדש',        '#FFF3CD'],
    ['נוצר קשר',   '#D9E7FB'],
    ['נקבע ראיון', '#D6E9D5'],
    ['רואיין',     '#CFE3F7'],
    ['התקבל',      '#B7E1B0'],
    ['לא מתאים',   '#F2D6D3']
  ].map(function (p) {
    return SpreadsheetApp.newConditionalFormatRule()
      .whenTextEqualTo(p[0]).setBackground(p[1]).setRanges([statusCol]).build();
  });
  sh.setConditionalFormatRules(rules);
}

/** Run once from the editor to create + format the sheet before going live. */
function setupNow() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sh = ss.getSheetByName(SHEET_NAME) || ss.insertSheet(SHEET_NAME);
  if (sh.getLastRow() === 0) setupSheet_(sh);
  Logger.log('sheet ready: ' + SHEET_NAME);
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
