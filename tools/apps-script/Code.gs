/**
 * ישיבת יראנו ניסים — application form receiver.
 *
 * Deployed as a Google Apps Script Web App: receives the landing-page form and
 * emails the yeshiva team. The candidate never opens an email client.
 *
 * Works BOTH as a container-bound script (opened from the sheet) and as a
 * standalone project — it reaches the sheet by ID, so logging never silently
 * stops just because the project was created standalone.
 *
 * Security: no credentials live in the browser. The only public value is the
 * deployment URL, which can do exactly two things — mail the fixed addresses
 * below and append a row to the log sheet.
 *
 * ── CONFIG ────────────────────────────────────────────────────────────────── */

// Recipients live HERE, server-side — never in the public page. That is what lets
// this satisfy both "both addresses receive" and "no e-mail address in the source".
var TEAM_EMAIL = 'info@yarenunissim.com';
var NOTIFY_CC  = 'mak720431@gmail.com';

// The shared tracking sheet. Not a secret — access is governed by the sheet's
// own sharing settings, not by whether the id is known.
var SHEET_ID   = '1gBNXydeDd0rblV3-6rIkprOzxbPS8lRy-jTkc9JEOMM';
var SHEET_NAME = 'מועמדויות';
var ALSO_LOG_TO_SHEET = true;

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

var STATUSES = ['חדש', 'נוצר קשר', 'נקבע ראיון', 'רואיין', 'התקבל', 'לא מתאים'];

function json_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}

/** The spreadsheet, whether this script is bound to it or standalone. */
function book_() {
  var ss = null;
  try { ss = SpreadsheetApp.getActiveSpreadsheet(); } catch (e) { ss = null; }
  if (!ss && SHEET_ID) { ss = SpreadsheetApp.openById(SHEET_ID); }
  if (!ss) throw new Error('לא נמצא גיליון: הגדר SHEET_ID בראש הקובץ.');
  return ss;
}

/* ── the web endpoint ─────────────────────────────────────────────────────── */

function doPost(e) {
  try {
    if (!e || !e.postData || !e.postData.contents) {
      return json_({ ok: false, error: 'empty request' });
    }

    var d = JSON.parse(e.postData.contents);

    // honeypot — accept silently so bots learn nothing
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

    // log to the sheet FIRST, so a mail failure can never lose the application
    var logged = false, logError = '';
    if (ALSO_LOG_TO_SHEET) {
      try { logRow_(d); logged = true; }
      catch (err) { logError = String(err); }
    }

    MailApp.sendEmail({
      to: TEAM_EMAIL,
      cc: NOTIFY_CC,                     // both addresses get every application
      subject: 'מועמדות חדשה — ' + name,
      body: body + (logged ? '' : '\n⚠️ שורה לא נרשמה בגיליון: ' + logError + '\n'),
      replyTo: String(d.email).trim(),   // reply goes straight to the candidate
      name: 'טופס מועמדות — יראנו ניסים'
    });

    return json_({ ok: true, logged: logged });

  } catch (err) {
    return json_({ ok: false, error: String(err) });
  }
}

/** GET returns a heartbeat so the deployment can be checked in a browser. */
function doGet() {
  return json_({ ok: true, service: 'yiranu-nissim application form', method: 'POST only' });
}

/* ── shared tracking sheet ────────────────────────────────────────────────────
   Two columns (סטטוס, הערות צוות) belong to the team and are never overwritten,
   because new applications are only ever appended below.                       */

function sheet_() {
  var ss = book_();
  var sh = ss.getSheetByName(SHEET_NAME);
  if (!sh) sh = ss.insertSheet(SHEET_NAME);
  if (sh.getLastRow() === 0) setupSheet_(sh);
  return sh;
}

function logRow_(d) {
  var sh = sheet_();

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
  sh.setRightToLeft(true);
  sh.setFrozenRows(1);
  sh.getRange(1, 1, 1, headers.length)
    .setFontWeight('bold').setBackground('#0A1626').setFontColor('#E4BC62')
    .setVerticalAlignment('middle');
  sh.setRowHeight(1, 34);

  var widths = [130, 150, 120, 200, 55, 110, 190, 420, 90, 110, 220];
  widths.forEach(function (w, i) { if (i < headers.length) sh.setColumnWidth(i + 1, w); });

  // the long free-text answer wraps instead of running off screen
  sh.getRange(1, FIELDS.length + 1, sh.getMaxRows(), 1).setWrap(true);

  // colour-code the status column so the funnel reads at a glance
  var statusCol = sh.getRange(2, FIELDS.length + 3, sh.getMaxRows() - 1, 1);
  sh.setConditionalFormatRules([
    ['חדש', '#FFF3CD'], ['נוצר קשר', '#D9E7FB'], ['נקבע ראיון', '#D6E9D5'],
    ['רואיין', '#CFE3F7'], ['התקבל', '#B7E1B0'], ['לא מתאים', '#F2D6D3']
  ].map(function (p) {
    return SpreadsheetApp.newConditionalFormatRule()
      .whenTextEqualTo(p[0]).setBackground(p[1]).setRanges([statusCol]).build();
  }));
}

/* ── run these two once, in this order ───────────────────────────────────── */

/** 1. Creates and formats the sheet. */
function setupNow() {
  var ss = book_();
  var sh = sheet_();

  // drop a leftover empty default tab so the team sees one clean sheet
  ss.getSheets().forEach(function (s) {
    if (s.getName() !== SHEET_NAME && s.getLastRow() === 0 && ss.getSheets().length > 1) {
      ss.deleteSheet(s);
    }
  });

  Logger.log('✅ גיליון מוכן: "' + SHEET_NAME + '" בתוך "' + ss.getName() + '"');
  Logger.log('   שורות כרגע: ' + sh.getLastRow() + ' (1 = כותרת בלבד)');
  Logger.log('   קישור: ' + ss.getUrl());
}

/** 2. Sends a real test application and reports exactly what happened. */
function selfTest() {
  var before = 0;
  try { before = sheet_().getLastRow(); } catch (e) {}

  var res = doPost({ postData: { contents: JSON.stringify({
    name: 'בדיקת מערכת', phone: '0500000000', email: 'test@example.com',
    age: '22', city: 'נתניה', now: 'בדיקה', about: 'שליחת בדיקה מהסקריפט',
    page: 'selfTest'
  })}});

  var out = JSON.parse(res.getContent());
  Logger.log('תוצאה: ' + JSON.stringify(out));

  if (out.ok) {
    Logger.log('✅ מייל נשלח אל: ' + TEAM_EMAIL + '  ובעותק אל: ' + NOTIFY_CC);
  } else {
    Logger.log('❌ נכשל: ' + out.error);
  }

  try {
    var after = sheet_().getLastRow();
    Logger.log((after > before ? '✅' : '❌') + ' שורות בגיליון: ' + before + ' → ' + after);
  } catch (e) {
    Logger.log('❌ כתיבה לגיליון נכשלה: ' + e);
  }

  Logger.log('מיילים שנותרו במכסה היומית: ' + MailApp.getRemainingDailyQuota());
}
